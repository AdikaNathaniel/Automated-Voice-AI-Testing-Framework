#!/bin/bash

################################################################################
# Development Setup Script
#
# This script automates the local development environment setup for the
# automated testing application. It handles:
# - Docker environment startup
# - Database creation and initialization
# - Running database migrations
# - Seeding initial test data
# - Starting all application services
#
# Usage:
#   ./scripts/dev-setup.sh [options]
#
# Options:
#   --clean    Clean up existing containers and volumes before setup
#   --help     Display this help message
################################################################################

set -euo pipefail  # Exit on error, undefined variable, or pipe failure

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

################################################################################
# Helper Functions
################################################################################

# Print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required dependencies
check_dependencies() {
    print_info "Checking required dependencies..."

    local missing_deps=()

    if ! command_exists docker; then
        missing_deps+=("docker")
    fi

    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        missing_deps+=("docker-compose")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        print_error "Please install the missing dependencies and try again."
        exit 1
    fi

    print_info "All dependencies are installed."
}

# Wait for a service to be healthy
wait_for_service() {
    local service_name="$1"
    local max_attempts=30
    local attempt=0

    print_info "Waiting for $service_name to be ready..."

    while [ $attempt -lt $max_attempts ]; do
        if docker-compose ps | grep -q "$service_name.*healthy"; then
            print_info "$service_name is ready!"
            return 0
        fi

        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done

    print_error "$service_name did not become ready in time"
    return 1
}

################################################################################
# Setup Functions
################################################################################

# Clean up existing containers and volumes
cleanup_environment() {
    print_info "Cleaning up existing environment..."

    cd "$PROJECT_ROOT"

    # Stop and remove containers
    if docker-compose ps -q | grep -q .; then
        print_info "Stopping existing containers..."
        docker-compose down -v
    fi

    print_info "Environment cleaned up successfully."
}

# Start Docker services
start_docker_services() {
    print_info "Starting Docker services..."

    cd "$PROJECT_ROOT"

    # Start postgres and redis first (dependencies)
    print_info "Starting database services (postgres, redis)..."
    docker-compose up -d postgres redis

    # Wait for postgres to be healthy
    print_info "Waiting for PostgreSQL to be ready..."
    sleep 5

    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; then
            print_info "PostgreSQL is ready!"
            break
        fi

        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done

    if [ $attempt -eq $max_attempts ]; then
        print_error "PostgreSQL did not become ready in time"
        exit 1
    fi

    print_info "Database services started successfully."
}

# Initialize database
initialize_database() {
    print_info "Initializing database..."

    cd "$PROJECT_ROOT"

    # Database should already be created by docker-compose environment variables
    # Check if database exists
    if docker-compose exec -T postgres psql -U postgres -lqt | cut -d \| -f 1 | grep -qw voiceai_testing; then
        print_info "Database 'voiceai_testing' already exists."
    else
        print_info "Creating database 'voiceai_testing'..."
        docker-compose exec -T postgres createdb -U postgres voiceai_testing
        print_info "Database created successfully."
    fi
}

# Run database migrations
run_migrations() {
    print_info "Running database migrations..."

    cd "$PROJECT_ROOT"

    # Check if backend is running, if not start it temporarily
    if ! docker-compose ps backend | grep -q "Up"; then
        print_info "Starting backend service for migrations..."
        docker-compose up -d backend
        sleep 10
    fi

    # Run alembic migrations
    print_info "Applying alembic migrations..."
    if [ -d "$PROJECT_ROOT/backend/alembic" ]; then
        docker-compose exec -T backend alembic upgrade head || {
            print_warn "Alembic migrations not configured yet or failed. Skipping..."
        }
    else
        print_warn "Alembic directory not found. Skipping migrations..."
    fi

    print_info "Database migrations completed."
}

# Seed initial data
seed_initial_data() {
    print_info "Seeding initial data..."

    cd "$PROJECT_ROOT"

    # Check if seed script exists
    if [ -f "$PROJECT_ROOT/backend/scripts/seed_data.py" ]; then
        print_info "Running seed data script..."
        docker-compose exec -T backend python scripts/seed_data.py || {
            print_warn "Seed data script failed or not available. Skipping..."
        }
    elif [ -f "$PROJECT_ROOT/backend/seed_data.sql" ]; then
        print_info "Running seed data SQL..."
        docker-compose exec -T postgres psql -U postgres -d voiceai_testing -f /docker-entrypoint-initdb.d/seed_data.sql || {
            print_warn "Seed data SQL failed or not available. Skipping..."
        }
    else
        print_warn "No seed data script found. Skipping initial data seeding..."
        print_info "You can add seed data by creating backend/scripts/seed_data.py"
    fi

    print_info "Initial data seeding completed."
}

# Start all application services
start_all_services() {
    print_info "Starting all application services..."

    cd "$PROJECT_ROOT"

    # Start all services
    print_info "Starting backend, frontend, nginx, and admin services..."
    docker-compose up -d

    print_info "Waiting for all services to be healthy..."
    sleep 10

    print_info "All services started successfully."
    print_info ""
    print_info "========================================="
    print_info "Development environment is ready!"
    print_info "========================================="
    print_info "Backend API:    http://localhost:8000"
    print_info "Frontend:       http://localhost:3000"
    print_info "Nginx Proxy:    http://localhost"
    print_info "pgAdmin:        http://localhost:5050"
    print_info "========================================="
    print_info ""
    print_info "To view logs: docker-compose logs -f"
    print_info "To stop:      docker-compose down"
}

# Display help message
show_help() {
    cat << EOF
Development Setup Script

This script automates the local development environment setup.

Usage:
    $0 [options]

Options:
    --clean    Clean up existing containers and volumes before setup
    --help     Display this help message

Examples:
    $0                 # Normal setup
    $0 --clean         # Clean setup from scratch

EOF
}

################################################################################
# Main Execution
################################################################################

main() {
    local clean_mode=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean)
                clean_mode=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    print_info "========================================="
    print_info "Development Environment Setup"
    print_info "========================================="
    print_info ""

    # Check dependencies
    check_dependencies

    # Clean up if requested
    if [ "$clean_mode" = true ]; then
        cleanup_environment
    fi

    # Run setup steps
    start_docker_services
    initialize_database
    run_migrations
    seed_initial_data
    start_all_services

    print_info ""
    print_info "Setup completed successfully! 🚀"
}

# Run main function
main "$@"
