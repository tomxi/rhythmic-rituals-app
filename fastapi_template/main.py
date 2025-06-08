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
            line-height: 1.6; display: flex; flex-direction: column; align-items: center;
        }
        .container { max-width: 800px; width: 100%; padding: 15px; margin: 20px auto; }
        h1 { text-align: center; margin-bottom: 30px; font-weight: 300; color: #fff; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        h2 { margin-bottom: 20px; font-weight: 500; color: rgba(255,255,255,0.95); }
        .section { background: rgba(255,255,255,0.08); padding: 20px; margin: 20px 0;
                  border-radius: 12px; backdrop-filter: blur(10px); margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .input-group { /* margin-bottom: 15px; */ }
        input, textarea, select { width: 100%; padding: 12px; border: none; border-radius: 8px;
                                 background: rgba(255,255,255,0.9); color: #333; }
        textarea#entry-content {
            resize: vertical; min-height: 80px;
            background: rgba(255,255,255,0.95); color: #222; border: 1px solid rgba(0,0,0,0.1);
            transition: box-shadow 0.3s ease, border-color 0.3s ease;
            font-size: 16px;
        }
        textarea#entry-content:focus {
            border-color: #764ba2;
            box-shadow: 0 0 0 3px rgba(118, 75, 162, 0.3);
            outline: none;
        }
        button { background: #4CAF50; color: white; padding: 12px 24px; border: none;
                border-radius: 8px; cursor: pointer; font-weight: 500; }
        /* Default button:hover is fine for other buttons for now */
        button:hover { background: #45a049; }

        #capture-button {
            padding: 10px 20px; font-size: 16px; display: inline-flex; align-items: center; gap: 8px;
            background-color: #5cb85c; /* A friendly green */
            transition: background-color 0.3s ease, transform 0.2s ease;
            font-weight: 500;
        }
        #capture-button:hover {
            background-color: #4cae4c;
            transform: translateY(-1px);
        }
        #capture-button:active {
            background-color: #449d44;
            transform: translateY(0);
        }
        .priority-task { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;
                        margin: 10px 0; font-size: 18px; text-align: center; }
        .entries {
            margin-top: 20px;
            max-height: 300px; /* Increased max-height */
            overflow-y: auto;
            padding-right: 10px; /* For scrollbar */
        }
        .entries p { /* Styling for "No entries yet" message */
            color: rgba(255,255,255,0.6);
            text-align: center;
            padding: 20px;
        }
        /* .entry { background: rgba(255,255,255,0.1); padding: 10px; margin: 5px 0; border-radius: 6px; } */ /* Old style, replaced by entry-card */
        .entry-card {
            background: rgba(255,255,255,0.85); /* More opaque */
            color: #333; /* Darker text for better contrast */
            padding: 15px; margin-bottom: 10px; border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; /* Added box-shadow transition */
        }
        .entry-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .entry-card-content {
            margin-bottom: 8px;
            font-size: 1em;
            color: #333;
            line-height: 1.5;
        }
        .entry-card-date {
            font-size: 0.75em;
            color: #777;
            margin-top: 8px;
            display: block;
            text-align: right;
        }
        .projects { display: grid; gap: 15px; }
        .project { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; }
        .hidden { display: none; }

        @media (max-width: 600px) {
            h1 { font-size: 2em; }
            .container { padding: 10px; margin-top: 10px; margin-bottom: 10px; }
            #capture-button {
                width: 100%;
                margin-top: 10px;
                padding: 12px; /* Slightly larger padding for tap */
            }
            textarea#entry-content { font-size: 15px; } /* Adjust if needed */
            .section { padding: 15px; }
            h2 { font-size: 1.5em; }
        }
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
        <div class="section" id="rapid-capture-section">
            <h2>💭 Quick Note</h2>
            <div class="input-group">
                <textarea id="entry-content" placeholder="What's on your mind? Tell me everything..." rows="4" aria-label="Note content"></textarea>
            </div>
            <button id="capture-button" onclick="createEntry()">📝 Capture Note</button>
        </div>

        <!-- Recent Entries -->
        <div class="section">
            <h2>📝 My Notes</h2>
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
            if (entries && entries.length > 0) {
                container.innerHTML = entries.slice(0, 10).map(entry => `
                    <div class="entry-card">
                        <p class="entry-card-content">${entry.content ? entry.content.replace(/\\n/g, '<br>') : 'No content'}</p>
                        <small class="entry-card-date">Captured: ${entry.created_at ? new Date(entry.created_at).toLocaleDateString() : 'N/A'}</small>
                    </div>
                `).join('');
            } else {
                container.innerHTML = "<p>No entries yet. Start capturing your thoughts!</p>";
            }
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