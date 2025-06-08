# 🎯 Lean Productivity Portal

**A minimalist productivity wrapper around Notion - for people who think fast and move faster.**

## The Problem
Academic researchers and knowledge workers need rapid idea capture without friction, plus clear task prioritization without complexity. Most tools are bloated. This isn't.

## The Solution
- **Rapid Capture**: Dump any thought in 2 seconds
- **Priority Focus**: See your most important task instantly  
- **Goal Hierarchy**: Projects → Milestones → Tasks (Managed by backend API)
- **Your Data**: Data is managed by a backend service, accessible via this portal.

## Philosophy
**Elegant Simplicity**: One input field. One priority task. Zero cognitive overhead.

---

## ⚙️ Configuration

This application connects to a backend API to manage data. You need to configure the following environment variable:

*   `API_BASE_URL`: The base URL of the rhythmic-rituals-api server (e.g., `https://your-api-server.com/api`).

Set this environment variable before running the application. For example, you can create a `.env` file in the project root:
```
API_BASE_URL=https://your-api-server.com/api
```
Or set it in your shell:
```bash
export API_BASE_URL="https://your-api-server.com/api"
```

## 🚀 Launch

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Set `API_BASE_URL`**: Ensure the environment variable is set as described above.
3.  **Run the application**:
    ```bash
    python -m uvicorn fastapi_template.main:app --reload
    ```
    Or if you have `main.py` in the root and adjust imports:
    ```bash
    python main.py
    ```
    Visit `http://localhost:8000` (or the port specified by uvicorn).


---

## 🎯 How It Works

**The Interface:**
- **Priority Focus**: Your next most important task, always visible
- **Rapid Capture**: One text field for everything (ideas, achievements, pain points)
- **Project Creation**: Simple form for goals with deadlines

**The Workflow:**
1. **Capture**: Ctrl+Enter to dump any thought
2. **Focus**: Complete the priority task shown at top
3. **Organize**: Create projects when patterns emerge
4. **Repeat**: Let the system surface what matters next

**The Data Flow:**
- Every capture → Sent to the backend API.
- Projects → Managed via the backend API.
- Priority algorithm → Handled by the backend API.
- Your data → Accessible through this portal, managed by the backend service.

---

## 📁 Architecture

This FastAPI application serves as a user interface for a productivity portal. It communicates with an external API (specified by `API_BASE_URL`) which in turn manages the data persistence, potentially using Notion or other services.

The main components are:
```
fastapi_template/main.py  # FastAPI application, serves HTML and API routes
fastapi_template/notion.py # APIClient for communicating with the backend server
requirements.txt          # Python dependencies
README.md                 # This file
```
The application is designed to be lightweight and focused on providing a swift user experience, while delegating data management to a dedicated backend service.

---

## 🧠 Design Philosophy

**Minimalism Over Features**: Every line serves a purpose. No bloat.

**Speed Over Polish**: Get thoughts captured in 2 seconds, not 20.

**Your Data**: Data is managed by the backend API, providing flexibility in storage.

**Zero Lock-in**: Standard web technologies. Fork it. Modify it. Own it.

---

## 🎯 Perfect For

- Academic researchers juggling multiple projects
- Knowledge workers drowning in scattered thoughts
- Anyone who thinks in bursts and needs rapid capture
- Teams who want productivity without vendor lock-in

---

## 💡 Core Insight

Most productivity tools fail because they optimize for features, not flow. This optimizes for flow.

**The magic**: One glance shows your priority. One field captures everything. One system organizes it all.

---

*Built for humans who move fast and think faster.*
