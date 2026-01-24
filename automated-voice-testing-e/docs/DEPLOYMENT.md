# Voice AI Testing Framework - Deployment Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Configuration Reference](#configuration-reference)
- [Deployment Environments](#deployment-environments)
- [Health Checks](#health-checks)
- [Monitoring Setup](#monitoring-setup)
- [Deployment Procedures](#deployment-procedures)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Disk | 20 GB | 50 GB |

### Software Requirements

- **Docker**: v24.0+ and Docker Compose v2.20+
- **Python**: 3.12+
- **Node.js**: 18+ (for frontend)
- **Git**: 2.40+

### Installation

#### Docker Installation (Ubuntu)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

#### Python Setup
```bash
# Install Python 3.12
sudo apt-get update
sudo apt-get install python3.12 python3.12-venv python3.12-dev

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Environment Setup

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/your-org/voiceai-testing.git
cd voiceai-testing
```

2. **Copy environment template**
```bash
cp .env.example .env
```

3. **Start infrastructure services**
```bash
docker-compose up -d postgres redis rabbitmq
```

4. **Run database migrations**
```bash
source venv/bin/activate
alembic upgrade head
```

5. **Start the application**
```bash
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment File (.env)

Create a `.env` file with the following variables:

```bash
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/voiceai_testing
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Authentication
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Rate Limiting
RATE_LIMIT_DEFAULT_REQUESTS=100
RATE_LIMIT_DEFAULT_WINDOW=60

# External Services
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=admin

# Alerting
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
ALERT_EMAIL_TO=ops@example.com
```

---

## Configuration Reference

### Environment Variables

#### Core Application

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Environment name (development/staging/production) | development | Yes |
| `DEBUG` | Enable debug mode | false | No |
| `SECRET_KEY` | Application secret for signing | - | Yes |

#### Database Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `DB_POOL_SIZE` | Connection pool size | 20 | No |
| `DB_MAX_OVERFLOW` | Max overflow connections | 10 | No |
| `DB_POOL_TIMEOUT` | Connection timeout (seconds) | 30 | No |

#### Cache Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_URL` | Redis connection URL | redis://localhost:6379/0 | Yes |
| `CACHE_TTL` | Default cache TTL (seconds) | 3600 | No |

#### Authentication

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `JWT_SECRET_KEY` | Secret for JWT signing | - | Yes |
| `JWT_ALGORITHM` | JWT algorithm | HS256 | No |
| `JWT_EXPIRATION_MINUTES` | Token expiration | 30 | No |

#### Queue Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `RABBITMQ_URL` | RabbitMQ connection URL | - | Yes |
| `CELERY_BROKER_URL` | Celery broker URL | - | Yes |
| `CELERY_RESULT_BACKEND` | Celery result backend | - | No |

#### Monitoring & Alerting

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PROMETHEUS_ENABLED` | Enable Prometheus metrics | true | No |
| `SLACK_WEBHOOK_URL` | Slack webhook for alerts | - | No |
| `ALERT_EMAIL_TO` | Email for alerts | - | No |

---

## Deployment Environments

### Development

**Purpose**: Local development and testing

**Configuration**:
- Debug mode enabled
- Hot reload enabled
- Local database and Redis
- No external service dependencies

**Access**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050

### Staging

**Purpose**: Pre-production testing and validation

**Configuration**:
- Debug mode disabled
- Connects to staging database
- Uses staging AWS resources
- Alerting to staging Slack channel

**URL**: https://staging.voiceai.example.com

**Deployment Trigger**: Push to `develop` branch

### Production

**Purpose**: Live user-facing environment

**Configuration**:
- Debug mode disabled
- API documentation disabled
- Full monitoring and alerting
- Auto-scaling enabled
- Backup enabled

**URL**: https://voiceai.example.com

**Deployment Trigger**: Push to `main` branch (with approval)

---

## Health Checks

### Available Endpoints

#### Basic Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Readiness Check
```bash
GET /ready
```

Checks:
- Database connectivity
- Redis connectivity
- RabbitMQ connectivity

Response:
```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "rabbitmq": "ok"
  }
}
```

#### Liveness Check
```bash
GET /live
```

Response:
```json
{
  "status": "alive",
  "uptime": 3600
}
```

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

### ECS Health Checks

```json
{
  "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
  "interval": 30,
  "timeout": 5,
  "retries": 3,
  "startPeriod": 60
}
```

---

## Monitoring Setup

### Prometheus

Prometheus collects metrics from all services.

**Access**: http://localhost:9090

**Configuration**: `infrastructure/prometheus/prometheus.yml`

**Metrics Endpoint**: `/metrics` (port 8000)

#### Key Metrics

| Metric | Description |
|--------|-------------|
| `http_requests_total` | Total HTTP requests |
| `http_request_duration_seconds` | Request latency |
| `db_query_duration_seconds` | Database query time |
| `cache_hits_total` | Cache hit count |
| `queue_depth` | Message queue depth |

### Grafana

Grafana provides dashboards and visualization.

**Access**: http://localhost:3000

**Default Credentials**: admin / admin

**Pre-configured Dashboards**:
- Voice AI Overview
- API Performance
- Database Metrics
- Infrastructure

### Alertmanager

Alertmanager handles alert routing and notifications.

**Access**: http://localhost:9093

**Configuration**: `infrastructure/alertmanager/alertmanager.yml`

**Alert Routing**:
- Critical alerts → PagerDuty + Slack #critical
- Warning alerts → Slack #warnings
- Database alerts → DBA team
- Queue alerts → Backend team

### Exporters

| Service | Exporter | Port |
|---------|----------|------|
| PostgreSQL | postgres-exporter | 9187 |
| Redis | redis-exporter | 9121 |
| RabbitMQ | rabbitmq-exporter | 9419 |
| Nginx | nginx-exporter | 9113 |

---

## Deployment Procedures

### Standard Deployment

#### Step 1: Pre-deployment Checks

```bash
# Run tests
venv/bin/pytest tests/ -v

# Check for pending migrations
alembic check

# Validate configuration
python scripts/validate_env.py
```

#### Step 2: Database Migration

```bash
# Backup database first
./scripts/backup/postgres_backup.sh

# Run migrations
alembic upgrade head
```

#### Step 3: Deploy Application

**Via GitHub Actions** (Recommended):
- Push to `develop` → Deploys to staging
- Push to `main` → Deploys to production (with approval)

**Manual Deployment**:
```bash
# Build and push images
docker build -t voiceai-backend:latest .
docker push ecr.aws/voiceai-backend:latest

# Update ECS service
aws ecs update-service --cluster voiceai-cluster --service backend --force-new-deployment
```

#### Step 4: Post-deployment Verification

```bash
# Health check
curl https://api.voiceai.example.com/health

# Smoke tests
./scripts/smoke_test.sh
```

### Database Migration Deployment

1. **Backup the database**
```bash
./scripts/backup/postgres_backup.sh
```

2. **Run migration dry-run**
```bash
alembic check
```

3. **Apply migration**
```bash
alembic upgrade head
```

4. **Verify migration**
```bash
alembic current
```

### Rollback Procedure

#### Application Rollback

```bash
# Get previous task definition
PREV_TASK=$(aws ecs list-task-definitions --family-prefix voiceai-backend --sort DESC --query 'taskDefinitionArns[1]' --output text)

# Update service to previous version
aws ecs update-service --cluster voiceai-cluster --service backend --task-definition $PREV_TASK
```

#### Database Rollback

```bash
# Downgrade one revision
alembic downgrade -1

# Or downgrade to specific revision
alembic downgrade <revision_id>
```

#### Full Rollback

1. Rollback application to previous version
2. Rollback database migration
3. Verify system health
4. Notify stakeholders

### Blue-Green Deployment

1. **Deploy to green environment**
```bash
aws ecs update-service --cluster voiceai-cluster --service backend-green --task-definition new-version
```

2. **Run smoke tests on green**
```bash
./scripts/smoke_test.sh https://green.voiceai.example.com
```

3. **Switch traffic to green**
```bash
aws elbv2 modify-listener --listener-arn $LISTENER_ARN --default-actions Type=forward,TargetGroupArn=$GREEN_TARGET_GROUP
```

4. **Monitor for issues**

5. **Decommission blue** (after stability period)

---

## Troubleshooting

### Common Issues

#### Database Connection Failed

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres pg_isready

# Check logs
docker-compose logs postgres
```

#### Redis Connection Failed

```bash
# Check Redis is running
docker-compose exec redis redis-cli ping

# Check memory usage
docker-compose exec redis redis-cli info memory
```

#### Migration Failed

```bash
# Check current revision
alembic current

# View migration history
alembic history

# Rollback and retry
alembic downgrade -1
alembic upgrade head
```

#### Application Won't Start

```bash
# Check logs
docker-compose logs backend

# Verify environment variables
python scripts/validate_env.py

# Check port availability
netstat -tlnp | grep 8000
```

### Debug Mode

Enable debug mode for detailed error messages:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
uvicorn backend.api.main:app --reload --log-level debug
```

### Log Locations

| Service | Location |
|---------|----------|
| Backend | `docker-compose logs backend` |
| PostgreSQL | `docker-compose logs postgres` |
| Redis | `docker-compose logs redis` |
| Nginx | `/var/log/nginx/` |

---

## Security Considerations

### Secrets Management

- Never commit secrets to version control
- Use environment variables or secret managers
- Rotate secrets regularly (see docs/RUNBOOKS.md)

### Network Security

- Use TLS for all external communications
- Restrict database access to application servers only
- Use security groups/firewalls to limit access

### Access Control

- Implement role-based access control (RBAC)
- Use strong authentication (JWT with short expiration)
- Audit all administrative actions

---

## Support

For deployment issues:
1. Check this documentation
2. Review docs/RUNBOOKS.md for operational procedures
3. Contact the infrastructure team at infra@voiceai-testing.local
