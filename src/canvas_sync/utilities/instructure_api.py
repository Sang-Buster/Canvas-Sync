"""
Canvas-Sync by Sang-Buster
February 2017

--------------------------------------------

instructure_api.py

The InstructureApi object is initialized with a Settings object from the Canvas-Sync.py module.
This class implements the basic API calling functionality to the Canvas by Instructure server.

requests is used to do https communication with the server. The server domain and authentication token is
loaded from the Settings object. The Instructure API uses the JSON format to transmit data objects over the internet
in attribute-value pairs. The json module is used to easily convert this format into a Python dictionary object.

The InstructureApi object implements various methods that will fetch resources from the server such as lists of courses,
modules and files that the user has authentication to access.
"""

import json

import requests


class InstructureApi(object):
    def __init__(self, settings):
        """
        settings : string | A Settings object used to load domain and token attributes
        """
        self.settings = settings

    def _get(self, api_call):
        """
        [PRIVATE] Implements the basic GET call to the API. The get_json method wraps around this method.

        api_call : string | Any call to the Instructure API ("/api/v1/courses" for instance)
        """
        response = requests.get(
            "%s%s" % (self.settings.domain, api_call),
            headers={"Authorization": "Bearer %s" % self.settings.token},
        )
        if response.status_code == 401:
            raise PermissionError(
                "Authentication failed (401). Check that your API token is correct."
            )
        if response.status_code == 404:
            raise FileNotFoundError(
                "Resource not found (404): %s" % api_call
            )
        if response.status_code == 503:
            raise ConnectionError(
                "Canvas server is temporarily unavailable (503). "
                "Check https://status.instructure.com and try again later."
            )
        if not response.ok:
            raise ConnectionError(
                "API request failed with status %d: %s" % (response.status_code, api_call)
            )
        return response

    def get_json(self, api_call):
        """
        A wrapper around the private _get method that will call _get with a specified API call and return the json
        digested dictionary.

        api_call : string | Any call to the Instructure API ("/api/v1/courses" for instance)
        """
        response = self._get(api_call)
        text = response.text.strip()
        if not text:
            raise ValueError(
                "Empty response from API: %s\n"
                "Verify that the domain ('%s') is correct and reachable."
                % (api_call, self.settings.domain)
            )
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Could not parse API response as JSON for %s.\n"
                "Response text: %s" % (api_call, text[:200])
            ) from exc

    def get_json_list(self, api_call):
        data = self.get_json(api_call)
        if not isinstance(data, (list, tuple)):
            data = []
        return data

    def get_courses(self):
        """
        Returns a list of course dictionaries.
        """
        return self.get_json_list("/api/v1/courses?per_page=100")

    def get_modules_in_course(self, course_id):
        """
        Returns a list of dictionaries on the Canvas modules located in a given course.

        course_id : int | A course ID number
        """
        return self.get_json_list("/api/v1/courses/%s/modules?per_page=100" % course_id)

    def get_files_in_folder(self, folder_id):
        """
        Returns a list of dictionaries on the Canvas files located in a given folder

        folder_id : int | A folder ID number
        """
        return self.get_json_list("/api/v1/folders/%s/files?per_page=100" % folder_id)

    def get_folders_in_folder(self, folder_id):
        """
        Returns a list of dictionaries on the Canvas folders located in a given folder

        folder_id : int | A folder ID number
        """
        return self.get_json_list("/api/v1/folders/%s/folders?per_page=100" % folder_id)

    def get_files_in_course(self, course_id):
        """
        Returns a list of dictionaries on the Canvas files located in a given course.

        course_id : int | A course ID number
        """
        return self.get_json_list("/api/v1/courses/%s/files?per_page=100" % course_id)

    def get_folders_in_course(self, course_id):
        """
        Returns a list of dictionaries on the Canvas folders located in a given course.

        course_id : int | A course ID number
        """
        return self.get_json_list("/api/v1/courses/%s/folders?per_page=100" % course_id)

    def get_items_in_module(self, course_id, module_id):
        """
        Returns a dictionary of items located in a given module in a given course

        course_id : int | A course ID number
        module_id : int | A module ID number
        """
        return self.get_json(
            "/api/v1/courses/%s/modules/%s/items?per_page=100" % (course_id, module_id)
        )

    def download_item_information(self, url):
        """
        Returns a dictionary of information on a specified item

        url : string | The API url pointing to information on a specified file in the Canvas system
        """
        url = url.split(self.settings.domain)[-1]
        return self.get_json(url)

    def download_file_payload(self, donwload_url):
        """
        Returns the payload of a specified file in the Canvas system

        donwload_url : string | The API download url pointing to a file in the Canvas system
        """
        url = donwload_url.split(self.settings.domain)[-1]
        return self._get(url).content

    def get_assignments_in_course(self, course_id):
        """
        Returns a list of dictionaries of information on assignment objects under a course ID

        course_id : int | A course ID number
        """
        return self.get_json_list(
            "/api/v1/courses/%s/assignments?per_page=100" % course_id
        )

    def download_page_information(self, course_id, page_id):
        """
        Returns a dictionaries of information on a Page object

        course_id : int | A course ID number
        page_id : int | A page ID number
        """
        return self.get_json("/api/v1/courses/%s/pages/%s" % (course_id, page_id))
