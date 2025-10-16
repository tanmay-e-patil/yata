# Production Deployment Guide for MCP Server

This guide explains how to deploy the Yata Todo MCP server in a production environment.

## Architecture Overview

In production, the MCP server would be deployed as a standalone service that users can connect to using their personal access tokens. The architecture includes:

1. **Backend API** - Production FastAPI server with HTTPS
2. **MCP Server** - Containerized service that connects to the backend
3. **Database** - PostgreSQL with proper backups
4. **Authentication** - Personal access tokens with proper expiration

## Production Configuration

### 1. Environment Variables

Create a production `.env` file:

```bash
# Backend Configuration
DATABASE_URL=postgresql://user:password@prod-db-host:5432/yata_prod
REDIS_URL=redis://prod-redis-host:6379
SECRET_KEY=your-super-secure-production-secret-key
FRONTEND_URL=https://yourapp.com

# OAuth Configuration
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret

# Production Settings
DEBUG=false
SESSION_EXPIRE_HOURS=24
OAUTH_TOKEN_EXPIRE_SECONDS=3600
```

### 2. Docker Compose for Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: yata_prod
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    networks:
      - yata-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - yata-network

  backend:
    image: yata-backend:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - FRONTEND_URL=${FRONTEND_URL}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - yata-network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`api.yourapp.com`)"
      - "traefik.http.routers.backend.tls=true"

  frontend:
    image: yata-frontend:latest
    environment:
      - VITE_API_URL=https://api.yourapp.com
      - VITE_GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
    restart: unless-stopped
    networks:
      - yata-network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`yourapp.com`)"
      - "traefik.http.routers.frontend.tls=true"

  # Reverse Proxy
  traefik:
    image: traefik:v2.10
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=admin@yourapp.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    restart: unless-stopped
    networks:
      - yata-network

networks:
  yata-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

### 3. Production MCP Server Deployment

The MCP server in production would be deployed differently. Instead of running it in Docker on each user's machine, you have two options:

#### Option A: User-Hosted MCP Server (Recommended)

Users run the MCP server locally, connecting to your production backend:

```bash
# User's Claude Desktop configuration
{
  "mcpServers": {
    "yata-todo": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "PERSONAL_ACCESS_TOKEN=user_token_here",
        "-e", "API_BASE_URL=https://api.yourapp.com/api/v1/personal-todos",
        "yourapp/mcp-yata:latest",
        "python", "-m", "mcp_yata.simple_server"
      ]
    }
  }
}
```

#### Option B: Cloud-Hosted MCP Service

For enterprise users, you can host the MCP server as a service:

```yaml
# Add to docker-compose.prod.yml
  mcp-service:
    image: yourapp/mcp-yata:latest
    environment:
      - API_BASE_URL=https://api.yourapp.com/api/v1/personal-todos
    restart: unless-stopped
    networks:
      - yata-network
```

### 4. Security Considerations

#### Authentication
- Personal tokens should have configurable expiration (7-30 days)
- Implement rate limiting for token creation
- Add audit logging for token usage
- Consider IP whitelisting for sensitive operations

#### Network Security
- All communication must use HTTPS
- Implement CORS properly
- Use internal networks for service communication
- Add firewall rules to restrict access

#### Data Protection
- Encrypt sensitive data at rest
- Use environment variables for secrets
- Implement proper database backups
- Consider data retention policies

### 5. Monitoring and Logging

#### Application Monitoring
```yaml
# Add to docker-compose.prod.yml
  monitoring:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped
    networks:
      - yata-network

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped
    networks:
      - yata-network
```

#### Logging
- Use structured JSON logging
- Implement log aggregation with ELK stack or similar
- Set up alerts for critical errors
- Monitor authentication failures

### 6. Deployment Script

Create `deploy.sh`:

```bash
#!/bin/bash

# Build and deploy to production
echo "Building production images..."

# Build backend
docker build -t yata-backend:latest ./backend

# Build frontend
docker build -t yata-frontend:latest ./frontend

# Build MCP server
docker build -t yourapp/mcp-yata:latest ./mcp-yata

# Deploy
echo "Deploying to production..."
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

echo "Deployment complete!"
```

### 7. CI/CD Pipeline

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
          
      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: yourapp/backend:latest
          
      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: yourapp/frontend:latest
          
      - name: Build and push MCP server
        uses: docker/build-push-action@v4
        with:
          context: ./mcp-yata
          push: true
          tags: yourapp/mcp-yata:latest
          
      - name: Deploy to production
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/yata
            docker-compose -f docker-compose.prod.yml pull
            docker-compose -f docker-compose.prod.yml up -d
```

### 8. User Management

For production, you'll need a proper user management system:

#### User Registration
- Implement email verification
- Add user roles (free, premium, enterprise)
- Set up subscription management if needed

#### Token Management
- Implement token usage limits
- Add token refresh mechanism
- Provide token management UI in the frontend

#### Analytics
- Track MCP server usage
- Monitor API usage patterns
- Generate usage reports for billing

### 9. Scaling Considerations

#### Horizontal Scaling
- Use load balancers for the backend
- Implement session affinity if needed
- Consider read replicas for database

#### Caching Strategy
- Redis for session storage
- Cache frequently accessed todos
- Implement CDN for static assets

#### Database Optimization
- Add proper indexes
- Implement connection pooling
- Consider database sharding for large scale

### 10. Disaster Recovery

#### Backup Strategy
```bash
# Daily database backup
0 2 * * * docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres yata_prod > /backups/yata_$(date +%Y%m%d).sql

# Weekly backup to cloud storage
0 3 * * 0 aws s3 sync /backups/ s3://yourapp-backups/
```

#### High Availability
- Multi-region deployment
- Database failover setup
- Health checks and auto-recovery

This production setup ensures your MCP server is secure, scalable, and maintainable in a production environment.