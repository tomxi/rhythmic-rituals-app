import unittest
from unittest.mock import patch, MagicMock
import os
from fastapi import HTTPException
from typing import Optional, List, Dict

# Assuming test_apiclient.py is in the same directory as notion.py (which contains APIClient)
# For the subtask environment, let's be explicit:
# If notion.py is in fastapi_template, and test_apiclient.py is also in fastapi_template:
from .notion import APIClient
import requests # Import at the top level for exception types

class TestAPIClient(unittest.TestCase):

    @patch.dict(os.environ, {"API_BASE_URL": "http://testapi.com"})
    def setUp(self):
        self.client = APIClient()

    @patch('fastapi_template.notion.requests.request') # Patch where requests is used
    def test_get_entries_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "1", "title": "Test Entry 1", "content": "Content 1", "last_edited_time": "2023-01-01T12:00:00Z"},
            {"id": "2", "title": "Test Entry 2", "content": "Content 2", "last_edited_time": "2023-01-02T12:00:00Z"}
        ]
        mock_request.return_value = mock_response

        entries = self.client.get_entries()
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["id"], "1")
        self.assertEqual(entries[0]["content"], "Content 1") # APIClient maps 'content' or 'title'
        self.assertEqual(entries[0]["created_at"], "2023-01-01T12:00:00Z") # APIClient maps 'last_edited_time'
        mock_request.assert_called_once_with("GET", "http://testapi.com/api/notes", json=None, timeout=10)

    @patch('fastapi_template.notion.requests.request')
    def test_create_entry_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 201 # Typically 201 for created
        mock_response.json.return_value = {"id": "new_id", "message": "Note added successfully"}
        mock_request.return_value = mock_response

        entry_data = self.client.create_entry(content="New test entry")
        self.assertEqual(entry_data["id"], "new_id")
        self.assertEqual(entry_data["message"], "Note added successfully")
        # APIClient sends 'title' (first 100 chars of content) and 'content'
        expected_payload = {"title": "New test entry"[:100], "content": "New test entry"}
        mock_request.assert_called_once_with("POST", "http://testapi.com/api/notes", json=expected_payload, timeout=10)

    @patch('fastapi_template.notion.requests.request')
    def test_get_projects_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "p1", "name": "Project Alpha", "description": "Desc Alpha", "deadline": "2024-12-31"}
        ]
        mock_request.return_value = mock_response

        projects = self.client.get_projects()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["name"], "Project Alpha")
        mock_request.assert_called_once_with("GET", "http://testapi.com/api/projects", json=None, timeout=10)

    @patch('fastapi_template.notion.requests.request')
    def test_create_project_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 201 # Typically 201 for created
        mock_response.json.return_value = {"id": "new_project_id", "message": "Project created"}
        mock_request.return_value = mock_response

        project_data = self.client.create_project(name="New Project", description="A cool new project", deadline="2025-01-01")
        self.assertEqual(project_data["id"], "new_project_id")
        expected_payload = {"name": "New Project", "description": "A cool new project", "deadline": "2025-01-01"}
        mock_request.assert_called_once_with("POST", "http://testapi.com/api/projects", json=expected_payload, timeout=10)

    @patch('fastapi_template.notion.requests.request')
    def test_get_priority_task_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "task1", "name": "Important Task", "description": "Do this first"}
        mock_request.return_value = mock_response

        task = self.client.get_priority_task()
        self.assertIsNotNone(task)
        self.assertEqual(task["name"], "Important Task")
        mock_request.assert_called_once_with("GET", "http://testapi.com/api/priority-task", json=None, timeout=10)

    @patch('fastapi_template.notion.requests.request')
    def test_get_priority_task_no_tasks_message(self, mock_request): # Renamed for clarity
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "No tasks available"} # As handled by APIClient
        mock_request.return_value = mock_response

        task = self.client.get_priority_task()
        self.assertIsNotNone(task)
        self.assertIn("message", task)
        mock_request.assert_called_once_with("GET", "http://testapi.com/api/priority-task", json=None, timeout=10)

    @patch('fastapi_template.notion.requests.request')
    def test_api_http_error_404(self, mock_request): # Be specific in test names
        mock_http_error_response = MagicMock(spec=requests.Response)
        mock_http_error_response.status_code = 404
        mock_http_error_response.reason = "Not Found"
        mock_http_error_response.text = "Detailed error message from API"

        # The side_effect should be an instance of HTTPError, configured with the mock response
        http_error_instance = requests.exceptions.HTTPError(response=mock_http_error_response)
        mock_http_error_response.raise_for_status.side_effect = http_error_instance # Mock raise_for_status behavior
        mock_request.return_value = mock_http_error_response


        with self.assertRaises(HTTPException) as cm:
            self.client.get_entries() # Any method that uses _request would work
        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn("External API HTTP error: 404 Not Found", cm.exception.detail)
        self.assertIn("Detailed error message from API", cm.exception.detail)


    @patch('fastapi_template.notion.requests.request')
    def test_api_timeout_error(self, mock_request):
        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")

        with self.assertRaises(HTTPException) as cm:
            self.client.get_entries()
        self.assertEqual(cm.exception.status_code, 504) # As defined in APIClient
        self.assertEqual(cm.exception.detail, "External API request timed out.")

    @patch('fastapi_template.notion.requests.request')
    def test_api_connection_error(self, mock_request):
        mock_request.side_effect = requests.exceptions.ConnectionError("Failed to connect")

        with self.assertRaises(HTTPException) as cm:
            self.client.get_entries()
        self.assertEqual(cm.exception.status_code, 503) # As defined in APIClient
        self.assertIn("Service unavailable: Error connecting to external API (ConnectionError)", cm.exception.detail)

    def test_init_no_api_base_url(self):
        # Temporarily remove the API_BASE_URL for this test case
        original_api_base_url = os.environ.pop("API_BASE_URL", None)
        try:
            with self.assertRaises(ValueError) as cm:
                APIClient()
            self.assertEqual(str(cm.exception), "API_BASE_URL environment variable is not set.")
        finally:
            # Restore API_BASE_URL if it was originally set
            if original_api_base_url is not None:
                os.environ["API_BASE_URL"] = original_api_base_url


if __name__ == '__main__':
    unittest.main()
