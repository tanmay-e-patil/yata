# Architecture Diagrams

## System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Browser]
        AI[AI Assistant with MCP]
    end
    
    subgraph "Frontend Service"
        FE[React Frontend :3000]
    end
    
    subgraph "API Gateway"
        NGINX[Nginx/Traefik]
    end
    
    subgraph "Backend Services"
        API[FastAPI Backend :8000]
        OAUTH[OAuth Provider]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL)]
        REDIS[(Redis)]
    end
    
    subgraph "External Services"
        GOOGLE[Google OAuth]
    end
    
    WEB <--> NGINX
    NGINX <--> FE
    FE <--> API
    AI <--> API
    API --> OAUTH
    OAUTH <--> GOOGLE
    API --> PG
    API --> REDIS
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant User as User
    participant Browser as Web Browser
    participant Frontend as React App
    participant Backend as FastAPI
    participant Google as Google OAuth
    participant DB as Database

    User->>Browser: Clicks Login
    Browser->>Frontend: Initiate login
    Frontend->>Backend: GET /api/v1/auth/google/login
    Backend->>Google: Redirect to Google OAuth
    Google->>User: Show consent screen
    User->>Google: Grant permission
    Google->>Backend: Redirect with authorization code
    Backend->>Google: Exchange code for tokens
    Google->>Backend: Return access token & user info
    Backend->>DB: Create/update user record
    Backend->>Backend: Create session
    Backend->>Frontend: Redirect with session
    Frontend->>Browser: Set session cookie
    Frontend->>User: Show authenticated state
```

## API Data Flow

```mermaid
graph LR
    subgraph "Request Flow"
        CLIENT[Client Request]
        AUTH[Authentication Middleware]
        API[API Endpoint]
        SERVICE[Service Layer]
        DB[(Database)]
        CACHE[(Redis Cache)]
    end
    
    subgraph "Response Flow"
        DB_RESP[Database Response]
        SERVICE_RESP[Service Response]
        API_RESP[API Response]
        CLIENT_RESP[Client Response]
    end
    
    CLIENT --> AUTH
    AUTH --> API
    API --> SERVICE
    SERVICE --> DB
    SERVICE --> CACHE
    DB --> DB_RESP
    CACHE --> SERVICE_RESP
    DB_RESP --> SERVICE_RESP
    SERVICE_RESP --> API_RESP
    API_RESP --> CLIENT_RESP
```

## Development Environment

```mermaid
graph TB
    subgraph "Docker Compose Development"
        subgraph "Frontend Container"
            FE_DEV[React Dev Server :3000]
            VITE[Vite HMR]
        end
        
        subgraph "Backend Container"
            BE_DEV[FastAPI Dev Server :8000]
            UVICORN[Uvicorn with Reload]
        end
        
        subgraph "Database Containers"
            PG_DEV[(PostgreSQL :5432)]
            REDIS_DEV[(Redis :6379)]
        end
        
        subgraph "MCP Server"
            MCP_DEV[MCP-Yata Server]
        end
    end
    
    subgraph "Host Machine"
        DEV[Developer]
        IDE[IDE/Editor]
        TERMINAL[Terminal]
    end
    
    DEV --> IDE
    DEV --> TERMINAL
    IDE --> FE_DEV
    IDE --> BE_DEV
    TERMINAL --> FE_DEV
    TERMINAL --> BE_DEV
    FE_DEV --> BE_DEV
    BE_DEV --> PG_DEV
    BE_DEV --> REDIS_DEV
    MCP_DEV --> BE_DEV
```

## OAuth 2.0 Machine-to-Machine Flow (MCP)

```mermaid
sequenceDiagram
    participant MCPServer as MCP Server
    participant OAuthServer as OAuth Server (Yata API)
    participant YataAPI as Yata API
    participant AI as AI Assistant

    Note over MCPServer,YataAPI: Setup Phase (One-time)
    AI->>MCPServer: Start MCP Server
    MCPServer->>OAuthServer: Register OAuth Client
    OAuthServer-->>MCPServer: Return client_id, client_secret

    Note over MCPServer,YataAPI: Authentication Flow
    MCPServer->>OAuthServer: POST /oauth/token (client_id, client_secret)
    OAuthServer-->>MCPServer: Return access_token

    Note over MCPServer,YataAPI: Todo Operations
    AI->>MCPServer: Create todo request
    MCPServer->>YataAPI: POST /api/v1/todos (Bearer: access_token)
    YataAPI-->>MCPServer: Return created todo
    MCPServer-->>AI: Return todo details
```

## Production Architecture

```mermaid
graph TB
    subgraph "Internet"
        USER[End Users]
        AI_CLIENTS[AI Clients]
    end
    
    subgraph "CDN/Load Balancer"
        LB[Load Balancer]
        CDN[CDN]
    end
    
    subgraph "Web Services"
        FE[Frontend Containers]
        BE[Backend Containers]
    end
    
    subgraph "API Gateway"
        GATEWAY[Traefik Gateway]
    end
    
    subgraph "Data Services"
        PG_CLUSTER[(PostgreSQL Cluster)]
        REDIS_CLUSTER[(Redis Cluster)]
    end
    
    subgraph "Monitoring"
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana]
    end
    
    USER --> CDN
    USER --> LB
    LB --> GATEWAY
    CDN --> FE
    GATEWAY --> FE
    GATEWAY --> BE
    AI_CLIENTS --> GATEWAY
    BE --> PG_CLUSTER
    BE --> REDIS_CLUSTER
    BE --> PROMETHEUS
    PROMETHEUS --> GRAFANA