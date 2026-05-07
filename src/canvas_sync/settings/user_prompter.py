"""
Canvas-Sync by Sang-Buster
February 2017

---------------------------------------------

user_prompter.py, module

A collection of functions used to prompt the user for settings.

"""

# TODO
# - Comments
# - Make a Y/N function to reduce code redundancy

# Inbuilt modules
import glob
import os

from rich.prompt import Confirm, IntPrompt, Prompt

# Check for UNIX or Windows platform
try:
    import readline

    unix = True
except ImportError:
    unix = False

# Python 3.10+ uses built-in input()

# Prefer questionary when available for nicer prompts; fall back to plain input
try:
    import questionary

    HAS_QUESTIONARY = True
except Exception:
    HAS_QUESTIONARY = False

# Canvas-Sync module import
from canvas_sync.utilities import helpers
from canvas_sync.utilities.console import console


def _ask_questionary(prompt):
    answer = prompt.ask()
    if answer is None:
        raise KeyboardInterrupt
    return answer


def show_main_screen(settings_file_exists):
    """
    Prompt the user for initial choice of action. Does not allow Synchronization before settings file has been set
    """

    choices = {
        0: "quit",
        1: "sync",
        2: "set_settings",
        3: "show_settings",
        4: "show_help",
    }

    while True:
        helpers.clear_console()
        import canvas_sync

        console.print(f"[bold cyan]Canvas-Sync, {canvas_sync.__version__}[/bold cyan]")
        console.print(
            "Automatically synchronize modules, assignments and files located on a Canvas web server."
        )
        console.print("[bold]What would you like to do?[/bold]")
        console.print("1) Synchronize my Canvas")
        console.print("2) Set new settings")
        console.print("3) Show current settings")
        console.print("4) Show help")
        console.print("0) Quit")

        choice = IntPrompt.ask("Choose number", default=0)
        if choice not in choices:
            continue
        if choice == 1 and not settings_file_exists:
            return "set_settings"
        return choices[choice]


def ask_for_sync_path():
    """
    Prompt the user for a path to a folder that will be used to synchronize the Canvas page into
    The path should point into a directory along with a sub-folder name of a folder not already existing.
    This folder wll be created using the os module.
    """

    # Enable auto-completion of path and cursor movement using the readline and glob modules
    def path_completer(text, state):
        if "~" in text:
            text = text.replace("~", os.path.expanduser("~"))

        paths = glob.glob("%s*" % text)
        paths.append(False)

        return os.path.abspath(paths[state]) + "/"

    if unix:
        readline.set_completer_delims(" \t\n;")
        readline.parse_and_bind("tab: complete")
        readline.set_completer(path_completer)

    found = False
    # Keep asking until a valid path has been entered by the user
    while not found:
        sync_path = Prompt.ask(
            "Enter a relative or absolute path to sync to (~/Desktop/Canvas etc.)"
        )

        # Expand tilde if present in the sync_path
        if "~" in sync_path:
            sync_path = sync_path.replace("~", os.path.expanduser("~"))
        sync_path = os.path.abspath(sync_path)

        if not os.path.exists(os.path.split(sync_path)[0]):
            console.print(
                "[bold red][ERROR][/bold red] Base path "
                f"'{os.path.split(sync_path)[0]}' does not exist."
            )
        else:
            found = True

    if unix:
        # Disable path auto-completer
        readline.parse_and_bind("set disable-completion on")

    return sync_path


def ask_for_domain():
    """
    Prompt the user for a Canvas domain.

    To ensure that the API calls are made on an encrypted SSL connection the initial 'https://' is pre-specified.
    To ensure that the user input is 1) a valid URL and 2) a URL representing a Canvas web server request is used
    to fetch a resources on the Canvas page. If the GET requests fails the URL was not valid. If the server returns
    a 404 unauthenticated error the domain is very likely to be a Canvas server, if anything else is returned the
    URL points to a correct URL that is not a Canvas server.
    """
    found = False

    # Keep asking until a valid domain has been entered by the user
    while not found:
        dom = Prompt.ask(
            "Enter the Canvas domain of your institution (without https://)"
        )
        domain = "https://" + (dom or "")
        found = helpers.validate_domain(domain)

    return domain


def ask_for_token(domain):
    """
    Prompt the user for an authentication token.

    The token must be generated on the Canvas web page when login in under the "Settings" menu.
    To ensure that the entered token is valid, a request GET call is made on a resource that requires authentication
    on the server. If the server responds with the resource the token is valid.
    """
    found = False

    # Keep asking until a valid authentication token has been entered by the user
    while not found:
        token = Prompt.ask("Enter authentication token (see README for details)")
        found = helpers.validate_token(domain, token)

    return token


def ask_for_courses(settings, api):

    courses = api.get_courses()

    def _course_label(course):
        # Some Canvas endpoints omit course_code; fall back gracefully.
        name = course.get("name")
        course_code = course.get("course_code")

        if settings.use_nicknames:
            return name or (
                course_code.split(";")[-1]
                if course_code
                else str(course.get("id", "Unknown course"))
            )

        if course_code:
            return course_code.split(";")[-1]
        return name or str(course.get("id", "Unknown course"))

    labels = [_course_label(course) for course in courses]
    if HAS_QUESTIONARY:
        answer = _ask_questionary(
            questionary.checkbox("Choose which courses to sync:", choices=labels)
        )
        return answer or []
    else:
        choices = [True] * len(labels)

        choice = -1
        while choice != 0:
            settings.print_settings(clear=True)
            console.print(
                "\nPlease choose which courses you would like Canvas-Sync to sync:\n"
            )

            console.print("[bold cyan]Sync this item\tNumber\tCourse Title[/bold cyan]")
            for index, course in enumerate(labels):
                toggle = (
                    "[green]True[/green]"
                    if choices[index]
                    else "[red]False[/red]"
                )
                console.print(f"{toggle}\t\t[{index + 1}]\t{labels[index]}")
            console.print(
                "\n\t\t[0]\t[bold cyan]Confirm selection (at least one course required)[/bold cyan]"
            )
            console.print("\t\t[-1]\t[green]Select all[/green]")
            console.print("\t\t[-2]\t[red]Deselect all[/red]")

            choice = IntPrompt.ask("Choose number", default=0)
            if choice < -2 or choice > len(labels):
                continue

            if choice == 0:
                if sum(choices) == 0:
                    choice = -1
                    continue
                else:
                    break
            elif choice == -1:
                choices = [True] * len(labels)
            elif choice == -2:
                choices = [False] * len(labels)
            else:
                choices[choice - 1] = choices[choice - 1] is not True

        return [x for index, x in enumerate(labels) if choices[index]]


def ask_for_advanced_settings(settings):
    while True:
        settings.print_settings(clear=True)

        console.print(
            "\nAll mandatory settings are set. Do you want to see advanced settings?"
        )
        console.print("[1] Show advanced settings (recommended)")
        console.print("[2] Use default settings")

        choice = IntPrompt.ask("Choose number", default=1)
        if choice == 1:
            return True
        if choice == 2:
            return False


def ask_for_module_settings(module_settings, settings):
    choice = -1
    while choice != 0:
        settings.print_advanced_settings(clear=True)
        console.print("[bold cyan]Module settings[/bold cyan]")
        console.print(
            "In Canvas, Modules may contain files, HTML pages, and links to external websites.\n"
            "Specify if Canvas-Sync should avoid syncing some of these items.\n"
            "If all items are False, modules are skipped."
        )

        console.print("[bold cyan]\nSync this item\tNumber\t\tItem[/bold cyan]")

        list_of_keys = list(module_settings.keys())
        for index, item in enumerate(list_of_keys):
            boolean = module_settings[item]
            console.print(
                f"{'[green]True[/green]' if boolean else '[red]False[/red]'}\t\t[{index + 1}]\t\t{item}"
            )

        console.print("\n\t\t[0]\t\t[bold cyan]Confirm selection[/bold cyan]")

        choice = IntPrompt.ask("Choose number", default=0)
        if choice < 0 or choice > len(module_settings):
            continue

        if choice == 0:
            break
        else:
            module_settings[list_of_keys[choice - 1]] = (
                module_settings[list_of_keys[choice - 1]] is not True
            )

    return module_settings


def ask_for_assignment_sync(settings):
    settings.print_advanced_settings(clear=True)
    return Confirm.ask("Synchronize assignments?", default=True)


def ask_for_download_linked(settings):
    settings.print_advanced_settings(clear=True)
    return Confirm.ask(
        "Enable downloading of linked files referenced in assignment descriptions?",
        default=True,
    )


def ask_for_avoid_duplicates(settings):
    settings.print_advanced_settings(clear=True)
    return Confirm.ask(
        "Avoid downloading duplicate files into 'Various Files'?",
        default=True,
    )
