# Voice AI Testing Framework - Disaster Recovery Plan

## Overview

This document defines the disaster recovery (DR) procedures for the Voice AI Testing Framework, including Recovery Time Objectives (RTO), Recovery Point Objectives (RPO), and step-by-step recovery procedures.

## Recovery Objectives

### RTO (Recovery Time Objective)

| Service | RTO | Priority |
|---------|-----|----------|
| Database (PostgreSQL) | 30 minutes | Critical |
| Cache (Redis) | 15 minutes | High |
| Object Storage (MinIO) | 1 hour | Medium |
| Backend API | 15 minutes | Critical |
| Frontend | 15 minutes | High |
| Message Queue (RabbitMQ) | 30 minutes | High |

### RPO (Recovery Point Objective)

| Service | RPO | Backup Frequency |
|---------|-----|------------------|
| Database (PostgreSQL) | 24 hours | Daily at 2:00 AM |
| Cache (Redis) | 24 hours | Daily at 2:30 AM |
| Object Storage (MinIO) | 24 hours | Daily at 3:00 AM |

## Disaster Scenarios

### Scenario 1: Single Service Failure

**Symptoms**: One container/service is unhealthy or crashed

**Recovery Steps**:
1. Check service logs: `docker logs voiceai-<service>`
2. Restart service: `docker-compose restart <service>`
3. Verify healthcheck: `docker-compose ps`
4. If persistent, check resource limits and disk space

**Estimated Time**: 5-15 minutes

### Scenario 2: Database Corruption/Loss

**Symptoms**: Database unavailable, data integrity issues

**Recovery Steps**:

1. **Stop dependent services**:
   ```bash
   docker-compose stop backend celery-worker
   ```

2. **List available backups**:
   ```bash
   ./scripts/backup/postgres_restore.sh
   ```

3. **Select and restore backup**:
   ```bash
   ./scripts/backup/postgres_restore.sh voiceai_testing_YYYYMMDD_HHMMSS.sql.gz
   ```

4. **Run migrations** (if schema changed):
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Restart services**:
   ```bash
   docker-compose start backend celery-worker
   ```

6. **Verify data integrity**:
   ```bash
   docker-compose exec backend python -c "from api.database import test_connection; test_connection()"
   ```

**Estimated Time**: 30-45 minutes

### Scenario 3: Complete Infrastructure Loss

**Symptoms**: All services down, need full rebuild

**Recovery Steps**:

1. **Provision new infrastructure**:
   - Deploy new VM/instances
   - Install Docker and Docker Compose
   - Clone repository

2. **Restore environment configuration**:
   ```bash
   cp /path/to/backup/.env .env
   ```

3. **Pull latest images**:
   ```bash
   docker-compose pull
   ```

4. **Start infrastructure services first**:
   ```bash
   docker-compose up -d postgres redis rabbitmq minio
   ```

5. **Wait for services to be healthy**:
   ```bash
   docker-compose ps
   ```

6. **Restore database from backup**:
   ```bash
   ./scripts/backup/postgres_restore.sh <latest_backup>
   ```

7. **Restore MinIO data**:
   ```bash
   # Mirror from backup location
   mc mirror backup/voice-ai-testing-backups/minio/ myminio/
   ```

8. **Start application services**:
   ```bash
   docker-compose up -d
   ```

9. **Verify all services**:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost/health
   ```

**Estimated Time**: 1-2 hours

### Scenario 4: Redis Cache Loss

**Symptoms**: Cache miss rate 100%, sessions lost

**Recovery Steps**:

1. **Stop Redis container**:
   ```bash
   docker-compose stop redis
   ```

2. **Remove corrupted data**:
   ```bash
   docker-compose rm -v redis
   ```

3. **Restore from backup** (optional):
   ```bash
   # Download backup
   mc cp backup/voice-ai-testing-backups/redis/<backup>.rdb.gz /tmp/
   gunzip /tmp/<backup>.rdb.gz

   # Place in Redis data directory
   mv /tmp/<backup>.rdb ./redis_data/dump.rdb
   ```

4. **Start Redis**:
   ```bash
   docker-compose up -d redis
   ```

5. **Application will rebuild cache on demand**

**Estimated Time**: 15-30 minutes

## Backup Verification

### Daily Verification (Automated)

The backup verification script runs weekly:
```bash
./scripts/backup/verify_backups.sh
```

Checks:
- Backup file exists and not empty
- Backup file can be decompressed
- SQL syntax is valid (dry run)

### Monthly Verification (Manual)

1. Spin up test environment
2. Restore latest backup
3. Run test suite against restored data
4. Compare key metrics with production

## Communication Plan

### Incident Response

1. **Detect**: Monitoring alerts via Alertmanager
2. **Assess**: Determine severity and impact
3. **Communicate**: Notify stakeholders via Slack (#voiceai-incidents)
4. **Recover**: Follow appropriate recovery procedure
5. **Post-mortem**: Document incident and lessons learned

### Stakeholder Contacts

| Role | Contact | When to Notify |
|------|---------|----------------|
| On-call Engineer | oncall@voiceai-testing.local | All incidents |
| Engineering Lead | eng-lead@voiceai-testing.local | P1/P2 incidents |
| Product Owner | po@voiceai-testing.local | Customer-impacting incidents |

## Testing Schedule

### Quarterly DR Tests

1. **Q1**: Database restore test
2. **Q2**: Full infrastructure rebuild test
3. **Q3**: Service failover test
4. **Q4**: Complete DR simulation

### Test Procedure

1. Schedule maintenance window
2. Notify stakeholders
3. Create test environment
4. Execute recovery procedures
5. Document results and timings
6. Update runbooks if needed
7. Report to management

## Monitoring and Alerting

DR-related alerts configured in Alertmanager:

- `PostgresDown`: Database unavailable
- `HighQueueDepth`: Message backlog building
- `BackupFailed`: Nightly backup did not complete
- `DiskSpaceLow`: Less than 20% disk remaining

## Appendix

### Useful Commands

```bash
# Check all service health
docker-compose ps

# View service logs
docker-compose logs -f --tail=100 <service>

# Force recreate service
docker-compose up -d --force-recreate <service>

# Enter container shell
docker-compose exec <service> /bin/sh

# Database connection test
docker-compose exec postgres psql -U postgres -c "SELECT 1;"

# Redis connection test
docker-compose exec redis redis-cli ping

# List backups
mc ls backup/voice-ai-testing-backups/postgres/
```

### Recovery Contacts

- **Infrastructure Issues**: infra@voiceai-testing.local
- **Database Issues**: dba@voiceai-testing.local
- **Application Issues**: backend@voiceai-testing.local
