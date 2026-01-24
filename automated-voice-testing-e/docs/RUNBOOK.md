# Operations Runbook

This runbook provides step-by-step procedures for common operational tasks in the Voice AI Automated Testing Framework.

## Table of Contents

1. [Restarting Services](#restarting-services)
2. [Rotating SoundHound Credentials](#rotating-soundhound-credentials)
3. [Investigating Failed Test Runs](#investigating-failed-test-runs)
4. [Monitoring Queue Depth](#monitoring-queue-depth)
5. [Escalation Contacts](#escalation-contacts)

---

## Restarting Services

### Restart All Services

To restart all services using Docker Compose:

```bash
# Stop and restart all services
docker-compose restart

# Or for a full restart (stop, remove, recreate)
docker-compose down
docker-compose up -d
```

### Restart Individual Services

To restart specific services:

```bash
# Restart backend only
docker-compose restart backend

# Restart frontend only
docker-compose restart frontend

# Restart PostgreSQL database
docker-compose restart postgres

# Restart Redis cache
docker-compose restart redis

# Restart RabbitMQ message broker
docker-compose restart rabbitmq

# Restart Prometheus monitoring
docker-compose restart prometheus

# Restart Grafana dashboards
docker-compose restart grafana
```

### Health Check Verification

After restarting services, verify health status:

```bash
# Check all service status
docker-compose ps

# Check health of specific service
docker inspect --format='{{.State.Health.Status}}' voiceai-backend

# Verify backend API health endpoint
curl -f http://localhost:8000/health

# Check PostgreSQL connection
docker-compose exec postgres pg_isready -U postgres

# Check Redis connection
docker-compose exec redis redis-cli ping
```

### Common Restart Scenarios

**Backend not responding:**
```bash
# Check backend logs first
docker-compose logs --tail=100 backend

# Restart backend service
docker-compose restart backend

# Wait for health check to pass
sleep 30
curl http://localhost:8000/health
```

**Database connection issues:**
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Wait for PostgreSQL to be ready
until docker-compose exec postgres pg_isready -U postgres; do sleep 1; done

# Then restart backend to reconnect
docker-compose restart backend
```

---

## Rotating SoundHound Credentials

### Overview

SoundHound/Houndify API credentials should be rotated quarterly or when compromised.

### Rotation Procedure

1. **Obtain new credentials** from SoundHound developer portal

2. **Update environment variables** in deployment:

   For Docker Compose (development):
   ```bash
   # Edit .env file
   nano .env

   # Update these variables
   SOUNDHOUND_API_KEY=new-api-key-here
   SOUNDHOUND_CLIENT_ID=new-client-id-here
   ```

   For Kubernetes (production):
   ```bash
   # Update secret
   kubectl create secret generic soundhound-credentials \
     --from-literal=api-key=new-api-key \
     --from-literal=client-id=new-client-id \
     --dry-run=client -o yaml | kubectl apply -f -
   ```

3. **Restart affected services** to pick up new credentials:

   ```bash
   # Restart backend to use new credentials
   docker-compose restart backend

   # For Kubernetes
   kubectl rollout restart deployment/backend
   ```

4. **Verify the new credentials work:**

   ```bash
   # Check backend logs for successful Houndify connection
   docker-compose logs --tail=50 backend | grep -i houndify

   # Run a test to verify API connectivity
   curl -X POST http://localhost:8000/api/v1/test-runs/quick-test
   ```

5. **Revoke old credentials** in SoundHound portal after verification

### Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `SOUNDHOUND_API_KEY` | API key for Houndify service |
| `SOUNDHOUND_CLIENT_ID` | Client ID for Houndify service |
| `SOUNDHOUND_ENDPOINT` | Houndify API endpoint URL |

---

## Investigating Failed Test Runs

### Initial Triage

1. **Check recent test run status:**

   ```bash
   # View recent test runs via API
   curl http://localhost:8000/api/v1/test-runs?status=failed&limit=10

   # Or check in database
   docker-compose exec postgres psql -U postgres -d voiceai_testing -c \
     "SELECT id, name, status, created_at FROM test_runs WHERE status = 'failed' ORDER BY created_at DESC LIMIT 10;"
   ```

2. **Check application logs:**

   ```bash
   # Backend logs for errors
   docker-compose logs --tail=200 backend | grep -i error

   # Filter for specific test run
   docker-compose logs backend | grep "test_run_id=YOUR_TEST_RUN_ID"
   ```

### Common Failure Patterns

**Timeout failures:**
```bash
# Check for timeout patterns in logs
docker-compose logs backend | grep -i timeout

# Common causes:
# - Slow SoundHound API responses
# - Database connection pool exhaustion
# - Network issues
```

**Validation failures:**
```bash
# Check validation service logs
docker-compose logs backend | grep -i "validation"

# Review low confidence scores
docker-compose exec postgres psql -U postgres -d voiceai_testing -c \
  "SELECT * FROM validation_results WHERE confidence_score < 0.5 ORDER BY created_at DESC LIMIT 20;"
```

**Database errors:**
```bash
# Check for database connection errors
docker-compose logs backend | grep -i "database\|postgres\|sqlalchemy"

# Verify database connectivity
docker-compose exec postgres pg_isready -U postgres
```

### Metrics and Grafana Dashboards

1. **Access Grafana** at http://localhost:3000

2. **Check key dashboards:**
   - System Overview: Overall health metrics
   - Performance: Response times and throughput
   - Quality: Test pass rates and validation accuracy

3. **Check Prometheus** directly at http://localhost:9090:

   ```promql
   # Failed test executions in last hour
   sum(rate(test_executions_total{result="failure"}[1h]))

   # Success rate
   sum(rate(test_executions_total{result="success"}[5m])) / sum(rate(test_executions_total[5m]))
   ```

---

## Monitoring Queue Depth

### Understanding Queue Depth

Queue depth indicates the number of pending test execution jobs. High queue depth can indicate:
- Worker capacity issues
- Slow test execution
- External API bottlenecks

### Checking Queue Depth

1. **Via Prometheus metrics:**

   ```bash
   curl -s http://localhost:9090/api/v1/query?query=queue_depth | jq .
   ```

2. **Via RabbitMQ Management:**

   - Access http://localhost:15672
   - Login: rabbitmq/rabbitmq
   - Check queue lengths in "Queues" tab

3. **Via application logs:**

   ```bash
   docker-compose logs backend | grep -i "queue"
   ```

### Responding to High Queue Depth

**If queue_depth > 1000 for > 2 minutes:**

1. **Check worker status:**
   ```bash
   # Celery worker status
   docker-compose exec backend celery -A celery_app inspect active
   ```

2. **Scale workers (if possible):**
   ```bash
   # Scale Celery workers
   docker-compose up -d --scale celery-worker=4
   ```

3. **Check for stuck jobs:**
   ```bash
   # View active tasks
   docker-compose exec backend celery -A celery_app inspect active

   # Purge queue if necessary (CAUTION: loses all pending jobs)
   docker-compose exec backend celery -A celery_app purge
   ```

4. **Check external dependencies:**
   ```bash
   # SoundHound API latency
   docker-compose logs backend | grep -i "houndify.*latency"

   # Database connection pool
   docker-compose logs backend | grep -i "pool.*exhausted"
   ```

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| queue_depth | > 500 | > 1000 |
| Duration at threshold | > 5m | > 2m |

---

## Escalation Contacts

### On-Call Support

For urgent issues during business hours:
- **Primary Contact**: Platform Team Lead
- **Email**: platform-support@productiveplayhouse.com
- **Slack**: #platform-oncall

### Escalation Matrix

| Severity | Response Time | Contact |
|----------|---------------|---------|
| Critical (P1) | 15 minutes | Platform Team Lead |
| High (P2) | 1 hour | Platform Engineer |
| Medium (P3) | 4 hours | Platform Engineer |
| Low (P4) | Next business day | Platform Team |

### External Support

- **SoundHound Support**: support@soundhound.com
- **AWS Support**: (for cloud deployments)

---

## Appendix: Quick Reference Commands

```bash
# Service Status
docker-compose ps

# View Logs
docker-compose logs -f --tail=100 [service]

# Restart Service
docker-compose restart [service]

# Check Health
curl http://localhost:8000/health

# Database Query
docker-compose exec postgres psql -U postgres -d voiceai_testing

# Redis CLI
docker-compose exec redis redis-cli

# RabbitMQ Status
docker-compose exec rabbitmq rabbitmqctl status
```
