#!/bin/bash

# Production deployment script for Yata Todo App
# This script builds and deploys the application to production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="yata"
BACKUP_DIR="./backups"
LOG_FILE="./deploy.log"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a $LOG_FILE
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a $LOG_FILE
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a $LOG_FILE
}

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    print_error ".env.production file not found!"
    print_error "Please copy .env.production to .env and configure your values"
    exit 1
fi

# Load environment variables
source .env.production

# Check required variables
check_required_vars() {
    print_status "Checking required environment variables..."
    
    required_vars=(
        "SECRET_KEY"
        "POSTGRES_PASSWORD"
        "GOOGLE_CLIENT_ID"
        "GOOGLE_CLIENT_SECRET"
        "FRONTEND_URL"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables:"
        printf '%s\n' "${missing_vars[@]}"
        exit 1
    fi
    
    print_status "All required variables are set"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p $BACKUP_DIR
    mkdir -p letsencrypt
    mkdir -p monitoring
    
    print_status "Directories created"
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build backend
    print_status "Building backend image..."
    docker build -t yata-backend:latest ./backend 2>&1 | tee -a $LOG_FILE
    
    # Build frontend
    print_status "Building frontend image..."
    docker build -t yata-frontend:latest ./frontend 2>&1 | tee -a $LOG_FILE
    
    # Build MCP server
    print_status "Building MCP server image..."
    docker build -t yourapp/mcp-yata:latest ./mcp-yata 2>&1 | tee -a $LOG_FILE
    
    print_status "All images built successfully"
}

# Database backup before deployment
backup_database() {
    if docker-compose -f docker-compose.prod.yml ps postgres | grep -q "Up"; then
        print_status "Creating database backup..."
        
        backup_file="$BACKUP_DIR/yata_backup_$(date +%Y%m%d_%H%M%S).sql"
        
        docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > $backup_file
        
        # Compress backup
        gzip $backup_file
        
        print_status "Database backup created: ${backup_file}.gz"
    else
        print_warning "Database not running, skipping backup"
    fi
}

# Deploy the application
deploy_app() {
    print_status "Deploying application..."
    
    # Pull latest images
    docker-compose -f docker-compose.prod.yml pull 2>&1 | tee -a $LOG_FILE
    
    # Start services
    docker-compose -f docker-compose.prod.yml up -d 2>&1 | tee -a $LOG_FILE
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Run database migrations if needed
    print_status "Running database migrations..."
    docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head 2>&1 | tee -a $LOG_FILE
    
    print_status "Application deployed successfully"
}

# Health check
health_check() {
    print_status "Performing health checks..."
    
    # Check backend
    if curl -f -s https://$API_DOMAIN/health > /dev/null; then
        print_status "Backend health check passed"
    else
        print_error "Backend health check failed"
        return 1
    fi
    
    # Check frontend
    if curl -f -s https://$FRONTEND_DOMAIN > /dev/null; then
        print_status "Frontend health check passed"
    else
        print_error "Frontend health check failed"
        return 1
    fi
    
    print_status "All health checks passed"
}

# Cleanup old images
cleanup() {
    print_status "Cleaning up old Docker images..."
    docker image prune -f 2>&1 | tee -a $LOG_FILE
    print_status "Cleanup completed"
}

# Main deployment flow
main() {
    print_status "Starting production deployment at $(date)"
    
    # Run checks
    check_required_vars
    create_directories
    
    # Build images
    build_images
    
    # Backup database
    backup_database
    
    # Deploy
    deploy_app
    
    # Health check
    if health_check; then
        print_status "Deployment completed successfully at $(date)"
        
        # Cleanup
        cleanup
        
        # Print next steps
        print_status "Deployment complete!"
        print_status "Your application is now available at:"
        print_status "  Frontend: https://$FRONTEND_DOMAIN"
        print_status "  API: https://$API_DOMAIN"
        print_status "  Traefik Dashboard: https://$TRAEFIK_DOMAIN (if enabled)"
        
        print_status "To deploy the MCP server, users should:"
        print_status "1. Create a personal access token at https://$FRONTEND_DOMAIN"
        print_status "2. Use the setup-mcp-personal.py script with their token"
    else
        print_error "Deployment failed! Check the logs at $LOG_FILE"
        exit 1
    fi
}

# Handle script interruption
trap 'print_error "Deployment interrupted"; exit 1' INT

# Run main function
main "$@"