# setup.py
#!/usr/bin/env python3
"""One-command setup for Lean Productivity Portal."""

import os
import sys
import subprocess
from notion import create_notion_databases

def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "fastapi", "uvicorn", "notion-client", "python-dotenv"])

def setup_notion():
    """Setup Notion integration."""
    print("\n🔗 Setting up Notion integration...")
    print("1. Go to https://www.notion.so/my-integrations")
    print("2. Click 'New integration'")
    print("3. Name it 'Productivity Portal'")
    print("4. Copy the integration token\n")
    
    token = input("Enter your Notion integration token: ").strip()
    if not token:
        print("❌ Token required. Exiting.")
        sys.exit(1)
    
    print("\n📂 Optional: Parent page for databases?")
    parent_page_id = input("Enter parent page ID (or press Enter for workspace root): ").strip()
    parent_page_id = parent_page_id if parent_page_id else None
    
    try:
        print("\n🚀 Creating Notion databases...")
        databases = create_notion_databases(token, parent_page_id)
        
        # Create .env file
        env_content = f"""NOTION_TOKEN={token}
NOTION_ENTRIES_DB={databases['entries']}
NOTION_PROJECTS_DB={databases['projects']}
NOTION_MILESTONES_DB={databases['milestones']}
NOTION_TASKS_DB={databases['tasks']}
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        print("✅ Notion setup complete!")
        print("\n📋 Next steps:")
        print("1. Share each database with your integration in Notion")
        print("2. Run: python main.py")
        print("3. Visit http://localhost:8000")
        print("\n🎉 Your productivity portal is ready!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your token and try again.")
        sys.exit(1)

def main():
    print("🎯 Lean Productivity Portal - Setup")
    print("=" * 40)
    
    # Check if .env already exists
    if os.path.exists(".env"):
        print("✅ Found existing .env file")
        choice = input("Skip Notion setup? (y/n): ").lower()
        if choice != 'y':
            setup_notion()
    else:
        install_dependencies()
        setup_notion()
    
    print("\n🚀 Ready to launch!")
    print("Run: python main.py")

if __name__ == "__main__":
    main()