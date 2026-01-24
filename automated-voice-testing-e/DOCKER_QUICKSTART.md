# Docker Quick Start Guide

This guide shows you how to run the entire Voice AI Testing Platform with Docker Compose.

## What Happens Automatically

When you start the services with Docker Compose, the following happens automatically:

### 🔄 Backend Startup Process
1. **Database Migrations**: Alembic runs all database migrations (`alembic upgrade head`)
2. **Test Data Seeding**: Seeds the database with test users and sample data
3. **API Server**: Starts FastAPI server on port 8000
4. **WebSocket Server**: Socket.IO server starts for real-time updates

### 💾 Persistent Data
All data is stored in Docker volumes and persists across container restarts:
- `postgres_data`: Database tables and user data
- `redis_data`: Cache and session data
- `rabbitmq_data`: Message queue data
- `minio_data`: S3-compatible object storage for audio files
- `grafana_data`: Monitoring dashboards
- `prometheus_data`: Metrics time-series data

## Quick Start

### 1. Start All Services

```bash
docker-compose up -d
```

This starts:
- ✅ PostgreSQL (port 5433)
- ✅ Redis (port 6379)
- ✅ RabbitMQ (port 5672, UI: 15672)
- ✅ Backend API (port 8000)
- ✅ Frontend (port 3001)
- ✅ Nginx (ports 80, 443)
- ✅ MinIO S3 Storage (port 9000, UI: 9001)
- ✅ Prometheus (port 9090)
- ✅ Grafana (port 3000)
- ✅ Alertmanager (port 9093)

### 2. Wait for Backend to Initialize

The backend will automatically:
- Wait for PostgreSQL to be ready
- Run database migrations
- Seed test data
- Start the API server

Watch the logs:
```bash
docker-compose logs -f backend
```

You'll see:
```
🚀 Starting backend entrypoint...
⏳ Waiting for PostgreSQL to be ready...
✅ PostgreSQL is ready!
🔄 Running database migrations...
✅ Migrations completed!
🌱 Seeding test data...
✅ Test data seeded!
🎯 Starting FastAPI application...
```

### 3. Access the Application

**Frontend**: http://localhost:3001

**Test Login Credentials**:
The system automatically seeds test users on startup:
- **Admin**: `admin@voiceai.com` / `admin123`
- **Developer**: `dev1@voiceai.com` / `dev123`
- **Tester**: `tester1@voiceai.com` / `test123`

**API Documentation**: http://localhost:8000/docs

**Other Services**:
- RabbitMQ Management UI: http://localhost:15672 (rabbitmq/rabbitmq)
- MinIO Console: http://localhost:9001 (minio_user/changeme_minio_s3)
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (grafana_admin/changeme_grafana_*)
- Alertmanager: http://localhost:9093

## Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Restart Services
```bash
# Restart specific service
docker-compose restart backend

# Restart all services
docker-compose restart
```

### Stop Services
```bash
# Stop but keep data
docker-compose stop

# Stop and remove containers (data persists in volumes)
docker-compose down

# Stop and remove containers AND volumes (deletes all data!)
docker-compose down -v
```

### Rebuild After Code Changes
```bash
# Rebuild backend
docker-compose build backend

# Rebuild and restart backend
docker-compose up -d --build backend

# Rebuild all services
docker-compose up -d --build
```

### Check Service Status
```bash
docker-compose ps
```

### Access Container Shell
```bash
# Backend shell
docker-compose exec backend bash

# Database shell
docker-compose exec postgres psql -U postgres -d voiceai_testing
```

## Environment Variables

### Disable Auto-Seeding

If you don't want test data seeded automatically, set in `docker-compose.yml`:

```yaml
environment:
  SEED_DATA: "false"
```

### Custom Database Credentials

Edit `docker-compose.yml`:

```yaml
environment:
  POSTGRES_USER: myuser
  POSTGRES_PASSWORD: mypassword
  POSTGRES_DB: mydb
```

## Troubleshooting

### Backend Won't Start

**Check logs**:
```bash
docker-compose logs backend
```

**Common issues**:
- Database not ready: Wait a few more seconds
- Port conflict: Another service using port 8000
- Migration error: Check migration files in `alembic/versions/`

### Database Connection Errors

**Verify PostgreSQL is running**:
```bash
docker-compose ps postgres
```

**Check health**:
```bash
docker-compose exec postgres pg_isready -U postgres
```

### Fresh Database Reset

```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm automated-voice-testing_postgres_data

# Start services (database will be recreated and seeded)
docker-compose up -d
```

### View All Volumes
```bash
docker volume ls | grep automated-voice-testing
```

## Development Mode with pgAdmin

Start with development profile to access pgAdmin:

```bash
docker-compose --profile dev up -d
```

Access pgAdmin at http://localhost:5050 (pgadmin@voiceai.local/changeme_pgadmin)

## Production Deployment

For production, remove or comment out:
- pgAdmin service
- Change all default passwords in `.env` file
- Set `SEED_DATA: "false"`
- Configure proper SSL certificates with Certbot

## Architecture

```
┌─────────────┐     ┌──────────┐     ┌─────────────┐
│  Frontend   │────▶│  Nginx   │────▶│   Backend   │
│  (React)    │     │ (Proxy)  │     │  (FastAPI)  │
│  Port 3001  │     │ Port 80  │     │  Port 8000  │
└─────────────┘     └──────────┘     └─────────────┘
                                             │
                            ┌────────────────┼────────────────┐
                            ▼                ▼                ▼
                     ┌──────────┐    ┌──────────┐    ┌──────────┐
                     │PostgreSQL│    │  Redis   │    │ RabbitMQ │
                     │Port 5433 │    │Port 6379 │    │Port 5672 │
                     └──────────┘    └──────────┘    └──────────┘
```

## Next Steps

1. **Login**: Use test credentials at http://localhost:3001
2. **Explore API**: Visit http://localhost:8000/docs
3. **Monitor**: Check Grafana at http://localhost:3000
4. **Check Logs**: `docker-compose logs -f backend`

Enjoy your automated testing platform! 🚀
