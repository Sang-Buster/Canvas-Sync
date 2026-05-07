"""
Canvas-Sync by Mathias Sang-Buster
February 2017

--------------------------------------------

synchronizer.py, CanvasEntity class

The Synchronizer class is the highest level CanvasEntity object in the folder hierarchy.
It inherits from the CanvasEntity base class and extends its functionality to allow downloading
information on courses listed in the Canvas system.
A Course object is initialized for each course found and appended to a list of children under the Synchronizer object.
Synchronization, walking and printing of the folder hierarchy starts by invoking the method on the Synchronizer object
which in turn propagates the signal to all children objects.

The Synchronizer encapsulates a list of children Course objects.

"""

# Future imports

# Third party

# Canvas-Sync modules
from canvas_sync.entities.canvas_entity import CanvasEntity
from canvas_sync.entities.course import Course
from canvas_sync.utilities import helpers
from canvas_sync.utilities.console import console


class Synchronizer(CanvasEntity):
    def __init__(self, settings, api):
        """
        Constructor method, initializes base CanvasEntity class and adds all children
        Course objects to the list of children

        settings : object | A Settings object, has top-level sync path attribute
        api      : object | An InstructureApi object
        """

        if not settings.is_loaded():
            settings.load_settings("")

        # Get the corrected top-level sync path
        sync_path = helpers.get_corrected_path(
            settings.sync_path, parent_path=False, folder=True
        )

        # A dictionary to store lists of CanvasEntity objects
        # added to the hierarchy under a course ID number
        self.entities = {}

        # Initialize base class
        CanvasEntity.__init__(
            self,
            id_number=-1,
            name="",
            sync_path=sync_path,
            api=api,
            settings=settings,
            synchronizer=self,
            identifier="synchronizer",
        )

    def __repr__(self):
        """String representation, overwriting base class method"""
        return f"\n[bold]Syncing to:[/bold] [cyan]{self.sync_path}[/cyan]"

    def get_entities(self, course_id):
        """Getter method for the list of Entities"""
        return self.entities[course_id]

    def add_entity(self, entity, course_id):
        """Add method to append CanvasEntity objects to the list of entities"""
        self.entities[course_id].append(entity)

    def download_courses(self):
        """Returns a dictionary of courses from the Canvas server"""
        return self.api.get_courses()

    def add_courses(self):
        """
        Method that adds all Course objects representing Canvas courses to the
        list of children
        """
        # Download list of dictionaries representing Canvas crouses and
        # add them all to the list of children
        for course_information in self.download_courses():
            # Add an empty list to the entities dictionary that will
            # store entities when added
            self.entities[course_information["id"]] = []

            # Create Course object
            try:
                course = Course(course_information, parent=self, settings=self.settings)
            except KeyError:
                continue
            self.add_child(course)

    def walk(self):
        """Walk by adding all Courses to the list of children"""

        # Print initial walk message
        console.print(self)
        console.print(
            "[bold red][*] Mapping out the Canvas folder hierarchy. Please wait...[/bold red]"
        )
        self.add_courses()

        counter = [2]
        for course in self:
            course.walk(counter)

        return counter

    def sync(self, progress=None, tasks=None):
        """
        1) Adding all Courses objects to the list of children
        2) Synchronize all children objects
        """
        console.print(str(self))

        if len(self.children) == 0:
            self.add_courses()

        for course in self:
            task_id = tasks.get(course.get_id()) if tasks else None
            if progress and task_id is not None:
                progress.update(task_id, description=f"[cyan]{course.get_name()}[/cyan] (syncing)")

            course.sync(progress=progress, task_id=task_id)

            if progress and task_id is not None:
                progress.advance(task_id, 1)
                progress.update(task_id, description=f"[green]{course.get_name()}[/green] (done)")

    def show(self):
        """Show the folder hierarchy by printing every level"""

        helpers.clear_console()
        console.print("\n")
        console.print(str(self))

        for course in self:
            course.show()
