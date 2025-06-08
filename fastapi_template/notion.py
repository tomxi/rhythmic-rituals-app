# notion.py
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

class NotionDB:
    """Minimal Notion integration for productivity portal."""
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv("NOTION_TOKEN")
        if not self.token:
            raise ValueError("Notion token is required")
        
        self.client = Client(auth=self.token)
        self.entries_db = os.getenv("NOTION_ENTRIES_DB")
        self.projects_db = os.getenv("NOTION_PROJECTS_DB")
        self.milestones_db = os.getenv("NOTION_MILESTONES_DB")
        self.tasks_db = os.getenv("NOTION_TASKS_DB")
        
        # Test connection and get workspace info
        self._validate_connection()
    
    def _validate_connection(self):
        """Validate the Notion connection and set up databases if needed."""
        try:
            # Test the connection by getting user info
            user_info = self.client.users.me()
            
            # If databases are not configured, create them
            if not all([self.entries_db, self.projects_db, self.milestones_db, self.tasks_db]):
                self._setup_databases()
        except Exception as e:
            raise ValueError(f"Failed to connect to Notion: {str(e)}")
    
    def _setup_databases(self):
        """Set up required databases if they don't exist."""
        try:
            # Create databases
            db_ids = create_notion_databases(self.token)
            
            # Update instance variables
            self.entries_db = db_ids["entries"]
            self.projects_db = db_ids["projects"]
            self.milestones_db = db_ids["milestones"]
            self.tasks_db = db_ids["tasks"]
            
        except Exception as e:
            raise ValueError(f"Failed to set up databases: {str(e)}")
    
    def create_entry(self, content: str, tags: List[str] = None) -> Dict:
        """Create a new entry in Notion."""
        properties = {
            "Content": {"title": [{"text": {"content": content}}]},
            "Created": {"date": {"start": datetime.now().isoformat()}},
        }
        if tags:
            properties["Tags"] = {"multi_select": [{"name": tag} for tag in tags]}
        
        return self.client.pages.create(
            parent={"database_id": self.entries_db},
            properties=properties
        )
    
    def get_entries(self, limit: int = 50) -> List[Dict]:
        """Get recent entries from Notion."""
        response = self.client.databases.query(
            database_id=self.entries_db,
            sorts=[{"property": "Created", "direction": "descending"}],
            page_size=limit
        )
        
        entries = []
        for page in response["results"]:
            content = ""
            if page["properties"]["Content"]["title"]:
                content = page["properties"]["Content"]["title"][0]["text"]["content"]
            
            created_at = page["properties"]["Created"]["date"]["start"] if page["properties"]["Created"]["date"] else ""
            
            entries.append({
                "id": page["id"],
                "content": content,
                "created_at": created_at
            })
        
        return entries
    
    def create_project(self, name: str, description: str, deadline: str = None) -> Dict:
        """Create a new project in Notion."""
        properties = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Description": {"rich_text": [{"text": {"content": description}}]},
            "Status": {"select": {"name": "Active"}},
            "Created": {"date": {"start": datetime.now().isoformat()}},
        }
        if deadline:
            properties["Deadline"] = {"date": {"start": deadline}}
        
        return self.client.pages.create(
            parent={"database_id": self.projects_db},
            properties=properties
        )
    
    def get_projects(self) -> List[Dict]:
        """Get all projects from Notion."""
        response = self.client.databases.query(
            database_id=self.projects_db,
            sorts=[{"property": "Created", "direction": "descending"}]
        )
        
        projects = []
        for page in response["results"]:
            name = ""
            if page["properties"]["Name"]["title"]:
                name = page["properties"]["Name"]["title"][0]["text"]["content"]
            
            description = ""
            if page["properties"]["Description"]["rich_text"]:
                description = page["properties"]["Description"]["rich_text"][0]["text"]["content"]
            
            deadline = ""
            if page["properties"].get("Deadline", {}).get("date"):
                deadline = page["properties"]["Deadline"]["date"]["start"]
            
            projects.append({
                "id": page["id"],
                "name": name,
                "description": description,
                "deadline": deadline
            })
        
        return projects
    
    def get_priority_task(self) -> Optional[Dict]:
        """Get the highest priority incomplete task."""
        try:
            response = self.client.databases.query(
                database_id=self.tasks_db,
                filter={
                    "property": "Status",
                    "select": {"does_not_equal": "Completed"}
                },
                sorts=[
                    {"property": "Priority", "direction": "descending"},
                    {"property": "Created", "direction": "ascending"}
                ],
                page_size=1
            )
            
            if not response["results"]:
                return None
            
            page = response["results"][0]
            name = ""
            if page["properties"]["Name"]["title"]:
                name = page["properties"]["Name"]["title"][0]["text"]["content"]
            
            description = ""
            if page["properties"]["Description"]["rich_text"]:
                description = page["properties"]["Description"]["rich_text"][0]["text"]["content"]
            
            return {
                "id": page["id"],
                "name": name,
                "description": description
            }
        except:
            return None

def create_notion_databases(token: str, parent_page_id: str = None) -> Dict[str, str]:
    """Create all required Notion databases."""
    client = Client(auth=token)
    parent = {"type": "page_id", "page_id": parent_page_id} if parent_page_id else {"type": "workspace", "workspace": True}
    
    # Entries Database
    entries_db = client.databases.create(
        parent=parent,
        title=[{"text": {"content": "📝 Ideas & Entries"}}],
        properties={
            "Content": {"title": {}},
            "Tags": {"multi_select": {}},
            "Created": {"date": {}}
        }
    )
    
    # Projects Database
    projects_db = client.databases.create(
        parent=parent,
        title=[{"text": {"content": "🏆 Projects"}}],
        properties={
            "Name": {"title": {}},
            "Description": {"rich_text": {}},
            "Status": {"select": {"options": [{"name": "Active"}, {"name": "Completed"}, {"name": "On Hold"}]}},
            "Deadline": {"date": {}},
            "Created": {"date": {}}
        }
    )
    
    # Milestones Database
    milestones_db = client.databases.create(
        parent=parent,
        title=[{"text": {"content": "📍 Milestones"}}],
        properties={
            "Name": {"title": {}},
            "Description": {"rich_text": {}},
            "Project": {"relation": {"database_id": projects_db["id"]}},
            "Status": {"select": {"options": [{"name": "Active"}, {"name": "Completed"}]}},
            "Deadline": {"date": {}},
            "Created": {"date": {}}
        }
    )
    
    # Tasks Database
    tasks_db = client.databases.create(
        parent=parent,
        title=[{"text": {"content": "✅ Tasks"}}],
        properties={
            "Name": {"title": {}},
            "Description": {"rich_text": {}},
            "Milestone": {"relation": {"database_id": milestones_db["id"]}},
            "Priority": {"number": {}},
            "Status": {"select": {"options": [{"name": "Todo"}, {"name": "In Progress"}, {"name": "Completed"}]}},
            "Created": {"date": {}}
        }
    )
    
    return {
        "entries": entries_db["id"],
        "projects": projects_db["id"],
        "milestones": milestones_db["id"],
        "tasks": tasks_db["id"]
    }