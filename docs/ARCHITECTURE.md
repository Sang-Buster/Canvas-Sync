# Canvas-Sync Architecture

## Overview

Canvas-Sync is designed from an end-user application perspective and is not optimized for general interaction with the Canvas API. For detailed Canvas API documentation, see the [Canvas API Reference](https://canvas.instructure.com/doc/api/).

Canvas-Sync implements a hierarchical class structure that closely mirrors the organization of the Canvas LMS server. The system consists of various container 'entities' such as modules, assignments, and folders that may contain items like files, HTML pages, and URLs.

## Entity Hierarchy

### Container Objects

The most important container objects are:

- **Courses** — Represented by the `Course` object, this is the highest-level representation. It stores all information on a course including modules, files, assignments, grades, and messages.

- **Modules** — Represented by the `Module` object, these are folder-like structures that organize files, HTML pages, and links to external sites for a given course. For example, a Math 101 course might have a "Calculus" module containing various instructor-uploaded files and pages.

- **Subheaders** — Represented by the `SubHeader` class, these are sub-folder-like structures that separate items within modules into logical sub-categories.

- **Assignments** — Represented by the `AssignmentsFolder` class, this is a collection of individual assignments under a course. Each `Assignment` contains a description (downloaded as HTML) and links to files referenced in the description.

- **Files Section** — Represented by the `Folder` object, this is a hierarchical folder structure corresponding to the Canvas Files section, which may recursively contain nested directories.

### Object Hierarchy Diagram

```
                            Synchronizer
                                 |
                                 |
                               Course
                                 |
                  --------------------------------
                  |                |              |
            AssignmentsFolder    Folder      Module
                  |                |          |    |
                  |                |          |    |
              Assignment      (nested)    SubHeader
                  |            Folders         |
                  |                |           |
            ------+------          |      --------+--------
            |            |         |      |       |       |
        LinkedFile    (none)       |    File    Page  ExternalUrl
```

### Inheritance Model

Most objects inherit from `CanvasEntity`, a base class that provides:

- ID numbers
- Object names and paths
- Synchronization paths (absolute paths to local directories)
- Parent-child relationships
- Common sync/download methods

The `SubHeader` class inherits from `Module` rather than directly from `CanvasEntity`, reusing much of its functionality.

## Synchronization Flow

1. **Synchronizer** initializes with a `Settings` object and a list of `Course` objects.
2. **Synchronizer.sync()** calls `sync()` on each course (using parallel `ThreadPoolExecutor` for concurrent syncing).
3. **Course.sync()** propagates the sync call to all child entities (modules, assignments, files folders).
4. **Module/SubHeader.sync()** adds child items (Files, Pages, ExternalURLs) and syncs each.
5. **Assignment.sync()** downloads the assignment description as HTML and syncs linked files.
6. **Folder.sync()** recursively syncs the file hierarchy from Canvas.
7. Leaf nodes (`File`, `LinkedFile`, `Page`, `ExternalUrl`) download their content to disk.

## Key Classes

### Entity Base Class (`CanvasEntity`)

Provides common functionality for all entity types:

```python
class CanvasEntity:
    def __init__(self, id_number, name, sync_path, parent, folder=True, identifier=""):
        self.id = id_number
        self.name = name
        self.sync_path = sync_path
        self.parent = parent
        self.children = []
        # ...
    
    def sync(self):
        """Override in subclasses to implement sync logic"""
        raise NotImplementedError
```

### Course

The top-level entity representing a Canvas course. Responsible for:

- Fetching modules, assignments, and files from Canvas API
- Creating child entity objects (Module, AssignmentsFolder, Folder)
- Orchestrating the sync process for the course

### Module

A container for course content organized by topic. Handles:

- Fetching module items (files, pages, URLs)
- Creating child entities for each item type
- Supporting SubHeader objects for nested organization

### SubHeader

A specialized Module representing a folder within a module. Inherits from Module but:

- Accepts a pre-populated list of items rather than fetching from the API
- Prevents redundant API calls for nested structures

### Assignment

Represents a single Canvas assignment. Handles:

- Downloading assignment descriptions as HTML
- Parsing and downloading files linked in the description
- Creating `LinkedFile` objects for external URLs

### Folder

Represents the Canvas Files section or nested file directories. Supports:

- Recursive folder hierarchies
- Automatic duplicate avoidance (configured via settings)

### LinkedFile

Handles downloading files from external URLs referenced in assignment descriptions:

- Validates URL format and filename
- Attempts download with error handling
- Stores in assignment folder with original filename

## Settings Management

The `Settings` object manages:

- **Sync Path**: Local directory where files are downloaded
- **Canvas Domain**: Institution's Canvas server URL
- **Authentication Token**: API token for Canvas access
- **Module Settings**: Toggle which content types to sync (Files, HTML pages, External URLs)
- **Assignment Settings**: Toggle assignment syncing and linked file downloading
- **Duplicate Avoidance**: Prevent duplicate downloads in Files section
- **Advanced Options**: Use nicknames for courses, etc.

Settings are encrypted with AES-256 and stored in:
- `~/.Canvas-Sync.settings` (encrypted binary)
- `~/.Canvas-Sync.pw` (bcrypt hashed password)
- `.env` (base64-encoded encrypted blob, for convenience)

## Parallel Synchronization

Canvas-Sync uses `concurrent.futures.ThreadPoolExecutor` with up to 4 worker threads to:

- Download multiple courses concurrently
- Improve overall sync performance on systems with sufficient I/O bandwidth
- Fall back to sequential sync if concurrent execution fails

## Error Handling

- **Invalid credentials**: Prompt user to reset settings via `canvas reset`
- **Network errors**: Log and skip affected items, continue syncing
- **File access errors**: Handle permission and path errors gracefully
- **API errors**: Retry logic with exponential backoff (future enhancement)

## Development Notes

- **API Focus**: Interaction with Canvas API is isolated in `utilities/instructure_api.py`
- **No Modifications**: Canvas-Sync is read-only; it never modifies or deletes Canvas content
- **Configuration**: All sync behavior is configurable via the `Settings` object
- **Extensibility**: New entity types or download sources can be added by extending `CanvasEntity`

## Future Enhancements

- Incremental sync (detect only new/modified content)
- Webhook-based real-time sync
- Support for nested assignment folders
- Advanced filtering and selective sync
- Sync history and change logs
