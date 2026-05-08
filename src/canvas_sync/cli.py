"""
Canvas-Sync — Modern Typer-based CLI for synchronizing Canvas content locally.

Implements the command-line interface using Typer and Rich for an intuitive,
user-friendly experience. Supports interactive setup, synchronization, and
settings management.
"""

import os
from typing import Optional

import typer
from rich import box
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.rule import Rule
from rich.table import Table

from canvas_sync.entities.synchronizer import Synchronizer
from canvas_sync.settings import user_prompter
from canvas_sync.settings.settings import Settings
from canvas_sync.utilities import helpers
from canvas_sync.utilities.console import console
from canvas_sync.utilities.instructure_api import InstructureApi

app = typer.Typer(help="Canvas-Sync — synchronize Canvas content locally")


def _print_header() -> None:
    console.print(
        Panel(
            "[bold cyan]Canvas-Sync[/bold cyan]\nSynchronize Canvas content to local folders",
            title=":cloud: Canvas-Sync",
            expand=False,
            box=box.ROUNDED,
        )
    )
    console.print(Rule(style="cyan"))


def _render_settings(settings: Settings) -> None:
    table = Table(title="Current Settings", box=box.SIMPLE_HEAVY)
    table.add_column("Setting", style="bold cyan")
    table.add_column("Value", style="white")
    table.add_row("Sync path", settings.sync_path)
    table.add_row("Canvas domain", settings.domain)
    table.add_row("Authentication token", settings.token)
    table.add_row("Courses to sync", ", ".join(settings.courses_to_sync))
    table.add_row(
        "Module items",
        ", ".join([k for k, enabled in settings.modules_settings.items() if enabled])
        or "None",
    )
    table.add_row(
        "Sync assignments",
        "[green]True[/green]" if settings.sync_assignments else "[red]False[/red]",
    )
    table.add_row(
        "Download linked files",
        "[green]True[/green]" if settings.download_linked else "[red]False[/red]",
    )
    table.add_row(
        "Avoid duplicates",
        "[green]True[/green]" if settings.avoid_duplicates else "[red]False[/red]",
    )
    table.add_row(
        "Use nicknames",
        "[green]True[/green]" if settings.use_nicknames else "[red]False[/red]",
    )
    console.print(table)


@app.command()
def setup() -> None:
    """Interactive setup: configure sync path, domain and token."""
    _print_header()
    settings = Settings()
    try:
        settings.set_settings()
        console.print(":white_check_mark: [green]Settings saved.[/green]")
    except KeyboardInterrupt:
        console.print(":x: [red]Setup interrupted.[/red]")


@app.command()
def info() -> None:
    """Show current settings."""
    _print_header()
    settings = Settings()
    valid = settings.load_settings("")
    _render_settings(settings)
    if not valid:
        settings.print_auth_token_reset_error()


@app.command()
def sync(
    password: Optional[str] = typer.Option(
        None, "-p", "--password", help="Decryption password (not recommended on CLI)"
    ),
    select_courses: bool = typer.Option(
        False,
        "-c",
        "--choose-courses",
        help="Interactively choose which courses to sync for this run",
    ),
) -> None:
    """Start synchronization using saved settings."""
    _print_header()
    settings = Settings()
    valid = settings.load_settings(password or "")
    if not valid:
        console.print(
            ":x: [red]Authentication failed. Use `canvas setup` to reconfigure.[/red]"
        )
        raise typer.Exit(code=1)

    api = InstructureApi(settings)

    # Allow interactive course selection at runtime (do not persist selection)
    if select_courses:
        try:
            chosen = user_prompter.ask_for_courses(settings, api=api)
            settings.courses_to_sync = chosen or []
        except Exception as exc:
            console.print(
                f":x: [red]Unable to select courses interactively:[/red] {exc}"
            )
            raise typer.Exit(code=2)

    synchronizer = Synchronizer(settings=settings, api=api)

    try:
        synchronizer.add_courses()
        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task_ids = {}
            for course in synchronizer:
                if not course.to_be_synced:
                    continue
                task_ids[course.get_id()] = progress.add_task(
                    f"[cyan]{course.get_name()}[/cyan]",
                    total=1,
                )
            synchronizer.sync(progress=progress, tasks=task_ids)
        console.print(Panel(":sparkles: [green]Sync complete![/green]", expand=False))
    except KeyboardInterrupt:
        console.print(":warning: [yellow]Sync interrupted by user.[/yellow]")
    except (PermissionError, FileNotFoundError, ConnectionError, ValueError) as exc:
        console.print(f":x: [red]API error:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command()
def reset(
    confirm: bool = typer.Option(False, "--yes", help="Confirm reset without prompt"),
) -> None:
    """Reset and remove saved settings (if you forgot your password).

    Warning: this irreversibly deletes the encrypted settings and stored password hash.
    """
    _print_header()
    if not confirm:
        if not typer.confirm(
            "This will erase saved settings and cannot be undone. Continue?"
        ):
            console.print(":white_check_mark: [green]Aborted reset.[/green]")
            raise typer.Exit()

    settings = Settings()
    removed = []
    try:
        if os.path.exists(settings.settings_path):
            os.remove(settings.settings_path)
            removed.append(settings.settings_path)
    except Exception:
        pass

    # Remove stored bcrypt password and project .env if present
    try:
        pw_path = os.path.expanduser("~") + "/.Canvas-Sync.pw"
        if os.path.exists(pw_path):
            os.remove(pw_path)
            removed.append(pw_path)
    except Exception:
        pass

    try:
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        env_path = os.path.join(project_root, ".env")
        if os.path.exists(env_path):
            os.remove(env_path)
            removed.append(env_path)
    except Exception:
        pass

    if removed:
        console.print(
            Panel(
                ":wastebasket: [green]Reset complete. Removed:[/green]\n"
                + "\n".join(removed),
                expand=False,
            )
        )
    else:
        console.print(":information: [yellow]No settings found to remove.[/yellow]")


@app.command()
def version() -> None:
    """Show package version."""
    from canvas_sync import _version

    console.print(Rule("Canvas-Sync Version", style="cyan"))
    console.print(f"[bold]{_version.__version__}[/bold]")


def entry() -> None:
    if os.name == "nt":
        helpers.clear_console()
        console.print(
            Panel(
                ":warning: Running on Windows — some features may be limited",
                expand=False,
            )
        )
    try:
        app()
    except Exception as exc:
        console.print(f":x: [red]Error:[/red] {exc}")
        raise


if __name__ == "__main__":
    entry()
