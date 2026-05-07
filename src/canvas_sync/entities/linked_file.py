"""
Canvas-Sync by Sang-Buster
February 2017

--------------------------------------------

Implements a class representing files not located on the Canvas server
Initialization of this object thus does not require a info dictionary as is the case for all classes representing true
Canvas entities. Instead, LinkedFile should be initialized with a direct download link.
However, the LinkedFile is derived from the base entity class and the walk, sync and show methods are implemented
and should be used in a similar fashion to other CanvasEntities objects.

An Assignment object is the parent object.

See developer_info.txt file for more information on the class hierarchy of CanvasEntities objects.

"""

# Inbuilt modules
import os

import requests

# Canvas-Sync module imports
from canvas_sync.entities.canvas_entity import CanvasEntity
from canvas_sync.utilities.console import console


class LinkedFile(CanvasEntity):
    def __init__(self, download_url, parent):
        """
        Constructor method, initializes base CanvasEntity class

        download_url    : string | A URL pointing to a file somewhere on the web
        parent          : object | The parent object, an Assignment object
        """

        self.download_url = download_url
        self.valid_url = True

        # Get the potential file name from the URL
        # OBS: We do not correct the name in this class, as we need to use the length of the name to determine
        # if the link is valid.
        file_name = os.path.split(download_url)[-1]

        # File path
        file_path = os.path.join(parent.get_path(), file_name)

        # No file extension or weirdly long filename will not be allowed
        # (this is not strictly necessary as the regex should only match OK URLs)
        if not os.path.splitext(file_name)[-1] or len(file_name) > 60:
            self.valid_url = False

        # Initialize base class
        CanvasEntity.__init__(
            self,
            id_number=-1,
            name=file_name,
            sync_path=file_path,
            parent=parent,
            folder=False,
            identifier="linked_file",
        )

    def __repr__(self):
        """String representation, overwriting base class method"""
        prefix = "  " * max(0, self.indent)
        return f"{prefix}  [magenta]•[/magenta] {self.name}"

    def _print_leaf(self, icon: str, style: str) -> None:
        prefix = "  " * max(0, self.indent)
        console.print(f"{prefix}  [{style}]{icon}[/{style}] {self.name}")

    def url_is_valid(self):
        return self.valid_url

    def download(self):
        """
        Download the file; returns True if fetched, False if already present, -1 on failure.
        """
        if os.path.exists(self.sync_path):
            return False

        try:
            response = requests.get(self.download_url)
        except Exception:
            return -1

        if response.status_code != 200:
            return -1

        with open(self.sync_path, "wb") as out_file:
            out_file.write(response.content)

        return True

    def walk(self, counter):
        """Stop walking, endpoint"""
        console.print(str(self))
        counter[0] += 1

    def sync(self):
        """Attempt to download a linked file from the web and save it locally."""
        result = self.download()
        if result is True:
            self._print_leaf("↓", "bold blue")
        elif result is False:
            self._print_leaf("✓", "dim green")
        else:
            self._print_leaf("✗", "bold red")

    def show(self):
        """Show the folder hierarchy by printing every level"""
        console.print(str(self))
