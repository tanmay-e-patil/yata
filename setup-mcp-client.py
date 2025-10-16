#!/usr/bin/env python3
"""
Setup script to create an OAuth client for the MCP server.
Run this script after starting the backend to generate client credentials.
"""

import requests
import json
import sys

def create_oauth_client(base_url="http://localhost:8000"):
    """Create an OAuth client for the MCP server"""
    
    # Client details
    client_name = "MCP Yata Server"
    scopes = "todos:read todos:write"
    
    # API endpoint
    url = f"{base_url}/api/v1/oauth/clients"
    
    try:
        print(f"Creating OAuth client at {url}...")
        response = requests.post(
            url,
            params={
                "client_name": client_name,
                "scopes": scopes
            }
        )
        
        if response.status_code == 200:
            client_data = response.json()
            print("✅ OAuth client created successfully!")
            print("\nClient Credentials:")
            print(f"Client ID: {client_data['client_id']}")
            print(f"Client Secret: {client_data['client_secret']}")
            print(f"Client Name: {client_data['client_name']}")
            print(f"Scopes: {', '.join(client_data['scopes'])}")
            
            print("\nAdd these to your .env file:")
            print(f"MCP_OAUTH_CLIENT_ID={client_data['client_id']}")
            print(f"MCP_OAUTH_CLIENT_SECRET={client_data['client_secret']}")
            
            return client_data
        else:
            print(f"❌ Failed to create OAuth client: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the backend server.")
        print("Make sure the backend is running at http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_oauth_client(client_id, client_secret, base_url="http://localhost:8000"):
    """Test the OAuth client by requesting an access token"""
    
    # Token endpoint
    url = f"{base_url}/api/v1/oauth/token"
    
    try:
        print(f"\nTesting OAuth client at {url}...")
        response = requests.post(
            url,
            auth=(client_id, client_secret),
            json={
                "grant_type": "client_credentials",
                "scope": "todos:read todos:write"
            }
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ OAuth client test successful!")
            print(f"Access Token: {token_data['access_token'][:20]}...")
            print(f"Token Type: {token_data['token_type']}")
            print(f"Expires In: {token_data['expires_in']} seconds")
            print(f"Scope: {token_data['scope']}")
            return True
        else:
            print(f"❌ Failed to get access token: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("=== MCP Yata Server OAuth Client Setup ===\n")
    
    # Create OAuth client
    client_data = create_oauth_client()
    
    if client_data:
        # Test the client
        test_oauth_client(
            client_data['client_id'],
            client_data['client_secret']
        )
        
        print("\n=== Setup Complete ===")
        print("1. Add the client credentials to your .env file")
        print("2. Run 'docker-compose up --build' to start all services")
        print("3. The MCP server will be available for AI assistants")
    else:
        print("\n=== Setup Failed ===")
        print("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()