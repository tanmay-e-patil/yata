# MCP Server Usage Guide

This guide explains how to use the Yata Todo MCP server with Claude Desktop. You have two authentication options:

## Option 1: OAuth Client Credentials (Recommended for Developers)

This approach uses OAuth 2.0 client credentials flow. It's more secure but requires a one-time setup.

### Automated Setup

Run the automated setup script:

```bash
python setup-mcp-claude.py
```

This script will:
1. Check if the backend is running
2. Create an OAuth client automatically
3. Build the MCP server Docker image
4. Configure Claude Desktop for you

### Manual Setup

1. **Start the backend services**:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d postgres redis backend
   ```

2. **Create an OAuth client**:
   ```bash
   python setup-mcp-client.py
   ```

3. **Build the MCP server**:
   ```bash
   docker-compose -f docker-compose.dev.yml build mcp-yata
   ```

4. **Configure Claude Desktop**:
   - Find your Claude Desktop config file:
     - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
     - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
     - Linux: `~/.config/claude/claude_desktop_config.json`
   
   - Add this configuration (replace with your actual client credentials):
   ```json
   {
     "mcpServers": {
       "yata-todo": {
         "command": "docker",
         "args": [
           "run",
           "--rm",
           "-i",
           "--network", "host",
           "-e", "OAUTH_CLIENT_ID=your_client_id_here",
           "-e", "OAUTH_CLIENT_SECRET=your_client_secret_here",
           "-e", "OAUTH_TOKEN_URL=http://localhost:8000/api/v1/oauth/token",
           "-e", "API_BASE_URL=http://localhost:8000/api/v1/oauth-todos",
           "yata-mcp-yata:latest"
         ]
       }
     }
   }
   ```

## Option 2: Personal Access Tokens (Recommended for Users)

This approach uses personal access tokens that you create through the web interface. It's simpler for end-users.

### Automated Setup

Run the automated setup script:

```bash
python setup-mcp-personal.py
```

This script will:
1. Check if the backend is running
2. Guide you to create a personal access token
3. Configure the MCP server with your token
4. Update Claude Desktop configuration

### Manual Setup

1. **Start all services**:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Create a personal access token**:
   - Open http://localhost:3000 in your browser
   - Log in with your Google account
   - Open http://localhost:8000/docs
   - Click "Authorize" and log in
   - Find the "Personal Tokens" section
   - Use "POST /api/v1/personal-tokens/tokens" to create a token
   - Copy the `token` value from the response

3. **Create MCP environment file**:
   ```bash
   # Create mcp-yata/.env with your token
   cat > mcp-yata/.env << EOF
   PERSONAL_ACCESS_TOKEN=your_personal_token_here
   API_BASE_URL=http://localhost:8000/api/v1/personal-todos
   SERVER_NAME=mcp-yata-personal
   SERVER_VERSION=1.0.0
   AUTH_MODE=personal
   EOF
   ```

4. **Configure Claude Desktop**:
   Add this configuration to your Claude Desktop config file:
   ```json
   {
     "mcpServers": {
       "yata-todo-personal": {
         "command": "docker",
         "args": [
           "run",
           "--rm",
           "-i",
           "--network", "host",
           "--env-file", "$(pwd)/mcp-yata/.env",
           "yata-mcp-yata:latest",
           "python", "-m", "mcp_yata.simple_server"
         ]
       }
     }
   }
   ```

## Using the MCP Server

Once configured, restart Claude Desktop if it's running. You can then use natural language to manage your todos:

### Example Commands

- **Create a todo**:
  - "Create a todo to call mom"
  - "Add a new todo: Finish the project proposal"
  - "I need to buy groceries tomorrow"

- **List todos**:
  - "Show me all my todos"
  - "What do I need to do today?"
  - "List my todos"

- **Update a todo**:
  - "Mark the todo to call mom as complete"
  - "Change the title of the grocery todo to 'Buy groceries and detergent'"
  - "Set the project proposal todo as completed"

- **Delete a todo**:
  - "Delete the todo about calling mom"
  - "Remove the completed grocery item"
  - "Delete all completed todos"

## Troubleshooting

### MCP Server Not Connecting

1. **Check Docker**:
   ```bash
   docker ps | grep yata-mcp-yata
   ```

2. **Check logs**:
   ```bash
   docker logs yata-mcp-yata-1
   ```

3. **Verify backend is running**:
   ```bash
   curl http://localhost:8000/health
   ```

### Authentication Errors

1. **For OAuth**:
   - Check that the OAuth client credentials are correct
   - Verify the client hasn't expired
   - Check backend logs for OAuth errors

2. **For Personal Tokens**:
   - Ensure the token hasn't expired (30 days)
   - Verify you're logged into the web interface
   - Create a new token if needed

### Network Issues

- Ensure Docker containers can communicate with the backend
- On macOS/Windows, `--network host` should work for localhost access
- On Linux, you might need to use `--network bridge` and container names

## Security Notes

### OAuth Client Credentials
- Client secrets are sensitive - store them securely
- The MCP server has access to all todos associated with the OAuth client
- Tokens expire after 1 hour and are automatically refreshed

### Personal Access Tokens
- Tokens are shown only once when created
- Tokens expire after 30 days by default
- Each user can have up to 5 active tokens
- Revoke tokens when no longer needed through the API

## Development

For development, you can run the MCP server directly without Docker:

```bash
# OAuth mode
cd mcp-yata
export OAUTH_CLIENT_ID=your_id
export OAUTH_CLIENT_SECRET=your_secret
export OAUTH_TOKEN_URL=http://localhost:8000/api/v1/oauth/token
export API_BASE_URL=http://localhost:8000/api/v1/oauth-todos
python -m mcp_yata.server

# Personal token mode
cd mcp-yata
export PERSONAL_ACCESS_TOKEN=your_token
export API_BASE_URL=http://localhost:8000/api/v1/personal-todos
python -m mcp_yata.simple_server
```

Then configure Claude Desktop to run the Python script directly instead of using Docker.