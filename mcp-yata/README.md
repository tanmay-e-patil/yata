# MCP Server for Yata Todo App

This is a Model Context Protocol (MCP) server that enables AI assistants to interact with the Yata Todo application through secure API calls using OAuth 2.0 machine-to-machine authentication.

## Features

- Full CRUD operations for todos (Create, Read, Update, Delete)
- Secure OAuth 2.0 authentication with client credentials flow
- Standard MCP protocol implementation
- Dockerized deployment

## Setup

1. Copy `.env.example` to `.env` and configure your OAuth credentials:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your OAuth client credentials:
   ```
   OAUTH_CLIENT_ID=your_client_id_here
   OAUTH_CLIENT_SECRET=your_client_secret_here
   ```

3. Build and run with Docker:
   ```bash
   docker build -t mcp-yata .
   docker run --env-file .env mcp-yata
   ```

## MCP Tools

The server provides the following tools:

### create_todo
Create a new todo item
- **title** (required): Title of the todo item
- **description** (optional): Description of the todo
- **completed** (optional): Whether the todo is completed (default: false)

### list_todos
Get all todos for the authenticated user
- No parameters required

### get_todo
Get a specific todo by ID
- **todo_id** (required): ID of the todo to retrieve

### update_todo
Update an existing todo
- **todo_id** (required): ID of the todo to update
- **title** (optional): New title for the todo
- **description** (optional): New description for the todo
- **completed** (optional): Whether the todo is completed

### delete_todo
Delete a todo
- **todo_id** (required): ID of the todo to delete

## Usage Examples

Once connected to an AI assistant, you can use natural language:

```
User: "Create a todo to review the quarterly report"
AI: [Uses create_todo tool]
AI: "I've created a todo titled 'Review the quarterly report'"

User: "Show me all my todos"
AI: [Uses list_todos tool]
AI: "Here are your todos: - Review quarterly report (ID: abc-123, Completed: false)"

User: "Mark the quarterly report review as completed"
AI: [Uses get_todo to find ID, then update_todo]
AI: "I've marked the quarterly report review as completed"
```

## Development

To run in development mode:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

2. Set environment variables:
   ```bash
   export OAUTH_CLIENT_ID=your_client_id
   export OAUTH_CLIENT_SECRET=your_client_secret
   ```

3. Run the server:
   ```bash
   python -m mcp_yata.server
   ```

## Architecture

The MCP server consists of:

- **OAuth Client**: Handles authentication with the Yata API
- **API Client**: Communicates securely with the Yata API
- **MCP Tools**: Implements todo operations using the MCP protocol
- **Configuration Management**: Handles environment variables and settings

## Security

- Uses OAuth 2.0 client credentials flow for authentication
- Access tokens expire after 1 hour with automatic refresh
- All communications are secured with Bearer tokens
- Minimal scopes granted based on required operations