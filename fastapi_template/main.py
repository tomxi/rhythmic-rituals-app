# main.py
from fastapi import FastAPI, HTTPException, Request # Added Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
# Removed: from datetime import datetime
import os
from .notion import APIClient # Updated import

# Data Models (EntryRequest, ProjectRequest remain unchanged)
class EntryRequest(BaseModel):
    content: str
    tags: Optional[List[str]] = []

class ProjectRequest(BaseModel):
    name: str
    description: str
    deadline: Optional[str] = None

# Initialize FastAPI
app = FastAPI(title="Lean Productivity Portal", version="2.0.0")

# Initialize API Client
api_client: Optional[APIClient] = None

@app.on_event("startup")
async def startup_event():
    global api_client
    try:
        api_client = APIClient()
        print("APIClient initialized successfully.")
    except ValueError as e:
        print(f"CRITICAL: Failed to initialize APIClient during startup: {e}")
        # api_client remains None. Subsequent requests relying on it will fail.
        # This allows the app to start and potentially serve static content or health checks.

# HTML_TEMPLATE (remains unchanged, but NOTION_SETUP_TEMPLATE is removed)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lean Productivity Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; color: white; padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; font-weight: 300; }
        .section { background: rgba(255,255,255,0.1); padding: 20px; margin: 20px 0; 
                  border-radius: 12px; backdrop-filter: blur(10px); }
        .input-group { margin-bottom: 15px; }
        input, textarea, select { width: 100%; padding: 12px; border: none; border-radius: 8px;
                                 background: rgba(255,255,255,0.9); color: #333; }
        button { background: #4CAF50; color: white; padding: 12px 24px; border: none;
                border-radius: 8px; cursor: pointer; font-weight: 500; }
        button:hover { background: #45a049; }
        .priority-task { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;
                        margin: 10px 0; font-size: 18px; text-align: center; }
        .entries { max-height: 200px; overflow-y: auto; }
        .entry { background: rgba(255,255,255,0.1); padding: 10px; margin: 5px 0; border-radius: 6px; }
        .projects { display: grid; gap: 15px; }
        .project { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Lean Productivity Portal</h1>
        
        <!-- Priority Task Display -->
        <div class="section">
            <h2>🚀 Priority Focus</h2>
            <div id="priority-task" class="priority-task">Loading your next priority...</div>
        </div>

        <!-- Quick Entry -->
        <div class="section">
            <h2>💭 Rapid Capture</h2>
            <div class="input-group">
                <textarea id="entry-content" placeholder="Dump any thought, idea, achievement, or pain point..." rows="3"></textarea>
            </div>
            <button onclick="createEntry()">Capture</button>
        </div>

        <!-- Recent Entries -->
        <div class="section">
            <h2>📝 Recent Captures</h2>
            <div id="entries" class="entries">Loading entries...</div>
        </div>

        <!-- Project Management -->
        <div class="section">
            <h2>🏆 Projects</h2>
            <div class="input-group">
                <input type="text" id="project-name" placeholder="Project name">
                <textarea id="project-desc" placeholder="Project description" rows="2"></textarea>
                <input type="date" id="project-deadline">
            </div>
            <button onclick="createProject()">Create Project</button>
            <div id="projects" class="projects">Loading projects...</div>
        </div>
    </div>

    <script>
        // API Functions
        async function api(endpoint, method = 'GET', data = null) {
            const options = { method, headers: { 'Content-Type': 'application/json' } };
            if (data) options.body = JSON.stringify(data);
            const response = await fetch(`/api${endpoint}`, options);
            return response.json();
        }

        // Create Entry
        async function createEntry() {
            const content = document.getElementById('entry-content').value.trim();
            if (!content) return;
            
            await api('/entries', 'POST', { content, tags: [] });
            document.getElementById('entry-content').value = '';
            loadEntries();
            loadPriorityTask();
        }

        // Create Project
        async function createProject() {
            const name = document.getElementById('project-name').value.trim();
            const description = document.getElementById('project-desc').value.trim();
            const deadline = document.getElementById('project-deadline').value;
            
            if (!name) return;
            
            await api('/projects', 'POST', { name, description, deadline });
            document.getElementById('project-name').value = '';
            document.getElementById('project-desc').value = '';
            document.getElementById('project-deadline').value = '';
            loadProjects();
        }

        // Load Priority Task
        async function loadPriorityTask() {
            const task = await api('/priority-task');
            const elem = document.getElementById('priority-task');
            if (task.message) {
                elem.textContent = task.message;
            } else {
                elem.innerHTML = `<strong>${task.name}</strong><br><small>${task.description}</small>`;
            }
        }

        // Load Entries
        async function loadEntries() {
            const entries = await api('/entries');
            const container = document.getElementById('entries');
            container.innerHTML = entries.slice(0, 10).map(entry => 
                `<div class="entry">${entry.content} <small>(${new Date(entry.created_at).toLocaleDateString()})</small></div>`
            ).join('');
        }

        // Load Projects
        async function loadProjects() {
            const projects = await api('/projects');
            const container = document.getElementById('projects');
            container.innerHTML = projects.map(project => 
                `<div class="project">
                    <strong>${project.name}</strong><br>
                    <small>${project.description}</small>
                    ${project.deadline ? `<br><small>Due: ${project.deadline}</small>` : ''}
                </div>`
            ).join('');
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            loadPriorityTask();
            loadEntries();
            loadProjects();
        });

        // Enter key shortcuts
        document.getElementById('entry-content').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) createEntry();
        });
    </script>
</body>
</html>
"""

# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request): # Added request: Request
    if api_client is None:
        # Simplified error message for now.
        return HTMLResponse(
            content="<h1>Service Not Configured</h1><p>The application is not properly configured to connect to the backend API. Please contact support or check server logs.</p>",
            status_code=503
        )
    return HTMLResponse(content=HTML_TEMPLATE) # HTML_TEMPLATE is defined below this

# Removed TokenRequest model and /api/setup-notion route

@app.post("/api/entries")
async def create_entry(entry: EntryRequest):
    if api_client is None:
        raise HTTPException(status_code=503, detail="API client not initialized. Service is unavailable.")
    # Assuming APIClient.create_entry might raise HTTPException for API errors
    return api_client.create_entry(entry.content, entry.tags)

@app.get("/api/entries")
async def get_entries():
    if api_client is None:
        raise HTTPException(status_code=503, detail="API client not initialized. Service is unavailable.")
    return api_client.get_entries()

@app.get("/api/priority-task")
async def get_priority_task():
    if api_client is None:
        raise HTTPException(status_code=503, detail="API client not initialized. Service is unavailable.")
    task = api_client.get_priority_task()
    # Original code had: return task if task else {"message": "No tasks available. Create a project to get started!"}
    # APIClient.get_priority_task should ideally return a similar structure or this logic needs to adapt.
    # Assuming APIClient.get_priority_task() now returns the dict with "message" if no task.
    return task

@app.post("/api/projects")
async def create_project(project: ProjectRequest):
    if api_client is None:
        raise HTTPException(status_code=503, detail="API client not initialized. Service is unavailable.")
    return api_client.create_project(project.name, project.description, project.deadline)

@app.get("/api/projects")
async def get_projects():
    if api_client is None:
        raise HTTPException(status_code=503, detail="API client not initialized. Service is unavailable.")
    return api_client.get_projects()

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)