import os
import requests
from typing import List, Dict, Optional, Any
from fastapi import HTTPException

class APIClient:
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL")
        if not self.base_url:
            # In a real scenario, you might want to log this or handle it more gracefully
            # For now, raising ValueError is consistent with the original NotionDB behavior
            raise ValueError("API_BASE_URL environment variable is not set.")

    def _request(self, method: str, endpoint: str, json_data: Optional[Dict] = None) -> Any:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method, url, json=json_data, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
            if response.status_code == 204:  # No Content
                return None
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Log the error details for server-side inspection
            error_detail = f"External API HTTP error: {e.response.status_code} {e.response.reason}"
            if e.response.text:
                error_detail += f" - {e.response.text[:500]}" # Include some of the response text
            print(f"Error during API request to {url}: {error_detail}")
            # Raise HTTPException to be caught by FastAPI and returned to the client
            raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        except requests.exceptions.Timeout:
            print(f"Timeout during API request to {url}")
            raise HTTPException(status_code=504, detail="External API request timed out.")
        except requests.exceptions.RequestException as e:
            # Catch other request-related errors (e.g., connection error)
            print(f"Request exception during API request to {url}: {e}")
            raise HTTPException(status_code=503, detail=f"Service unavailable: Error connecting to external API ({e.__class__.__name__}).")

    def create_entry(self, content: str, tags: Optional[List[str]] = None) -> Dict:
        # Based on notes.js, the API expects 'title' and 'content'.
        # We'll use the provided 'content' for both, or part of it for 'title'.
        # Tags are not supported by the notes.js example.
        payload = {
            "title": content[:100],  # Use the first 100 chars of content as title
            "content": content
        }
        # notes.js returns: { message: "Note added successfully", id: response.id }
        # The original app expects something like: {"id": result["id"], "message": "Entry captured"}
        response_data = self._request("POST", "api/notes", json_data=payload) # Assuming /api/notes from notes.js
        if response_data and "id" in response_data:
            return {"id": response_data["id"], "message": response_data.get("message", "Entry captured")}
        raise HTTPException(status_code=500, detail="Failed to create entry or unexpected response format.")


    def get_entries(self, limit: int = 50) -> List[Dict]:
        # notes.js (target API) returns: [{id, title, content, last_edited_time}]
        # This app's frontend (main.py HTML_TEMPLATE JS) expects: [{id, content, created_at}]
        api_response = self._request("GET", "api/notes") # Assuming /api/notes from notes.js
        entries = []
        if isinstance(api_response, list):
            for item in api_response:
                if not isinstance(item, dict):
                    print(f"Skipping malformed item in get_entries: {item}")
                    continue
                entries.append({
                    "id": item.get("id"),
                    "content": item.get("content", item.get("title", "No content available")),
                    "created_at": item.get("last_edited_time")
                })
        elif api_response is not None: # If it's not a list but also not None, it's an unexpected format
             print(f"Unexpected response format from get_entries: {api_response}")
             raise HTTPException(status_code=500, detail="Unexpected response format from external API for entries.")
        return entries

    def create_project(self, name: str, description: str, deadline: Optional[str] = None) -> Dict:
        # This endpoint /api/projects is an assumption.
        # Assuming server expects {name, description, deadline} and returns {id, message}
        payload = {"name": name, "description": description}
        if deadline:
            payload["deadline"] = deadline
        
        response_data = self._request("POST", "api/projects", json_data=payload)
        if response_data and "id" in response_data:
             return {"id": response_data["id"], "message": response_data.get("message", "Project created")}
        raise HTTPException(status_code=500, detail="Failed to create project or unexpected response format.")


    def get_projects(self) -> List[Dict]:
        # This endpoint /api/projects is an assumption.
        # Assumes server returns list of projects: [{id, name, description, deadline}]
        # This matches what the frontend expects.
        api_response = self._request("GET", "api/projects")
        if isinstance(api_response, list):
            return api_response
        elif api_response is not None:
            print(f"Unexpected response format from get_projects: {api_response}")
            raise HTTPException(status_code=500, detail="Unexpected response format from external API for projects.")
        return []

    def get_priority_task(self) -> Optional[Dict]:
        # This endpoint /api/priority-task is an assumption.
        # Assumes server returns a single task object: {id, name, description}
        # or a message like {"message": "No tasks available..."}
        # This matches what the frontend expects.
        return self._request("GET", "api/priority-task")
