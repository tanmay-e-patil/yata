#!/usr/bin/env python3
"""
Setup script for MCP server with personal access tokens.
This script will:
1. Guide you to create a personal access token through the web interface
2. Configure the MCP server to use your personal token
3. Update Claude Desktop configuration
"""

import json
import os
import sys
import webbrowser
from pathlib import Path

def get_claude_config_path():
    """Get Claude Desktop config path based on OS"""
    home = Path.home()
    
    if sys.platform == "darwin":  # macOS
        return home / "Library/Application Support/Claude/claude_desktop_config.json"
    elif sys.platform == "win32":  # Windows
        return home / "AppData/Roaming/Claude/claude_desktop_config.json"
    else:  # Linux
        return home / ".config/claude/claude_desktop_config.json"

def create_mcp_env_file(personal_token):
    """Create .env file for MCP server with personal token"""
    
    mcp_env_path = Path("mcp-yata/.env")
    
    env_content = f"""# Personal Access Token Configuration
PERSONAL_ACCESS_TOKEN={personal_token}
API_BASE_URL=http://localhost:8000/api/v1/personal-todos
SERVER_NAME=mcp-yata-personal
SERVER_VERSION=1.0.0
AUTH_MODE=personal
"""
    
    with open(mcp_env_path, "w") as f:
        f.write(env_content)
    
    return mcp_env_path

def create_claude_config():
    """Create Claude Desktop configuration for personal token auth"""
    
    config = {
        "mcpServers": {
            "yata-todo-personal": {
                "command": "docker",
                "args": [
                    "run",
                    "--rm",
                    "-i",
                    "--network", "host",  # Use host network to access localhost
                    "--env-file", str(Path.cwd() / "mcp-yata" / ".env"),
                    "yata-mcp-yata:latest",
                    "python", "-m", "mcp_yata.simple_server"
                ]
            }
        }
    }
    
    return config

def update_claude_desktop_config(config):
    """Update Claude Desktop configuration file"""
    
    config_path = get_claude_config_path()
    
    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read existing config
    existing_config = {}
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                existing_config = json.load(f)
        except:
            existing_config = {}
    
    # Merge configurations
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    existing_config["mcpServers"].update(config["mcpServers"])
    
    # Write updated config
    with open(config_path, "w") as f:
        json.dump(existing_config, f, indent=2)
    
    return config_path

def main():
    """Main setup function"""
    print("=== MCP Yata Server Setup with Personal Tokens ===\n")
    
    # Check if backend is running
    import requests
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not running at http://localhost:8000")
            print("Please start the backend first:")
            print("  docker-compose -f docker-compose.dev.yml up -d backend postgres redis")
            sys.exit(1)
    except:
        print("❌ Cannot connect to backend at http://localhost:8000")
        print("Please start the backend first:")
        print("  docker-compose -f docker-compose.dev.yml up -d backend postgres redis")
        sys.exit(1)
    
    print("✅ Backend is running")
    
    # Check if user is logged in
    print("\nChecking if you're logged in...")
    try:
        # Try to access a protected endpoint
        response = requests.get("http://localhost:8000/api/v1/todos", timeout=5)
        if response.status_code == 401:
            print("❌ You're not logged in")
            print("\nPlease follow these steps:")
            print(f"1. Open http://localhost:3000 in your browser")
            print("2. Log in with your Google account")
            print("3. Come back here and press Enter to continue...")
            input()
        else:
            print("✅ You're logged in")
    except:
        print("❌ Cannot check login status")
        print("Please ensure the frontend is running at http://localhost:3000")
        sys.exit(1)
    
    # Get personal token
    print("\n" + "="*50)
    print("PERSONAL ACCESS TOKEN SETUP")
    print("="*50)
    print("\n1. Open the API documentation in your browser:")
    print("   http://localhost:8000/docs")
    print("\n2. Click on 'Authorize' and log in with your Google account")
    print("\n3. Scroll down to 'Personal Tokens' section")
    print("\n4. Click 'POST /api/v1/personal-tokens/tokens'")
    print("\n5. Enter a name for your token (e.g., 'Claude Desktop')")
    print("\n6. Copy the 'token' value from the response")
    print("\n" + "="*50)
    
    # Open browser automatically
    webbrowser.open("http://localhost:8000/docs")
    
    # Get token from user
    personal_token = input("\nPaste your personal access token here: ").strip()
    
    if not personal_token:
        print("❌ No token provided. Exiting.")
        sys.exit(1)
    
    print(f"✅ Token received: {personal_token[:20]}...")
    
    # Create MCP .env file
    mcp_env_path = create_mcp_env_file(personal_token)
    print(f"\n✅ MCP environment file created at: {mcp_env_path}")
    
    # Build MCP server Docker image
    print("\nBuilding MCP server Docker image...")
    result = os.system("docker-compose -f docker-compose.dev.yml build mcp-yata > /dev/null 2>&1")
    if result != 0:
        print("❌ Failed to build MCP server image")
        sys.exit(1)
    print("✅ MCP server image built")
    
    # Create Claude Desktop configuration
    config = create_claude_config()
    
    # Update Claude Desktop config
    config_path = update_claude_desktop_config(config)
    
    print(f"\n✅ Claude Desktop configuration updated at:")
    print(f"  {config_path}")
    
    print("\n=== Setup Complete ===")
    print("1. Restart Claude Desktop if it's running")
    print("2. The MCP server will automatically connect when you use Claude")
    print("3. You can now use todo management through Claude!")
    
    print("\nAvailable commands:")
    print("  - Create todos: 'Create a todo to call mom'")
    print("  - List todos: 'Show me all my todos'")
    print("  - Update todos: 'Mark the todo to call mom as complete'")
    print("  - Delete todos: 'Delete the todo about calling mom'")
    
    print("\n🎉 Your personal token will expire in 30 days.")
    print("   You can create a new token following the same steps when it expires.")

if __name__ == "__main__":
    main()