#!/bin/bash

# Relationship Finder API - Docker Deployment Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

check_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed."
        exit 1
    fi
    print_success "Docker Compose is available"
}

build_image() {
    print_info "Building Docker image..."
    docker-compose build
    print_success "Docker image built successfully"
}

start_services() {
    print_info "Starting services..."
    docker-compose up -d
    print_success "Services started"
}

stop_services() {
    print_info "Stopping services..."
    docker-compose stop
    print_success "Services stopped"
}

restart_services() {
    print_info "Restarting services..."
    docker-compose restart
    print_success "Services restarted"
}

show_logs() {
    docker-compose logs -f app
}

show_status() {
    echo ""
    print_info "Container Status:"
    docker-compose ps
    echo ""
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:1001/healthz | grep -q "200"; then
        print_success "API is healthy and responding at http://localhost:1001"
        echo ""
        print_info "Available endpoints:"
        echo "  - API Docs: http://localhost:1001/docs"
        echo "  - Health: http://localhost:1001/healthz"
        echo "  - REST API: http://localhost:1001/relationship?name=Saanvi"
        echo "  - WebSocket: ws://localhost:1001/relationship/stream"
    else
        print_error "API is not responding. Check logs with: ./deploy.sh logs"
    fi
    echo ""
}

clean() {
    print_info "Cleaning up Docker resources..."
    docker-compose down -v
    print_success "Cleanup complete"
}

rebuild() {
    print_info "Rebuilding and restarting services..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    print_success "Services rebuilt and started"
}

show_help() {
    cat << EOF
Relationship Finder API - Docker Deployment Script

Usage: ./deploy.sh [COMMAND]

Commands:
    start       Build and start the services
    stop        Stop the services
    restart     Restart the services
    logs        Show and follow logs
    status      Show service status
    rebuild     Rebuild images and restart
    clean       Stop services and remove containers/volumes
    help        Show this help message

Examples:
    ./deploy.sh start       # Start the application
    ./deploy.sh logs        # View logs
    ./deploy.sh status      # Check if running
    ./deploy.sh stop        # Stop the application

EOF
}

# Main script
main() {
    case "${1:-start}" in
        start)
            check_docker
            check_compose
            build_image
            start_services
            sleep 5
            show_status
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            sleep 3
            show_status
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        rebuild)
            check_docker
            check_compose
            rebuild
            sleep 5
            show_status
            ;;
        clean)
            clean
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
