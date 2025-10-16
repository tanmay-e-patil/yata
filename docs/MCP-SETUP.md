# MCP Server Setup Guide

This guide will help you set up the MCP server for the Yata Todo application.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for running the setup script)
- Backend and frontend services configured

## Setup Steps

### 1. Start the Backend Service

First, start only the backend service to create the OAuth client:

```bash
docker-compose up -d postgres redis backend
```

Wait for the backend to be fully started (you can check with `docker-compose logs backend`).

### 2. Create OAuth Client

Run the setup script to create an OAuth client for the MCP server:

```bash
python setup-mcp-client.py
```

This will:
- Create an OAuth client in the backend
- Test the client credentials
- Provide the client ID and secret

### 3. Configure Environment

Add the OAuth client credentials to your `.env` file:

```bash
# Add these lines to your .env file
MCP_OAUTH_CLIENT_ID=your-client-id-here
MCP_OAUTH_CLIENT_SECRET=your-client-secret-here
```

### 4. Start All Services

Now start all services including the MCP server:

```bash
docker-compose up --build
```

This will start:
- PostgreSQL database
- Redis cache
- Backend API
- Frontend application
- MCP server

## Verification

### Check Backend OAuth Endpoints

You can verify the OAuth setup by checking:

1. **Token Endpoint**: http://localhost:8000/docs#/OAuth/oauth_token_post
2. **OAuth Client Creation**: http://localhost:8000/docs#/OAuth/create_client_oauth_clients_post

### Test MCP Server

The MCP server runs as a stdio service and doesn't expose HTTP endpoints. It communicates through the MCP protocol with AI assistants.

## Usage with AI Assistants

Once the MCP server is running, you can connect it to AI assistants that support the MCP protocol (like Claude Desktop).

The server provides these tools:
- `create_todo`: Create a new todo
- `list_todos`: Get all todos
- `get_todo`: Get a specific todo
- `update_todo`: Update an existing todo
- `delete_todo`: Delete a todo

## Troubleshooting

### OAuth Client Creation Fails

- Make sure the backend is running at http://localhost:8000
- Check that the database tables are created
- Verify the backend logs for any errors

### MCP Server Fails to Start

- Check that the OAuth client credentials are correctly set in the .env file
- Verify the backend is accessible from the MCP server container
- Check the MCP server logs with `docker-compose logs mcp-yata`

### Authentication Errors

- Verify the OAuth client credentials are correct
- Check that the client has the required scopes (todos:read todos:write)
- Ensure the token is not expired

## Architecture

The setup consists of:

1. **Backend**: FastAPI application with OAuth 2.0 server
2. **MCP Server**: Standalone service that authenticates with OAuth and provides todo operations
3. **Database**: PostgreSQL storing OAuth clients, tokens, and todos
4. **Cache**: Redis for session management

## Security Notes

- OAuth client secrets are sensitive - keep them secure
- Access tokens expire after 1 hour
- All communications between services should use HTTPS in production
- The MCP server only has access to the scopes granted to its OAuth client

## Next Steps

Once setup is complete:

1. Connect the MCP server to your AI assistant
2. Test the todo operations through natural language
3. Customize the MCP tools if needed
4. Deploy to production with proper security measures