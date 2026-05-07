"""
Canvas-Sync by Sang-Buster
February 2017

--------------------------------------------

file, CanvasEntity Class

The File class stores information on files hosted on the Canvas server. It represents an end point in the hierarchy and
contains no child objects. When the sync method is invoked the file will be downloaded or skipped depending on if it is
already present in at the sync path.

A Module, SubHeader, Folder or Assignment object is the parent object.

See developer_info.txt file for more information on the class hierarchy of CanvasEntities objects.

"""

# Inbuilt modules
import os

from canvas_sync.entities.canvas_entity import CanvasEntity
from canvas_sync.utilities import helpers
from canvas_sync.utilities.console import console


class File(CanvasEntity):
    def __init__(self, file_info, parent, add_to_list_of_entities=True):
        """
        Constructor method, initializes base CanvasEntity class

        assignment_info : dict   | A dictionary of information on the Canvas file object
        parent          : object | The parent object, a Module, SubHeader, Folder or Assignment object
        """

        self.file_info = file_info

        self.locked = self.file_info["locked_for_user"]

        file_id = self.file_info["id"]
        file_name = helpers.get_corrected_name(self.file_info["display_name"])
        file_path = os.path.join(parent.get_path(), file_name)

        # Initialize base class
        CanvasEntity.__init__(
            self,
            id_number=file_id,
            name=file_name,
            sync_path=file_path,
            parent=parent,
            folder=False,
            identifier="file",
            add_to_list_of_entities=add_to_list_of_entities,
        )

    def __repr__(self):
        """String representation, overwriting base class method"""
        prefix = "  " * max(0, self.indent)
        return f"{prefix}  [yellow]•[/yellow] {self.name}"

    def _print_leaf(self, icon: str, style: str) -> None:
        prefix = "  " * max(0, self.indent)
        console.print(f"{prefix}  [{style}]{icon}[/{style}] {self.name}")

    def download(self):
        """Download the file; returns True if fetched, False if already present."""
        if os.path.exists(self.sync_path):
            return False

        file_data = self.api.download_file_payload(self.file_info["url"])

        try:
            with open(self.sync_path, "wb") as out_file:
                out_file.write(file_data)
        except KeyboardInterrupt as e:
            if os.path.exists(self.sync_path):
                os.remove(self.sync_path)
            raise e

        return True

    def walk(self, counter):
        """Stop walking, endpoint"""
        console.print(str(self))
        counter[0] += 1

    def sync(self):
        """
        Synchronize the file by downloading it from the Canvas server and saving it to the
        sync path. If the file has already been downloaded, skip downloading.
        """
        if not self.locked:
            was_downloaded = self.download()
            if was_downloaded:
                self._print_leaf("↓", "bold blue")
            else:
                self._print_leaf("✓", "dim green")
        else:
            self._print_leaf("✗", "bold red")

    def show(self):
        """Show the folder hierarchy by printing every level"""
        console.print(str(self))
