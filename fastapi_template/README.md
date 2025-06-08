# 🎯 Lean Productivity Portal

**A minimalist productivity wrapper around Notion - for people who think fast and move faster.**

## The Problem
Academic researchers and knowledge workers need rapid idea capture without friction, plus clear task prioritization without complexity. Most tools are bloated. This isn't.

## The Solution
- **Rapid Capture**: Dump any thought in 2 seconds
- **Priority Focus**: See your most important task instantly  
- **Goal Hierarchy**: Projects → Milestones → Tasks
- **Your Data**: Everything lives in your Notion workspace

## Philosophy
**Elegant Simplicity**: One input field. One priority task. Zero cognitive overhead.

---

## 🚀 Setup (2 minutes)

### 1. Run Setup
```bash
python setup.py
```

This will:
- Install dependencies
- Guide you through Notion integration
- Create required databases
- Generate your `.env` file

### 2. Share Databases
In Notion, share each created database with your integration:
- 📝 Ideas & Entries  
- 🏆 Projects
- 📍 Milestones
- ✅ Tasks

### 3. Launch
```bash
python main.py
```
Visit `http://localhost:8000`

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
- Every capture → Notion "Ideas & Entries" database
- Projects → Structured in Notion with milestones and tasks
- Priority algorithm → Surfaces most important incomplete task
- Your workspace → All data accessible in Notion forever

---

## 📁 Architecture (3 files)


```
main.py      # Single-file FastAPI app with embedded HTML/CSS/JS
notion.py    # Notion database integration
setup.py     # One-command setup script
README.md    # This file
```

**Total Lines**: ~350 lines across 4 files

---

## 🧠 Design Philosophy

**Minimalism Over Features**: Every line serves a purpose. No bloat.

**Speed Over Polish**: Get thoughts captured in 2 seconds, not 20.

**Your Data**: Notion as backend means you own everything forever.

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
