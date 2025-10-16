# MCP Server Implementation Guide

## 1. Backend OAuth 2.0 Implementation

### 1.1 Add OAuth Dependencies

Update `backend/requirements.txt`:
```
authlib==1.2.1
```

### 1.2 Create OAuth Client Model

Create `backend/app/models/oauth_client.py`:
```python
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class OAuthClient(Base):
    __tablename__ = "oauth_clients"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, unique=True, nullable=False, index=True)
    client_secret = Column(String, nullable=False)
    client_name = Column(String, nullable=False)
    scopes = Column(Text, nullable=False)  # JSON string of allowed scopes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<OAuthClient(id={self.id}, client_id={self.client_id})>"
```

### 1.3 Create OAuth Token Model

Create `backend/app/models/oauth_token.py`:
```python
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, ForeignKey("oauth_clients.client_id"), nullable=False)
    access_token = Column(String, unique=True, nullable=False, index=True)
    token_type = Column(String, default="Bearer")
    expires_at = Column(DateTime(timezone=True), nullable=False)
    scopes = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with OAuthClient
    client = relationship("OAuthClient", backref="tokens")

    def __repr__(self):
        return f"<OAuthToken(id={self.id}, client_id={self.client_id})>"
```

### 1.4 Update Configuration

Add to `backend/app/core/config.py`:
```python
# OAuth settings
oauth_token_expire_seconds: int = 3600  # 1 hour
```

### 1.5 Create OAuth Service

Create `backend/app/services/oauth_service.py`:
```python
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.oauth_client import OAuthClient
from app.models.oauth_token import OAuthToken


class OAuthService:
    @staticmethod
    def create_client(
        db: Session, 
        client_name: str, 
        scopes: List[str]
    ) -> OAuthClient:
        """Create a new OAuth client"""
        client = OAuthClient(
            client_id=secrets.token_urlsafe(32),
            client_secret=secrets.token_urlsafe(64),
            client_name=client_name,
            scopes=json.dumps(scopes)
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        return client
    
    @staticmethod
    def authenticate_client(
        db: Session, 
        client_id: str, 
        client_secret: str
    ) -> Optional[OAuthClient]:
        """Authenticate OAuth client"""
        return db.query(OAuthClient).filter(
            OAuthClient.client_id == client_id,
            OAuthClient.client_secret == client_secret,
            OAuthClient.is_active == True
        ).first()
    
    @staticmethod
    def generate_token(
        db: Session, 
        client: OAuthClient, 
        scopes: List[str]
    ) -> OAuthToken:
        """Generate access token for client"""
        # Deactivate existing tokens for this client
        db.query(OAuthToken).filter(
            OAuthToken.client_id == client.client_id,
            OAuthToken.is_active == True
        ).update({"is_active": False})
        
        # Create new token
        token = OAuthToken(
            client_id=client.client_id,
            access_token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(seconds=settings.oauth_token_expire_seconds),
            scopes=json.dumps(scopes)
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        return token
    
    @staticmethod
    def validate_token(
        db: Session, 
        access_token: str
    ) -> Optional[OAuthToken]:
        """Validate access token"""
        token = db.query(OAuthToken).filter(
            OAuthToken.access_token == access_token,
            OAuthToken.is_active == True,
            OAuthToken.expires_at > datetime.utcnow()
        ).first()
        return token
```

### 1.6 Create OAuth Endpoints

Create `backend/app/api/v1/oauth.py`:
```python
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.services.oauth_service import OAuthService
from pydantic import BaseModel

router = APIRouter()
security = HTTPBasic()


class TokenRequest(BaseModel):
    grant_type: str = "client_credentials"
    scope: str = ""


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: str


@router.post("/token", response_model=TokenResponse)
async def create_token(
    token_request: TokenRequest,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """OAuth 2.0 token endpoint"""
    # Validate grant type
    if token_request.grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant type"
        )
    
    # Authenticate client
    client = OAuthService.authenticate_client(
        db, credentials.username, credentials.password
    )
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Parse scopes
    requested_scopes = token_request.scope.split() if token_request.scope else []
    allowed_scopes = json.loads(client.scopes)
    
    # Validate requested scopes
    for scope in requested_scopes:
        if scope not in allowed_scopes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid scope: {scope}"
            )
    
    # Generate token
    token = OAuthService.generate_token(db, client, requested_scopes)
    
    return TokenResponse(
        access_token=token.access_token,
        token_type=token.token_type,
        expires_in=settings.oauth_token_expire_seconds,
        scope=" ".join(requested_scopes)
    )
```

### 1.7 Update Main Application

Update `backend/app/main.py`:
```python
# Add OAuth router
from app.api.v1 import oauth

# Include OAuth router
app.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
```

### 1.8 Create OAuth Authentication Dependency

Create `backend/app/api/oauth_deps.py`:
```python
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.oauth_service import OAuthService

security = HTTPBearer()


async def get_oauth_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Validate OAuth token and get client"""
    token = OAuthService.validate_token(db, credentials.credentials)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token.client
```

## 2. MCP Server Implementation

### 2.1 Project Structure

```
mcp-yata/
├── mcp_yata/
│   ├── __init__.py
│   ├── server.py          # Main MCP server
│   ├── auth.py            # OAuth client
│   ├── client.py          # API client
│   ├── tools.py           # MCP tools
│   └── config.py          # Configuration
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

### 2.2 Dependencies

Create `mcp-yata/requirements.txt`:
```
mcp>=1.0.0
httpx>=0.25.0
authlib>=1.2.0
pydantic>=2.5.0
python-dotenv>=1.0.0
```

### 2.3 Configuration

Create `mcp-yata/mcp_yata/config.py`:
```python
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # OAuth settings
    oauth_client_id: str
    oauth_client_secret: str
    oauth_token_url: str = "http://backend:8000/oauth/token"
    
    # API settings
    api_base_url: str = "http://backend:8000/api/v1"
    
    # MCP settings
    server_name: str = "mcp-yata"
    server_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"


settings = Settings()
```

### 2.4 OAuth Client

Create `mcp-yata/mcp_yata/auth.py`:
```python
import time
from typing import Optional
from authlib.integrations.httpx_client import OAuth2Client
from .config import settings


class OAuthClient:
    def __init__(self):
        self.client = OAuth2Client(
            client_id=settings.oauth_client_id,
            client_secret=settings.oauth_client_secret,
            token_endpoint=settings.oauth_token_url,
            token_endpoint_auth_method="client_secret_basic"
        )
        self._token = None
        self._token_expires_at = 0
    
    def get_access_token(self) -> str:
        """Get valid access token, refreshing if necessary"""
        current_time = time.time()
        
        # Check if token is valid
        if self._token and current_time < self._token_expires_at:
            return self._token["access_token"]
        
        # Fetch new token
        token = self.client.fetch_token(
            grant_type="client_credentials",
            scope="todos:read todos:write"
        )
        
        # Store token and expiration
        self._token = token
        self._token_expires_at = current_time + token.get("expires_in", 3600) - 60  # Refresh 1 min early
        
        return token["access_token"]


oauth_client = OAuthClient()
```

### 2.5 API Client

Create `mcp-yata/mcp_yata/client.py`:
```python
import httpx
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from .auth import oauth_client
from .config import settings


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class YataAPIClient:
    def __init__(self):
        self.base_url = settings.api_base_url
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        token = oauth_client.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def create_todo(self, todo: TodoCreate) -> Dict[str, Any]:
        """Create a new todo"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/todos/",
                json=todo.dict(),
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def list_todos(self) -> List[Dict[str, Any]]:
        """Get all todos"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/todos/",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_todo(self, todo_id: str) -> Dict[str, Any]:
        """Get a specific todo"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/todos/{todo_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def update_todo(self, todo_id: str, todo: TodoUpdate) -> Dict[str, Any]:
        """Update a todo"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/todos/{todo_id}",
                json=todo.dict(exclude_unset=True),
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_todo(self, todo_id: str) -> Dict[str, Any]:
        """Delete a todo"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/todos/{todo_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()


yata_client = YataAPIClient()
```

### 2.6 MCP Tools

Create `mcp-yata/mcp_yata/tools.py`:
```python
from typing import Dict, Any, List, Optional
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from .client import yata_client, TodoCreate, TodoUpdate


def setup_todo_tools(server: Server):
    """Setup todo-related tools"""
    
    @server.list_tools()
    async def handle_list_tools() -> List[Tool]:
        """List available tools"""
        return [
            Tool(
                name="create_todo",
                description="Create a new todo item",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title of the todo item"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the todo"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Whether the todo is completed (default: false)",
                            "default": False
                        }
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="list_todos",
                description="Get all todos for the authenticated user",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="get_todo",
                description="Get a specific todo by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "todo_id": {
                            "type": "string",
                            "description": "ID of the todo to retrieve"
                        }
                    },
                    "required": ["todo_id"]
                }
            ),
            Tool(
                name="update_todo",
                description="Update an existing todo",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "todo_id": {
                            "type": "string",
                            "description": "ID of the todo to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the todo"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description for the todo"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Whether the todo is completed"
                        }
                    },
                    "required": ["todo_id"]
                }
            ),
            Tool(
                name="delete_todo",
                description="Delete a todo",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "todo_id": {
                            "type": "string",
                            "description": "ID of the todo to delete"
                        }
                    },
                    "required": ["todo_id"]
                }
            )
        ]
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls"""
        try:
            if name == "create_todo":
                todo = TodoCreate(
                    title=arguments["title"],
                    description=arguments.get("description"),
                    completed=arguments.get("completed", False)
                )
                result = await yata_client.create_todo(todo)
                return [TextContent(
                    type="text",
                    text=f"Todo created successfully:\nTitle: {result['title']}\nID: {result['id']}"
                )]
            
            elif name == "list_todos":
                todos = await yata_client.list_todos()
                if not todos:
                    return [TextContent(type="text", text="No todos found")]
                
                todo_list = "\n".join([
                    f"- {todo['title']} (ID: {todo['id']}, Completed: {todo['completed']})"
                    for todo in todos
                ])
                return [TextContent(type="text", text=f"Your todos:\n{todo_list}")]
            
            elif name == "get_todo":
                todo = await yata_client.get_todo(arguments["todo_id"])
                return [TextContent(
                    type="text",
                    text=f"Todo Details:\nTitle: {todo['title']}\nDescription: {todo.get('description', 'N/A')}\nCompleted: {todo['completed']}\nID: {todo['id']}"
                )]
            
            elif name == "update_todo":
                todo_id = arguments["todo_id"]
                update_data = TodoUpdate(**{k: v for k, v in arguments.items() if k != "todo_id" and v is not None})
                result = await yata_client.update_todo(todo_id, update_data)
                return [TextContent(
                    type="text",
                    text=f"Todo updated successfully:\nTitle: {result['title']}\nID: {result['id']}"
                )]
            
            elif name == "delete_todo":
                result = await yata_client.delete_todo(arguments["todo_id"])
                return [TextContent(type="text", text=result["message"])]
            
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
```

### 2.7 Main Server

Create `mcp-yata/mcp_yata/server.py`:
```python
import asyncio
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from .tools import setup_todo_tools
from .config import settings


def create_server() -> Server:
    """Create and configure the MCP server"""
    server = Server(settings.server_name)
    
    # Setup todo tools
    setup_todo_tools(server)
    
    return server


async def main():
    """Main entry point"""
    server = create_server()
    
    # Run the server using stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=settings.server_name,
                server_version=settings.server_version,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
```

## 3. Docker Configuration

### 3.1 MCP Server Dockerfile

Create `mcp-yata/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port (not needed for stdio, but included for health checks)
EXPOSE 8000

# Run the application
CMD ["python", "-m", "mcp_yata.server"]
```

### 3.2 Environment Configuration

Create `mcp-yata/.env.example`:
```
# OAuth Configuration
OAUTH_CLIENT_ID=your_client_id_here
OAUTH_CLIENT_SECRET=your_client_secret_here
OAUTH_TOKEN_URL=http://backend:8000/oauth/token

# API Configuration
API_BASE_URL=http://backend:8000/api/v1

# MCP Configuration
SERVER_NAME=mcp-yata
SERVER_VERSION=1.0.0
```

### 3.3 Update Docker Compose

Update `docker-compose.dev.yml`:
```yaml
services:
  # ... existing services ...
  
  mcp-yata:
    build:
      context: ./mcp-yata
      dockerfile: Dockerfile
    environment:
      - OAUTH_CLIENT_ID=${MCP_OAUTH_CLIENT_ID}
      - OAUTH_CLIENT_SECRET=${MCP_OAUTH_CLIENT_SECRET}
      - OAUTH_TOKEN_URL=http://backend:8000/oauth/token
      - API_BASE_URL=http://backend:8000/api/v1
    depends_on:
      - backend
    networks:
      - yata-network
```

## 4. Setup Instructions

### 4.1 Backend Setup

1. Update `backend/requirements.txt` with OAuth dependencies
2. Create OAuth models and services
3. Add OAuth endpoints to the API
4. Create initial OAuth client for MCP server

### 4.2 MCP Server Setup

1. Create the MCP server project structure
2. Install dependencies
3. Configure environment variables
4. Build and run the MCP server

### 4.3 Testing

1. Test OAuth token generation
2. Test MCP server tools
3. Test integration with AI assistant
4. Verify security and error handling

## 5. Security Considerations

1. Store OAuth client credentials securely
2. Use short-lived access tokens
3. Implement proper scope validation
4. Add rate limiting
5. Monitor and audit API usage
6. Use HTTPS in production