# Developer Setup Guide

**Voice AI Automated Testing Framework**

This guide provides step-by-step instructions for setting up the development environment for the Voice AI Automated Testing Framework. Follow these instructions to get your local development environment up and running.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running Locally](#running-locally)
5. [Database Migrations](#database-migrations)
6. [Development Workflow](#development-workflow)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Next Steps](#next-steps)

---

## Prerequisites

Before you begin, ensure you have the following software installed on your system:

### Required Software

1. **Python 3.12+**
   - Check version: `python3 --version`
   - Download: [python.org](https://www.python.org/downloads/)
   - Required for backend development (FastAPI)

2. **Node.js 20.x+**
   - Check version: `node --version`
   - Download: [nodejs.org](https://nodejs.org/)
   - Required for frontend development (React + TypeScript)

3. **Docker & Docker Compose**
   - Check version: `docker --version` and `docker-compose --version`
   - Download: [docker.com](https://www.docker.com/get-started)
   - Required for running PostgreSQL, Redis, and pgAdmin

4. **Git**
   - Check version: `git --version`
   - Download: [git-scm.com](https://git-scm.com/downloads/)
   - Required for version control

### Optional but Recommended

- **VS Code** with Python and TypeScript extensions
- **Postman** or **Thunder Client** for API testing
- **pgAdmin** (or use the Docker container version)
- **Redis Commander** for Redis management

### System Requirements

- **OS**: Linux, macOS, or Windows (WSL2 recommended for Windows)
- **RAM**: Minimum 8GB, 16GB recommended
- **Disk Space**: Minimum 10GB free space
- **CPU**: Multi-core processor recommended

---

## Installation

### Step 1: Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/your-org/voice-ai-testing.git
cd voice-ai-testing
```

If you're using SSH:

```bash
git clone git@github.com:your-org/voice-ai-testing.git
cd voice-ai-testing
```

### Step 2: Set Up Python Backend

#### 2.1 Create Python Virtual Environment

Navigate to the project root and create a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows (PowerShell):
# .\venv\Scripts\Activate.ps1
```

You should see `(venv)` in your terminal prompt indicating the virtual environment is active.

#### 2.2 Install Python Dependencies

Install backend dependencies using pip:

```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

This will install:
- FastAPI for API framework
- SQLAlchemy for database ORM
- Alembic for database migrations
- Pydantic for data validation
- Celery for background tasks
- Redis client for caching
- And many more dependencies

### Step 3: Set Up Node.js Frontend

#### 3.1 Install Frontend Dependencies

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
cd ..
```

This will install:
- React 18 for UI framework
- TypeScript for type safety
- Vite for build tooling
- TailwindCSS for styling
- Redux Toolkit for state management
- And all other frontend dependencies

### Step 4: Set Up Docker Services

#### 4.1 Start Docker Containers

Start the required Docker services (PostgreSQL, Redis, pgAdmin):

```bash
docker-compose up -d
```

This command starts the following services:
- **PostgreSQL** (port 5432): Main database
- **Redis** (port 6379): Caching and session storage
- **pgAdmin** (port 5050): Database management UI

#### 4.2 Verify Docker Containers

Check that all containers are running:

```bash
docker-compose ps
```

You should see all services in the "Up" state.

---

## Configuration

### Step 1: Create Environment File

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

### Step 2: Configure Environment Variables

Edit the `.env` file with your local settings:

```bash
# Application Configuration
APP_NAME=Voice AI Testing Framework
ENVIRONMENT=development
DEBUG=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/voiceai_testing
DB_ECHO=false

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AWS Configuration (for SoundHound/S3)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=voiceai-testing-dev

# SoundHound Configuration
SOUNDHOUND_CLIENT_ID=your-client-id
SOUNDHOUND_CLIENT_SECRET=your-client-secret

# Email Configuration (optional for development)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

**Important**: Never commit your `.env` file to version control. It's already in `.gitignore`.

### Step 3: Initialize Database

The database will be automatically created when you start the Docker containers. To verify:

```bash
docker-compose logs postgres
```

You should see log messages indicating PostgreSQL is ready to accept connections.

---

## Running Locally

### Option 1: Run with Docker Compose (Recommended for Full Stack)

Start all services including backend and frontend:

```bash
# Start all services
docker-compose up

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **pgAdmin**: http://localhost:5050

### Option 2: Run Backend and Frontend Separately (Recommended for Development)

This option gives you hot-reload capabilities for faster development.

#### Run Backend (FastAPI)

In one terminal window, activate the virtual environment and start the backend:

```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI development server
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-restart on code changes.

Access the backend:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Schema**: http://localhost:8000/api/openapi.json

#### Run Frontend (React + Vite)

In another terminal window, start the frontend development server:

```bash
cd frontend
npm run dev
```

Access the frontend:
- **Frontend**: http://localhost:5173 (Vite default port)

The frontend will automatically proxy API requests to the backend.

#### Run Celery Worker (Background Tasks)

For processing background tasks, start a Celery worker:

```bash
# Activate virtual environment
source venv/bin/activate

# Start Celery worker
celery -A backend.celery_app worker --loglevel=info
```

#### Run Celery Beat (Scheduled Tasks)

For scheduled tasks, start Celery Beat:

```bash
# Activate virtual environment
source venv/bin/activate

# Start Celery beat
celery -A backend.celery_app beat --loglevel=info
```

---

## Database Migrations

### Understanding Alembic Migrations

This project uses Alembic for database migrations. Migrations allow you to version control your database schema changes.

### Running Migrations

#### Apply All Pending Migrations

To update your database to the latest schema:

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
alembic upgrade head
```

#### Check Current Migration Status

To see which migration version your database is currently at:

```bash
alembic current
```

#### View Migration History

To see all available migrations:

```bash
alembic history
```

### Creating New Migrations

When you modify database models, create a new migration:

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Example:
alembic revision --autogenerate -m "Add user roles table"
```

After creating a migration, always review the generated file in `alembic/versions/` before applying it.

### Rolling Back Migrations

If you need to rollback a migration:

```bash
# Rollback one revision
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

---

## Development Workflow

### Daily Development Routine

1. **Start Docker Services**
   ```bash
   docker-compose up -d
   ```

2. **Activate Python Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

3. **Run Database Migrations** (if new migrations exist)
   ```bash
   alembic upgrade head
   ```

4. **Start Backend Server**
   ```bash
   uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Start Frontend Server** (in separate terminal)
   ```bash
   cd frontend
   npm run dev
   ```

6. **Run Tests** (before committing)
   ```bash
   # Backend tests
   pytest tests/ -v

   # Frontend tests
   cd frontend
   npm test
   ```

### Git Workflow

Follow the branching strategy:

1. **Create Feature Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes and Commit**
   ```bash
   git add .
   git commit -m "feat: description of your changes"
   ```

3. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create PR on GitHub** targeting the `develop` branch

### Code Quality Checks

Before committing, run the following checks:

```bash
# Python linting (Ruff)
ruff check backend/

# Python formatting (Black)
black --check backend/

# Frontend linting (ESLint)
cd frontend
npm run lint

# Run all tests
pytest tests/ -v
cd frontend && npm test
```

---

## Testing

### Backend Testing

Run backend tests with pytest:

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=term-missing

# Run tests matching pattern
pytest tests/ -k "test_user" -v
```

### Frontend Testing

Run frontend tests with Vitest:

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

### Integration Testing

Run full integration tests:

```bash
# Ensure all services are running
docker-compose up -d

# Run integration tests
pytest tests/test_integration_full_flow.py -v
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Port 8000 already in use"

**Solution**: Kill the process using port 8000:

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn backend.api.main:app --reload --port 8001
```

#### Issue: "Cannot connect to database"

**Solution**: Verify PostgreSQL container is running:

```bash
# Check container status
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres

# Check logs for errors
docker-compose logs postgres
```

#### Issue: "ModuleNotFoundError: No module named 'backend'"

**Solution**: Ensure virtual environment is activated and dependencies are installed:

```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
```

#### Issue: "Alembic can't locate migration environment"

**Solution**: Ensure you're in the project root directory:

```bash
# Check current directory
pwd

# Should output: /path/to/voice-ai-testing

# If not, navigate to project root
cd /path/to/voice-ai-testing
```

#### Issue: "Redis connection refused"

**Solution**: Verify Redis container is running:

```bash
# Check Redis container
docker-compose ps redis

# Restart Redis
docker-compose restart redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

#### Issue: "Frontend can't reach backend API"

**Solution**: Check VITE_API_URL in frontend configuration:

```bash
# In frontend/.env
VITE_API_URL=http://localhost:8000/api
```

Ensure backend is running on port 8000.

#### Issue: "Docker containers won't start"

**Solution**: Check for port conflicts or disk space:

```bash
# Check running containers on same ports
docker ps

# Check disk space
df -h

# Stop all containers and restart
docker-compose down
docker-compose up -d
```

#### Issue: "Permission denied when accessing Docker"

**Solution**: Add your user to the docker group (Linux):

```bash
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo (not recommended for regular use)
sudo docker-compose up -d
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**:
   ```bash
   # Backend logs
   docker-compose logs backend

   # Frontend logs (in terminal where npm run dev is running)

   # Database logs
   docker-compose logs postgres
   ```

2. **Search existing GitHub issues**: Check if someone has encountered the same problem

3. **Ask in team Slack channel**: #voice-ai-testing-dev

4. **Create a GitHub issue**: Provide error messages, logs, and steps to reproduce

---

## Next Steps

Now that your development environment is set up:

1. **Review the Architecture**: Read `docs/architecture.md` to understand the system design

2. **Explore the API Documentation**: Visit http://localhost:8000/api/docs to see available endpoints

3. **Read the API Integration Guide**: See `docs/api-guide.md` for API usage examples

4. **Review Database Schema**: Check `docs/database-schema.md` for data model details

5. **Check the Project README**: `README.md` has overview and quick start guide

6. **Review Branching Strategy**: See `docs/branching-strategy.md` for Git workflow

7. **Start Development**: Pick a task from the project board and create a feature branch!

---

## Quick Reference

### Common Commands

```bash
# Start everything
docker-compose up -d
source venv/bin/activate
alembic upgrade head
uvicorn backend.api.main:app --reload

# Run tests
pytest tests/ -v
cd frontend && npm test

# Code quality
ruff check backend/
black backend/
cd frontend && npm run lint

# Database
alembic revision --autogenerate -m "message"
alembic upgrade head
alembic downgrade -1

# Docker
docker-compose up -d
docker-compose down
docker-compose logs -f
docker-compose ps

# Git
git checkout develop
git pull origin develop
git checkout -b feature/name
git add .
git commit -m "feat: message"
git push origin feature/name
```

### Important URLs

- Frontend: http://localhost:3000 or http://localhost:5173
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/api/docs
- API Docs (ReDoc): http://localhost:8000/api/redoc
- pgAdmin: http://localhost:5050 (admin@voiceai.com / admin)

---

**Happy Coding!** 🚀

If you have questions or need help, reach out to the team on Slack or create an issue on GitHub.
