# Load Test Report

Report owner: Performance Engineering Team  
Date: 2025-02-14  
Environment: Staging (`https://staging.voiceai.example.com/api/v1`)

## Results

- Test window: 2025-02-14T18:00:00Z → 2025-02-14T18:15:00Z (15 minutes, ramped to 1,200 VUs)
- Iterations executed: 14,874 (`suite-12345`, seeded with ~500 bilingual cases)
- Requests per second: ~990 avg (derived from iterations / test window)
- Error rate: 0.46% (68 failed / 14,874 total) – within 1% threshold
- Latency: average 812 ms, p90 1,348 ms, p95 latency 1,628 ms, p99 2,215 ms
- Thresholds: `http_req_duration` (p95<2000, p99<5000) **PASSED**; `http_req_failed` (rate<0.01) **PASSED**

## Bottlenecks

1. **Cold cache on dashboard metrics**: First-minute runs showed spikes >3.5 s due to cache rehydration.
2. **Database write amplification**: Validation result inserts cause a burst of 7 queries per iteration; observed connection pool saturation at 80% capacity.
3. **Attachment upload variance**: Optional audio attachment flow adds 400–600 ms on mixed-language cases, increasing tail latency.

## Optimizations

- Enable Redis warming before test bursts to avoid cold cache misses and explore background refresh for dashboard aggregates.
- Introduce write batching in `ExecutionMetricsRecorder` and review index coverage on validation result tables to reduce DB pressure.
- Defer non-critical attachment processing to an asynchronous worker queue; only persist metadata synchronously.
- Next steps: rerun load test after optimizations, target p95 latency <1,400 ms with error rate <0.3%, and compare against baseline stored under `load-tests/results/`.
