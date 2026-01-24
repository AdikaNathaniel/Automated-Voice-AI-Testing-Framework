# Load Testing Guide

This directory contains the artefacts required to stress-test the automated
testing API using [k6](https://k6.io). The primary scenario models one thousand
or more concurrent virtual users repeatedly triggering end-to-end voice test
executions against the staging environment.

## Contents

- `k6/testExecutionLoadTest.js` – main k6 scenario definition
- `k6/testExecutionConfig.cjs` – shared configuration (scenarios, thresholds,
  environment helpers, summary writer)
- `results/sample-test-execution.json` – representative output captured from a
  dry run (illustrative metrics only)

## Prerequisites

1. Install the k6 CLI: `brew install k6` (macOS) or refer to the
   [official installation docs](https://k6.io/docs/get-started/installation/).
2. Ensure the staging environment is reachable and seeded with at least one test
   suite ID that can be executed via the `/test-executions` endpoint.

## Environment variables

The configuration helper reads the following values (falling back to sensible
defaults when not provided):

| Variable                | Description                                    | Default                                           |
| ----------------------- | ---------------------------------------------- | ------------------------------------------------- |
| `TARGET_BASE_URL`       | Base API URL for the execution endpoints       | `https://staging.voiceai.example.com/api/v1`      |
| `LOAD_TEST_TOKEN`       | Bearer token used for authenticated requests   | empty string (no auth header)                     |
| `LOAD_TEST_SUITE_ID`    | Identifier of the suite to execute             | `demo-suite`                                      |
| `LOAD_TEST_RAMP_DELAY`  | Seconds to sleep between iterations per VU     | `1`                                               |

Set these via the shell or `.env` before running the scenario, for example:

```bash
export TARGET_BASE_URL="https://staging.voiceai.example.com/api/v1"
export LOAD_TEST_TOKEN="your-temporary-staging-token"
export LOAD_TEST_SUITE_ID="suite-12345"
```

## Running the scenario

```bash
cd load-tests/k6
k6 run testExecutionLoadTest.js --vus 1200 --duration 15m
```

The bundled options already configure a **ramping-vus** executor that peaks at
1,200 virtual users while sustaining more than 1,000 concurrent executions for
several minutes. The CLI flags above simply mirror the internal configuration
and allow you to tweak the overall duration if required.

### Capturing structured output

The configuration exports a `handleSummary` hook that writes the full k6
results object to `load-results.json` in addition to printing an overview to
stdout. To persist the JSON file as well as the default text summary, run:

```bash
k6 run testExecutionLoadTest.js --summary-export load-results.json
```

> **Note:** Because the script also writes the JSON file, you do not need the
> `--summary-export` flag unless you prefer k6’s native formatting.

## Interpreting the metrics

The scenario enforces two key thresholds:

- `http_req_duration` – the 95th percentile must remain under **2 s** and the
  99th percentile under **5 s**.
- `http_req_failed` – the error rate must stay below **1 %**.

Should either threshold fail, k6 exits with a non-zero status code, allowing CI
pipelines to flag regressions automatically.

The sample report in `results/sample-test-execution.json` shows expected values
for a healthy run:

- Peak virtual users: **1,200**
- Requests executed: **14,872**
- Error rate: **0.46 %** (all due to 5xx responses)
- 95th percentile latency: **1.63 s**

Use these baselines to track improvements or regressions over time.
