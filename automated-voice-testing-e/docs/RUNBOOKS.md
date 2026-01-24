# Voice AI Testing Framework - Operational Runbooks

## Table of Contents
- [Incident Response](#incident-response)
- [Troubleshooting Guides](#troubleshooting-guides)
- [Performance Tuning](#performance-tuning)
- [Secret Rotation](#secret-rotation)

---

## Incident Response

### Incident Classification

| Severity | Definition | Response Time | Example |
|----------|------------|---------------|---------|
| P1 - Critical | Service completely down | 5 minutes | Database unavailable |
| P2 - High | Major feature broken | 15 minutes | Test execution failing |
| P3 - Medium | Degraded performance | 1 hour | High latency |
| P4 - Low | Minor issue | 24 hours | UI cosmetic issue |

### Incident Response Procedure

#### 1. Detection
- Alertmanager notifications via Slack/email
- User reports
- Monitoring dashboards

#### 2. Triage
```bash
# Check system status
docker-compose ps

# Check recent logs
docker-compose logs --tail=100 backend

# Check metrics
curl http://localhost:9090/api/v1/query?query=up
```

#### 3. Communication
- Acknowledge in #voiceai-incidents
- Update status page
- Notify stakeholders per severity

#### 4. Investigation
- Review logs and metrics
- Identify root cause
- Document findings

#### 5. Resolution
- Apply fix or workaround
- Verify resolution
- Update stakeholders

#### 6. Post-Mortem
- Document timeline
- Identify root cause
- List action items
- Update runbooks if needed

---

## Troubleshooting Guides

### Backend Service Issues

#### API Returns 500 Errors
```bash
# Check backend logs
docker-compose logs --tail=500 backend | grep -i error

# Check database connectivity
docker-compose exec backend python -c "from api.database import engine; print(engine.url)"

# Check Redis connectivity
docker-compose exec backend python -c "import redis; r = redis.from_url('redis://redis:6379'); print(r.ping())"

# Restart service
docker-compose restart backend
```

#### High Memory Usage
```bash
# Check container memory
docker stats --no-stream

# Identify memory-heavy processes
docker-compose exec backend ps aux --sort=-%mem | head

# Force garbage collection
docker-compose exec backend python -c "import gc; gc.collect()"

# Restart if needed
docker-compose restart backend
```

#### Slow API Responses
```bash
# Check database slow queries
docker-compose exec postgres psql -U postgres -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Check Redis latency
docker-compose exec redis redis-cli --latency

# Check backend CPU
docker stats --no-stream voiceai-backend

# Profile endpoint
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/test-cases/
```

### Database Issues

#### Connection Refused
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready

# Check container logs
docker-compose logs postgres

# Check disk space
docker-compose exec postgres df -h /var/lib/postgresql/data

# Restart PostgreSQL
docker-compose restart postgres
```

#### Too Many Connections
```bash
# Check current connections
docker-compose exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Identify connection sources
docker-compose exec postgres psql -U postgres -c "SELECT client_addr, count(*) FROM pg_stat_activity GROUP BY client_addr;"

# Kill idle connections
docker-compose exec postgres psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND query_start < now() - interval '10 minutes';"

# Increase max_connections (requires restart)
# Edit postgresql.conf and restart
```

#### Disk Space Full
```bash
# Check disk usage
docker-compose exec postgres df -h

# Clean old WAL files
docker-compose exec postgres psql -U postgres -c "SELECT pg_switch_wal();"

# Vacuum tables
docker-compose exec postgres psql -U postgres -d voiceai_testing -c "VACUUM FULL ANALYZE;"

# Delete old backups
find /backups -name "*.sql.gz" -mtime +30 -delete
```

### Redis Issues

#### Redis Not Responding
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis

# Check memory usage
docker-compose exec redis redis-cli info memory

# Restart Redis
docker-compose restart redis
```

#### Memory Full
```bash
# Check memory usage
docker-compose exec redis redis-cli info memory

# Evict old keys (if configured)
docker-compose exec redis redis-cli MEMORY PURGE

# Identify large keys
docker-compose exec redis redis-cli --bigkeys

# Clear specific patterns
docker-compose exec redis redis-cli KEYS "cache:*" | xargs redis-cli DEL
```

### Queue Issues

#### High Queue Backlog
```bash
# Check queue depth
docker-compose exec rabbitmq rabbitmqctl list_queues name messages

# Check consumer count
docker-compose exec rabbitmq rabbitmqctl list_consumers

# Scale workers
docker-compose up -d --scale celery-worker=5

# Purge stuck queue (caution!)
docker-compose exec rabbitmq rabbitmqctl purge_queue <queue-name>
```

#### Workers Not Processing
```bash
# Check worker status
docker-compose logs celery-worker

# Check RabbitMQ connectivity
docker-compose exec celery-worker python -c "import pika; pika.BlockingConnection()"

# Restart workers
docker-compose restart celery-worker
```

---

## Performance Tuning

### Database Optimization

#### Connection Pool Tuning
```python
# In settings or database.py
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 10
SQLALCHEMY_POOL_TIMEOUT = 30
```

#### Query Optimization
```sql
-- Find slow queries
SELECT query, calls, mean_time, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Add missing indexes
EXPLAIN ANALYZE SELECT * FROM test_cases WHERE status = 'active';
CREATE INDEX idx_test_cases_status ON test_cases(status);
```

#### Vacuum Schedule
```bash
# Manual vacuum
docker-compose exec postgres psql -U postgres -d voiceai_testing -c "VACUUM ANALYZE;"

# Configure autovacuum (postgresql.conf)
autovacuum_vacuum_cost_delay = 2ms
autovacuum_vacuum_cost_limit = 200
```

### Redis Optimization

#### Memory Configuration
```bash
# Set max memory
docker-compose exec redis redis-cli CONFIG SET maxmemory 1gb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

#### Persistence Tuning
```bash
# AOF fsync policy (in redis.conf)
# appendfsync everysec (balance)
# appendfsync always (durability)
# appendfsync no (performance)
```

### Application Tuning

#### Worker Configuration
```python
# Celery settings
CELERY_WORKER_CONCURRENCY = 4
CELERY_PREFETCH_MULTIPLIER = 4
CELERY_TASK_ACKS_LATE = True
```

#### API Rate Limiting
```bash
# Adjust in .env
RATE_LIMIT_DEFAULT_REQUESTS=200
RATE_LIMIT_DEFAULT_WINDOW=60
```

---

## Secret Rotation

### JWT Secret Rotation

**Impact**: All users will need to re-authenticate

```bash
# 1. Generate new secret
NEW_SECRET=$(openssl rand -base64 32)

# 2. Update .env file
sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$NEW_SECRET/" .env

# 3. Restart backend
docker-compose restart backend

# 4. Verify
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'
```

### Database Password Rotation

```bash
# 1. Update PostgreSQL password
docker-compose exec postgres psql -U postgres -c "ALTER USER postgres PASSWORD 'new_password';"

# 2. Update .env
sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=new_password/" .env

# 3. Update DATABASE_URL
sed -i "s/postgres:old_password@/postgres:new_password@/" .env

# 4. Restart services
docker-compose restart backend celery-worker
```

### AWS Credentials Rotation

```bash
# 1. Create new access key in AWS Console

# 2. Update .env
AWS_ACCESS_KEY_ID=new_key
AWS_SECRET_ACCESS_KEY=new_secret

# 3. Restart services using AWS
docker-compose restart backend

# 4. Delete old key in AWS Console

# 5. Verify
aws s3 ls
```

### Slack Webhook Rotation

```bash
# 1. Create new webhook in Slack App

# 2. Update .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/NEW/WEBHOOK/URL

# 3. Restart Alertmanager
docker-compose restart alertmanager

# 4. Test notification
curl -X POST $SLACK_WEBHOOK_URL -d '{"text": "Test notification"}'
```

### Rotation Schedule

| Secret | Frequency | Procedure |
|--------|-----------|-----------|
| JWT Secret | Quarterly | JWT rotation above |
| Database Passwords | Quarterly | DB rotation above |
| AWS Access Keys | Semi-annually | AWS rotation above |
| Webhook URLs | As needed | Slack rotation above |

---

## Emergency Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| On-call Engineer | oncall@voiceai-testing.local | All P1/P2 |
| DBA | dba@voiceai-testing.local | Database issues |
| Infrastructure | infra@voiceai-testing.local | Container/network issues |
| Security | security@voiceai-testing.local | Security incidents |

---

## Quick Reference

### Common Commands

```bash
# Service status
docker-compose ps

# View logs
docker-compose logs -f <service>

# Restart service
docker-compose restart <service>

# Enter container
docker-compose exec <service> sh

# Database shell
docker-compose exec postgres psql -U postgres -d voiceai_testing

# Redis CLI
docker-compose exec redis redis-cli

# RabbitMQ status
docker-compose exec rabbitmq rabbitmqctl status
```

### Important URLs

- API Docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Alertmanager: http://localhost:9093
- RabbitMQ Management: http://localhost:15672
