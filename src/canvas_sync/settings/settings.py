"""
Canvas-Sync by Mathias Sang-Buster
February 2017

--------------------------------------------

settings.py, Class

The Settings object implements the functionality of setting the initial-launch
settings and later loading these settings
These settings include:

1) A path to with synchronization will occur. The path must be pointing to a
   valid folder and contain a sub folder name.
   The sub folder is generated and stores all synchronized courses_to_sync.
2) The domain of the Canvas web server.
3) An authentication token used to authenticate with the Canvas API. The token
   is generated on the Canvas web server
   after authentication under "Settings".

The Settings object will prompt the user for these settings through the
set_settings method and write them to a hidden file in the users home directory.
The file is encrypted using a user-specified password. This password must
be specified whenever Canvas-Sync is launched. Encryption is implemented via
the PyCrypto AES-256 encryption module. The password is stored locally in a
hashed format using the bcrypt module. At runtime, the hashed password is used
to validate the user input password.
"""

# TODO
# - Clean things
# - Implement ANKI.fomrat method instead of accessing the ANKI attributes
#   directly
# - Make it possible reuse settings, so that you do not have to
#   re-specify all settings to change a single one

# Inbuilt modules
import os
import sys

from rich import box
from rich.panel import Panel
from rich.table import Table

from canvas_sync.settings import user_prompter

# Third party modules
# Canvas-Sync modules
from canvas_sync.settings.cryptography import decrypt, encrypt
from canvas_sync.utilities import helpers
from canvas_sync.utilities.console import console
from canvas_sync.utilities.instructure_api import InstructureApi


class Settings(object):
    def __init__(self):
        self.sync_path = "Not set"
        self.domain = "Not set"
        self.token = "Not set"
        self.courses_to_sync = ["Not set"]
        self.modules_settings = {
            "Files": True,
            "HTML pages": True,
            "External URLs": True,
        }
        self.sync_assignments = True
        self.download_linked = True
        self.avoid_duplicates = True
        self.use_nicknames = False

        # Get the path pointing to the settings file.
        self.settings_path = os.path.abspath(
            os.path.join(os.path.expanduser("~"), ".Canvas-Sync.settings")
        )

        # Initialize user prompt class, used to get information from the user
        # via the terminal
        self.api = InstructureApi(self)

    def settings_file_exists(self):
        """
        Returns a boolean representing if the settings file
        has already been created on this machine
        """
        return os.path.exists(self.settings_path)

    def is_loaded(self):
        return (
            self.sync_path != "Not set"
            and self.domain != "Not set"
            and self.token != "Not set"
            and self.courses_to_sync[0] != "Not set"
        )

    def load_settings(self, password):
        """
        Loads the current settings from the settings file and sets the
        attributes of the Settings object
        """
        if self.is_loaded():
            return helpers.validate_token(self.domain, self.token)

        if not self.settings_file_exists():
            self.set_settings()
            return True

        with open(self.settings_path, "rb") as settings_f:
            encrypted_message = settings_f.read()
        messages = decrypt(encrypted_message, password)
        if not messages:
            # Password file did not exist, set new settings
            console.print(
                Panel(
                    "[bold red]The hashed password file no longer exists. "
                    "You must re-enter settings.[/bold red]",
                    title="Error",
                    border_style="red",
                    expand=False,
                )
            )
            input("\nPres enter to continue.")
            self.set_settings()
            return self.load_settings("")
        else:
            messages = messages.decode("utf-8").split("\n")

        # Set sync path, domain and auth token
        self.sync_path, self.domain, self.token = messages[:3]

        def read_setting(settings_string):
            return settings_string.split("$")[-1] == "True"

        # Extract synchronization settings
        for message in messages:
            if message[:12] == "SYNC COURSE$":
                if self.courses_to_sync[0] == "Not set":
                    self.courses_to_sync.pop(0)
                self.courses_to_sync.append(message.split("$")[-1])

            setting = read_setting(message)
            if message[:6] == "Files$":
                self.modules_settings["Files"] = setting
            if message[:11] == "HTML pages$":
                self.modules_settings["HTML pages"] = setting
            if message[:14] == "External URLs$":
                self.modules_settings["External URLs"] = setting
            if message[:12] == "Assignments$":
                self.sync_assignments = setting
            if message[:13] == "Linked files$":
                self.download_linked = setting
            if message[:17] == "Avoid duplicates$":
                self.avoid_duplicates = setting
            if message[:14] == "Use nicknames$":
                self.use_nicknames = setting

        if not helpers.validate_token(self.domain, self.token):
            return False
        else:
            return True

    def set_settings(self):
        try:
            self._set_settings()
        except KeyboardInterrupt:
            console.print(
                "[bold red][*] Setup interrupted, nothing was saved.[/bold red]"
            )
            sys.exit()

        self.write_settings()

    def _set_settings(self):
        """
        Prompt the user for settings and write the information to a hidden file in the users home directory.
        """

        # Clear the console and print guidance
        self.print_settings(first_time_setup=True, clear=True)

        # Prompt user for sync path
        self.sync_path = user_prompter.ask_for_sync_path()
        self.print_settings(first_time_setup=True, clear=True)

        # Prompt user for domain
        self.domain = user_prompter.ask_for_domain()
        self.print_settings(first_time_setup=True, clear=True)

        # Prompt user for auth token
        self.token = user_prompter.ask_for_token(domain=self.domain)
        self.print_settings(first_time_setup=True, clear=True)

        # Prompt user for course sync selection
        self.courses_to_sync = user_prompter.ask_for_courses(self, api=self.api)
        self.print_settings(first_time_setup=True, clear=True)

        # Ask user for advanced settings
        show_advanced = user_prompter.ask_for_advanced_settings(self)

        if show_advanced:
            self.modules_settings = user_prompter.ask_for_module_settings(
                self.modules_settings, self
            )
            self.sync_assignments = user_prompter.ask_for_assignment_sync(self)
            if not self.sync_assignments:
                self.download_linked = False
            else:
                self.download_linked = user_prompter.ask_for_download_linked(self)
            self.avoid_duplicates = user_prompter.ask_for_avoid_duplicates(self)

    def write_settings(self):
        self.print_settings(first_time_setup=False, clear=True)
        self.print_advanced_settings(clear=False)
        console.print(
            Panel(
                "[bold cyan]These settings will be saved[/bold cyan]",
                expand=False,
                border_style="cyan",
            )
        )

        # Write password encrypted settings to hidden file in home directory
        with open(self.settings_path, "wb") as out_file:
            settings = self.sync_path + "\n" + self.domain + "\n" + self.token + "\n"

            for course in self.courses_to_sync:
                settings += "SYNC COURSE$" + course + "\n"

            settings += "Files$" + str(self.modules_settings["Files"]) + "\n"
            settings += "HTML pages$" + str(self.modules_settings["HTML pages"]) + "\n"
            settings += (
                "External URLs$" + str(self.modules_settings["External URLs"]) + "\n"
            )
            settings += "Assignments$" + str(self.sync_assignments) + "\n"
            settings += "Linked files$" + str(self.download_linked) + "\n"
            settings += "Avoid duplicates$" + str(self.avoid_duplicates) + "\n"

            out_file.write(encrypt(settings))

    def print_advanced_settings(self, clear=True):
        """
        Print the advanced settings currently in memory.
        Clear the console first if specified by the 'clear' parameter
        """
        if clear:
            helpers.clear_console()

        table = Table(title="Advanced Settings", box=box.SIMPLE_HEAVY)
        table.add_column("Setting", style="bold cyan")
        table.add_column("Value")
        enabled_module_items = [
            item for item, enabled in self.modules_settings.items() if enabled
        ]
        table.add_row(
            "Sync module items",
            ", ".join(enabled_module_items)
            if enabled_module_items
            else "[red]None[/red]",
        )
        table.add_row(
            "Sync assignments",
            "[green]True[/green]" if self.sync_assignments else "[red]False[/red]",
        )
        table.add_row(
            "Download linked files",
            "[green]True[/green]" if self.download_linked else "[red]False[/red]",
        )
        table.add_row(
            "Avoid item duplicates",
            "[green]True[/green]" if self.avoid_duplicates else "[red]False[/red]",
        )
        table.add_row(
            "Use nicknames",
            "[green]True[/green]" if self.use_nicknames else "[red]False[/red]",
        )
        console.print(table)

    def print_settings(self, first_time_setup=True, clear=True):
        """
        Print the settings currently in memory.
        Clear the console first if specified by the 'clear' parameter
        """
        if clear:
            helpers.clear_console()

        if first_time_setup:
            console.print(
                Panel(
                    "This is a first time setup.\nYou must specify at least the "
                    "following settings to run Canvas-Sync.",
                    title="Setup",
                    border_style="cyan",
                    expand=False,
                )
            )
        else:
            console.print(
                Panel(
                    "[bold cyan]Canvas-Sync - Current settings[/bold cyan]",
                    expand=False,
                    border_style="cyan",
                )
            )

        table = Table(title="Standard Settings", box=box.SIMPLE_HEAVY)
        table.add_column("Setting", style="bold cyan")
        table.add_column("Value")
        table.add_row("Sync path", self.sync_path)
        table.add_row("Canvas domain", self.domain)
        table.add_row("Authentication token", self.token)
        table.add_row("Courses to be synced", ", ".join(self.courses_to_sync))
        console.print(table)

    def show(self, quit=True):
        """
        Show the current settings
        If quit=True, sys.exit after user confirmation
        """
        valid_token = self.load_settings("")

        self.print_settings(first_time_setup=False, clear=True)
        self.print_advanced_settings(clear=False)

        if not valid_token:
            self.print_auth_token_reset_error()

        if quit:
            sys.exit()
        else:
            input("\nHit enter to continue.")

    def print_auth_token_reset_error(self):
        """
        Prints error message for when the auth token stored in the
        settings is no longer valid
        """
        console.print(
            Panel(
                "The authentication token has been reset.\n"
                "Generate a new token from Canvas and run `canvas setup`.",
                title="Authentication Error",
                border_style="red",
                expand=False,
            )
        )

    def show_main_screen(self, settings_file_exists):
        """
        Linker method to the show_main_screen function of the
        user_prompter module
        """
        return user_prompter.show_main_screen(settings_file_exists)
