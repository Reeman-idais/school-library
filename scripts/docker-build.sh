#!/bin/bash

# Docker helper script for the school-library application
# Usage: ./scripts/docker-build.sh [command]

set -e

COMMAND="${1:-help}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
NO_PULL="${NO_PULL:-false}"
NO_CACHE="${NO_CACHE:-false}"

# Colors
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}🐳 $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

function success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function error() {
    echo -e "${RED}❌ $1${NC}"
}

function show_help() {
    cat << EOF
📚 School Library Docker Helper

USAGE: ./scripts/docker-build.sh [command] [options]

COMMANDS:
  help              Show this help message
  build             Build Docker images
  up                Start containers
  down              Stop containers
  logs              View container logs
  test              Run tests in Docker
  shell             Open shell in running container
  clean             Remove containers and images
  push              Push images to registry
  pull              Pull images from registry

OPTIONS:
  ENVIRONMENT=dev|staging|prod    Set environment (default: dev)
  NO_PULL=true                    Don't pull images first
  NO_CACHE=true                   Build without cache

EXAMPLES:
  # Build images
  ./scripts/docker-build.sh build

  # Start containers for development
  ./scripts/docker-build.sh up

  # Run tests
  ./scripts/docker-build.sh test

  # View logs
  ./scripts/docker-build.sh logs

  # Clean with custom environment
  ENVIRONMENT=prod ./scripts/docker-build.sh clean
EOF
}

function build_images() {
    header "Building Docker Images"
    
    CACHE_ARG=""
    if [ "$NO_CACHE" = "true" ]; then
        CACHE_ARG="--no-cache"
    fi
    
    # Build main application image
    echo "Building main application image..."
    docker build -t school-library:latest -f Dockerfile $CACHE_ARG .
    success "Main image built"
    
    # Build test image
    echo "Building test image..."
    docker build -t school-library:test -f Dockerfile.test $CACHE_ARG .
    success "Test image built"
}

function start_containers() {
    header "Starting Containers ($ENVIRONMENT)"
    
    if [ "$NO_PULL" != "true" ]; then
        echo "Pulling latest images..."
        docker-compose pull || true
    fi
    
    COMPOSE_ARGS="-f docker-compose.yml"
    if [ "$ENVIRONMENT" = "dev" ]; then
        COMPOSE_ARGS="$COMPOSE_ARGS -f docker-compose.override.yml"
    fi
    
    echo "Starting services..."
    eval "docker-compose $COMPOSE_ARGS up -d"
    
    success "Containers started"
    echo -e "\n📊 Service Status:"
    eval "docker-compose $COMPOSE_ARGS ps"
}

function stop_containers() {
    header "Stopping Containers"
    docker-compose down
    success "Containers stopped"
}

function view_logs() {
    header "Container Logs"
    docker-compose logs -f
}

function run_tests() {
    header "Running Tests"
    
    echo "Building test image..."
    docker build -t school-library:test -f Dockerfile.test .
    
    echo "Running tests..."
    docker run --rm \
        -v "$(pwd)/coverage:/app/coverage" \
        school-library:test
    
    success "Tests completed"
    echo -e "\n📊 Coverage report generated in ./coverage"
}

function open_shell() {
    header "Opening Container Shell"
    
    CONTAINER_NAME="school-library-app"
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        error "Container '$CONTAINER_NAME' is not running"
        exit 1
    fi
    
    docker exec -it "$CONTAINER_NAME" /bin/bash
}

function clean_resources() {
    header "Cleaning Up Docker Resources"
    
    echo "Stopping containers..."
    docker-compose down --volumes
    
    echo "Removing images..."
    docker rmi school-library:latest school-library:test 2>/dev/null || true
    
    echo "Pruning system..."
    docker system prune -f
    
    success "Cleanup complete"
}

function push_images() {
    header "Pushing Images to Registry"
    
    echo "Tagging images..."
    docker tag school-library:latest ghcr.io/reeman-idais/school-library:latest
    
    echo "Pushing to registry..."
    docker push ghcr.io/reeman-idais/school-library:latest
    
    success "Images pushed"
}

function pull_images() {
    header "Pulling Images from Registry"
    
    echo "Pulling images..."
    docker pull ghcr.io/reeman-idais/school-library:latest
    docker tag ghcr.io/reeman-idais/school-library:latest school-library:latest
    
    success "Images pulled"
}

# Main script logic
case "$COMMAND" in
    help)
        show_help
        ;;
    build)
        build_images
        ;;
    up)
        start_containers
        ;;
    down)
        stop_containers
        ;;
    logs)
        view_logs
        ;;
    test)
        run_tests
        ;;
    shell)
        open_shell
        ;;
    clean)
        clean_resources
        ;;
    push)
        push_images
        ;;
    pull)
        pull_images
        ;;
    *)
        error "Unknown command: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac
