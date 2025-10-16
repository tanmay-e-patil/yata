#!/usr/bin/env python3
"""
Automated setup script for MCP server with Claude Desktop.
This script will:
1. Create an OAuth client if needed
2. Generate Claude Desktop configuration
3. Update the Claude Desktop config file
"""

import json
import os
import sys
import requests
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

def create_or_get_oauth_client(base_url="http://localhost:8000"):
    """Create OAuth client or get existing one"""
    
    # Try to get existing client from .env
    env_path = Path(".env")
    client_id = None
    client_secret = None
    
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("MCP_OAUTH_CLIENT_ID="):
                    client_id = line.split("=", 1)[1].strip()
                elif line.startswith("MCP_OAUTH_CLIENT_SECRET="):
                    client_secret = line.split("=", 1)[1].strip()
    
    # Test if existing credentials work
    if client_id and client_secret:
        print("Testing existing OAuth credentials...")
        if test_oauth_client(client_id, client_secret, base_url):
            return client_id, client_secret
        print("Existing credentials are invalid, creating new client...")
    
    # Create new client
    print("Creating new OAuth client...")
    client_name = "MCP Yata Server - Claude Desktop"
    scopes = "todos:read todos:write"
    
    url = f"{base_url}/api/v1/oauth/clients"
    
    try:
        response = requests.post(
            url,
            params={
                "client_name": client_name,
                "scopes": scopes
            }
        )
        
        if response.status_code == 200:
            client_data = response.json()
            
            # Update .env file
            update_env_file(client_data['client_id'], client_data['client_secret'])
            
            return client_data['client_id'], client_data['client_secret']
        else:
            print(f"Failed to create OAuth client: {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"Error creating OAuth client: {e}")
        return None, None

def test_oauth_client(client_id, client_secret, base_url="http://localhost:8000"):
    """Test OAuth client credentials"""
    
    url = f"{base_url}/api/v1/oauth/token"
    
    try:
        response = requests.post(
            url,
            auth=(client_id, client_secret),
            json={
                "grant_type": "client_credentials",
                "scope": "todos:read todos:write"
            }
        )
        
        return response.status_code == 200
    except:
        return False

def update_env_file(client_id, client_secret):
    """Update .env file with new credentials"""
    env_path = Path(".env")
    lines = []
    
    # Read existing file
    if env_path.exists():
        with open(env_path, "r") as f:
            lines = f.readlines()
    
    # Update or add credentials
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("MCP_OAUTH_CLIENT_ID="):
            lines[i] = f"MCP_OAUTH_CLIENT_ID={client_id}\n"
            updated = True
        elif line.startswith("MCP_OAUTH_CLIENT_SECRET="):
            lines[i] = f"MCP_OAUTH_CLIENT_SECRET={client_secret}\n"
            updated = True
    
    # Add if not found
    if not updated:
        lines.append(f"\n# MCP Server OAuth Configuration\n")
        lines.append(f"MCP_OAUTH_CLIENT_ID={client_id}\n")
        lines.append(f"MCP_OAUTH_CLIENT_SECRET={client_secret}\n")
    
    # Write back
    with open(env_path, "w") as f:
        f.writelines(lines)

def create_claude_config(client_id, client_secret):
    """Create Claude Desktop configuration"""
    
    # Get the project directory
    project_dir = Path(__file__).parent.absolute()
    
    config = {
        "mcpServers": {
            "yata-todo": {
                "command": "docker",
                "args": [
                    "run",
                    "--rm",
                    "-i",
                    "--network", "host",  # Use host network to access localhost
                    "-e", f"OAUTH_CLIENT_ID={client_id}",
                    "-e", f"OAUTH_CLIENT_SECRET={client_secret}",
                    "-e", "OAUTH_TOKEN_URL=http://localhost:8000/api/v1/oauth/token",
                    "-e", "API_BASE_URL=http://localhost:8000/api/v1/oauth-todos",
                    "yata-mcp-yata:latest"
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
    print("=== MCP Yata Server Setup for Claude Desktop ===\n")
    
    # Check if backend is running
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
    
    # Create or get OAuth client
    client_id, client_secret = create_or_get_oauth_client()
    
    if not client_id or not client_secret:
        print("❌ Failed to set up OAuth client")
        sys.exit(1)
    
    print(f"✅ OAuth client configured: {client_id[:20]}...")
    
    # Build MCP server Docker image
    print("\nBuilding MCP server Docker image...")
    result = os.system("docker-compose -f docker-compose.dev.yml build mcp-yata > /dev/null 2>&1")
    if result != 0:
        print("❌ Failed to build MCP server image")
        sys.exit(1)
    print("✅ MCP server image built")
    
    # Create Claude Desktop configuration
    config = create_claude_config(client_id, client_secret)
    
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

if __name__ == "__main__":
    main()