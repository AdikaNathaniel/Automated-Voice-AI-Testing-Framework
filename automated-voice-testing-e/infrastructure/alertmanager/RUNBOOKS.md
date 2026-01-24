# Voice AI Testing Framework - Alert Runbooks

This document provides response procedures for each alert configured in the system.

## Table of Contents
- [Critical Alerts](#critical-alerts)
- [Warning Alerts](#warning-alerts)
- [Database Alerts](#database-alerts)
- [Queue Alerts](#queue-alerts)

---

## Critical Alerts

### LowSuccessRate

**Severity**: Critical
**Alert Condition**: Test success rate < 95% for 5 minutes

**Impact**: Test quality degradation, potential missed regressions

**Investigation Steps**:
1. Check Grafana dashboard for recent test failures
2. Review failed test logs: `docker logs voiceai-backend --tail 1000 | grep ERROR`
3. Check for infrastructure issues (database, Redis connectivity)
4. Review recent code deployments

**Resolution**:
1. If infrastructure issue: Restart affected service
2. If code regression: Roll back to previous deployment
3. If test data issue: Validate test case configurations

**Escalation**: If unresolved after 15 minutes, escalate to on-call engineer

---

### HighQueueDepth

**Severity**: Critical
**Alert Condition**: Queue depth > 1000 jobs for 2 minutes

**Impact**: Test execution delays, potential job timeouts

**Investigation Steps**:
1. Check worker status: `docker ps | grep worker`
2. Check RabbitMQ management UI: http://localhost:15672
3. Review worker logs: `docker logs voiceai-celery-worker --tail 500`
4. Check for stuck or long-running tasks

**Resolution**:
1. Scale up workers: `docker-compose up -d --scale celery-worker=5`
2. Clear stuck jobs if necessary
3. Increase worker concurrency in settings
4. Investigate and fix slow-running tasks

**Escalation**: If queue depth continues rising after scaling, escalate immediately

---

### HighResponseLatency

**Severity**: Critical
**Alert Condition**: API P95 latency > 5 seconds for 5 minutes

**Impact**: Poor user experience, potential timeouts

**Investigation Steps**:
1. Check backend logs for slow queries
2. Review database performance: `SELECT * FROM pg_stat_activity;`
3. Check Redis latency: `redis-cli --latency`
4. Review recent deployments for performance regressions

**Resolution**:
1. Restart backend if memory leak suspected
2. Add database indexes for slow queries
3. Scale backend instances
4. Enable query caching

**Escalation**: If latency not reduced within 10 minutes, escalate to backend team

---

## Warning Alerts

### HighMemoryUsage

**Severity**: Warning
**Alert Condition**: Memory usage > 80% for 5 minutes

**Impact**: Potential OOM kills, service degradation

**Investigation Steps**:
1. Check container memory: `docker stats`
2. Identify memory-intensive processes
3. Review for memory leaks in recent code

**Resolution**:
1. Restart affected container
2. Increase memory limits in docker-compose
3. Fix memory leaks in code
4. Add memory profiling for persistent issues

---

### HighCPUUsage

**Severity**: Warning
**Alert Condition**: CPU usage > 80% for 5 minutes

**Impact**: Slow response times, degraded performance

**Investigation Steps**:
1. Check container CPU: `docker stats`
2. Review active processes: `top -c`
3. Check for CPU-intensive operations

**Resolution**:
1. Scale horizontal if load is legitimate
2. Optimize CPU-intensive code paths
3. Add caching for expensive computations

---

## Database Alerts

### PostgresDown

**Severity**: Critical
**Alert Condition**: PostgreSQL not responding

**Impact**: Complete application failure

**Investigation Steps**:
1. Check container status: `docker ps | grep postgres`
2. Check disk space: `df -h`
3. Review postgres logs: `docker logs voiceai-postgres --tail 500`
4. Check for connection limits

**Resolution**:
1. Restart PostgreSQL: `docker-compose restart postgres`
2. Free disk space if needed
3. Increase max_connections if connection limit reached
4. Restore from backup if data corruption

**Escalation**: Immediate escalation to DBA

---

### HighDatabaseConnections

**Severity**: Warning
**Alert Condition**: Connection count > 80% of max_connections

**Impact**: New connections may fail

**Investigation Steps**:
1. Check active connections: `SELECT count(*) FROM pg_stat_activity;`
2. Identify connection leaks
3. Review connection pool settings

**Resolution**:
1. Kill idle connections: `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle';`
2. Fix connection leak in application code
3. Increase max_connections (requires restart)
4. Implement connection pooling (PgBouncer)

---

### SlowQueries

**Severity**: Warning
**Alert Condition**: Queries taking > 1 second

**Impact**: Degraded application performance

**Investigation Steps**:
1. Enable query logging: `ALTER SYSTEM SET log_min_duration_statement = 1000;`
2. Review slow query log
3. Use EXPLAIN ANALYZE on slow queries

**Resolution**:
1. Add indexes for slow queries
2. Optimize query structure
3. Add query caching
4. Partition large tables

---

## Queue Alerts

### WorkerDown

**Severity**: Critical
**Alert Condition**: No workers responding

**Impact**: Test execution stopped

**Investigation Steps**:
1. Check worker containers: `docker ps | grep worker`
2. Review worker logs for errors
3. Check RabbitMQ connectivity

**Resolution**:
1. Restart workers: `docker-compose restart celery-worker`
2. Fix RabbitMQ connectivity issues
3. Scale workers if crashed due to load

---

### TaskFailureRate

**Severity**: Warning
**Alert Condition**: Task failure rate > 10%

**Impact**: Incomplete test executions

**Investigation Steps**:
1. Check task error logs
2. Review failed task types
3. Check external service availability

**Resolution**:
1. Fix task-specific errors
2. Retry failed tasks: `celery -A tasks inspect scheduled`
3. Implement better error handling

---

## General Troubleshooting

### Common Commands

```bash
# Check all container status
docker-compose ps

# View logs for a service
docker-compose logs -f <service-name>

# Restart a service
docker-compose restart <service-name>

# Scale workers
docker-compose up -d --scale celery-worker=N

# Check network connectivity
docker-compose exec backend ping postgres

# Database connection test
docker-compose exec postgres psql -U postgres -c "SELECT 1;"

# Redis connectivity test
docker-compose exec redis redis-cli ping
```

### Emergency Contacts

- **On-call Engineer**: oncall@voiceai-testing.local
- **DBA Team**: dba@voiceai-testing.local
- **Infrastructure Team**: infra@voiceai-testing.local

### Useful Links

- Grafana Dashboard: http://localhost:3000
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093
- RabbitMQ Management: http://localhost:15672

---

## Alert Acknowledgement

When an alert fires:
1. Acknowledge in Alertmanager UI
2. Create incident ticket
3. Follow runbook steps
4. Update ticket with findings
5. Resolve or escalate within SLA

**SLA Targets**:
- Critical: Acknowledge within 5 minutes, resolve within 30 minutes
- Warning: Acknowledge within 15 minutes, resolve within 2 hours
