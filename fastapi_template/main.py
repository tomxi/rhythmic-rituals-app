# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from notion import NotionDB

# Data Models
class EntryRequest(BaseModel):
    content: str
    tags: Optional[List[str]] = []

class ProjectRequest(BaseModel):
    name: str
    description: str
    deadline: Optional[str] = None

# Initialize FastAPI
app = FastAPI(title="Lean Productivity Portal", version="2.0.0")

# Initialize Notion DB
notion_db = None

# Check if Notion is configured
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
if NOTION_TOKEN:
    notion_db = NotionDB(NOTION_TOKEN)

# Embedded HTML Template
NOTION_SETUP_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Setup Notion Integration</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; color: white; padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; font-weight: 300; }
        .setup-box { background: rgba(255,255,255,0.1); padding: 20px; margin: 20px 0; 
                  border-radius: 12px; backdrop-filter: blur(10px); }
        .input-group { margin-bottom: 15px; }
        input { width: 100%; padding: 12px; border: none; border-radius: 8px;
               background: rgba(255,255,255,0.9); color: #333; }
        button { background: #4CAF50; color: white; padding: 12px 24px; border: none;
                border-radius: 8px; cursor: pointer; font-weight: 500; }
        button:hover { background: #45a049; }
        .instructions { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 Setup Notion Integration</h1>
        <div class="setup-box">
            <div class="input-group">
                <input type="text" id="notion-token" placeholder="Enter your Notion integration token">
            </div>
            <button onclick="setupNotion()">Connect</button>
            <div class="instructions">
                <h3>How to get your token:</h3>
                <ol>
                    <li>Go to <a href="https://www.notion.so/my-integrations" target="_blank">Notion Integrations</a></li>
                    <li>Create a new integration</li>
                    <li>Copy the token and paste it here</li>
                </ol>
            </div>
        </div>
    </div>
    <script>
        async function setupNotion() {
            const token = document.getElementById('notion-token').value.trim();
            if (!token) return;
            
            const response = await fetch('/api/setup-notion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: token })
            });
            
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Failed to connect. Please check your token.');
            }
        }
    </script>
</body>
</html>
"""

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
async def root():
    if not notion_db:
        return HTMLResponse(content=NOTION_SETUP_TEMPLATE)
    return HTMLResponse(content=HTML_TEMPLATE)

class TokenRequest(BaseModel):
    token: str

@app.post("/api/setup-notion")
async def setup_notion(request: TokenRequest):
    global notion_db
    try:
        # Test the connection by creating a NotionDB instance
        test_db = NotionDB(request.token)
        notion_db = test_db
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/entries")
async def create_entry(entry: EntryRequest):
    result = notion_db.create_entry(entry.content, entry.tags)
    return {"id": result["id"], "message": "Entry captured"}

@app.get("/api/entries")
async def get_entries():
    return notion_db.get_entries()

@app.get("/api/priority-task")
async def get_priority_task():
    task = notion_db.get_priority_task()
    return task if task else {"message": "No tasks available. Create a project to get started!"}

@app.post("/api/projects")
async def create_project(project: ProjectRequest):
    result = notion_db.create_project(project.name, project.description, project.deadline)
    return {"id": result["id"], "message": "Project created"}

@app.get("/api/projects")
async def get_projects():
    return notion_db.get_projects()

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)