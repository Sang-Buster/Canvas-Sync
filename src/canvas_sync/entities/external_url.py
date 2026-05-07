"""
Canvas-Sync by Sang-Buster
February 2017

--------------------------------------------

external_url, CanvasEntity Class

The ExternalUrl class stores information on external URLs and calls functions in the
Canvas-Sync.Stats.url_shortcut_maker.py module to create platform specific URL shortcuts. It represents an end point
in the hierarchy and contains no child objects.

A Module or SubHeader object is the parent object.

See developer_info.txt file for more information on the class hierarchy of CanvasEntities objects.

"""

# Inbuilt modules
import os

# Canvas-Sync module imports
from canvas_sync.entities.canvas_entity import CanvasEntity
from canvas_sync.utilities import helpers
from canvas_sync.utilities.console import console
from canvas_sync.utilities.url_shortcut_maker import make_url_shortcut


class ExternalUrl(CanvasEntity):
    def __init__(self, url_info, parent):
        """
        Constructor method, initializes base CanvasEntity class and synchronizes the Item (downloads if not downloaded)

        url_info : dict   | A dictionary of information on the Canvas ExternalUrl object
        parent   : object | The parent object, a Module or SubFolder object
        """
        self.url_info = url_info

        url_id = self.url_info["id"]
        url_name = helpers.get_corrected_name(self.url_info["title"])
        url_path = os.path.join(parent.get_path(), url_name)

        # Initialize base class
        CanvasEntity.__init__(
            self,
            id_number=url_id,
            name=url_name,
            sync_path=url_path,
            parent=parent,
            folder=False,
            identifier="external_url",
        )

    def __repr__(self):
        """String representation, overwriting base class method"""
        return (
            " " * 15
            + "|   "
            + "\t" * self.indent
            + "[magenta]ExternalUrl[/magenta]: %s" % self.name
        )

    def walk(self, counter):
        """Stop walking, endpoint"""
        console.print(str(self))

        counter[0] += 1
        return

    def sync(self):
        """
        Synchronize by creating a local URL shortcut file in in at the sync_pat
        ExternalUrl objects have no children objects and represents an end point of a folder traverse.
        """
        make_url_shortcut(url=self.url_info["external_url"], path=self.sync_path)

        # As opposed to the File and Page classes we never write the "DOWNLOAD" status as we already have
        # all information needed to create the URL shortcut at this point. Here we just print the SYNCED status
        # no matter if the shortcut was recreated or not
        console.print(f"[bold green][SYNCED][/bold green]{str(self)[len('[SYNCED]'):]}")

    def show(self):
        """Show the folder hierarchy by printing every level"""
        console.print(str(self))
