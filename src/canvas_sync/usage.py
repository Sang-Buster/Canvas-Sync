"""
Canvas-Sync by Sang-Buster
February 2017

--------------------------------------------

usage.py, module

Implements the help function that displays the help prompt.

"""

# TODO
# Update the help section

# Inbuilt modules
import sys


def help():
    print("""
-------------------------
       Canvas-Sync
     Sang-Buster
     February 2017--
-------------------------

Canvas-Sync helps students automatically synchronize modules, assignments & files located on their
institutions Canvas web server to a mirrored folder on their local computer.

Usage
-----
$ canvas.py [-S] <sync> [-h] <help> [-s] <reset settings> [-i] <show current settings>
    [-p {password}] <specify password>

    -h [--help], optional                : Show this help screen.

    -S [--sync], optional                : Synchronize with Canvas

    -s [--setup], optional               : Enter settings setup screen.

                                           The first time Canvas-Sync is launched settings must be set. Invoking
                                           Canvas-Sync with the -s or --setup flags will allow the user to reset
                                           these settings.

    -i [--info], optional                : Show currently active settings.

    -p {password}, optional              : Specify settings file decryption password (potentially dangerous)

Setup
-----
Canvas-Sync requires at least the following settings to be set:

- A path pointing to a local folder. This folder will store the synced files and folders.
- A Canvas web server URL.
- An authentication token (see https://github.com/Sang-Buster/Canvas-Sync for details)
- A list of courses that should be synchronized.

Canvas-Sync will guide you through these settings during the first time launch. Alternatively,
the settings may be reset using the -s or --setup flag. See below.

ADDITIONAL RESOURCES
--------------------
- Authentication token info and help:
  https://github.com/Sang-Buster/Canvas-Sync

- Canvas by Instructure home page
  https://canvas.instructure.com/

- Canvas LMS API documentation
  https://api.instructure.com
""")
    sys.exit(0)
