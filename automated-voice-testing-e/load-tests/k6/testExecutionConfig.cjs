const k6Env = typeof __ENV !== "undefined" ? __ENV : undefined;
const nodeEnv = typeof process !== "undefined" ? process.env : undefined;

const resolveEnv = (key, fallback) => {
  if (k6Env && k6Env[key]) {
    return k6Env[key];
  }
  if (nodeEnv && nodeEnv[key]) {
    return nodeEnv[key];
  }
  return fallback;
};

const testExecutionOptions = {
  scenarios: {
    test_execution: {
      executor: "ramping-vus",
      startVUs: 0,
      gracefulRampDown: "2m",
      stages: [
        { duration: "2m", target: 200 },
        { duration: "3m", target: 600 },
        { duration: "5m", target: 1000 },
        { duration: "3m", target: 1200 },
        { duration: "3m", target: 800 },
        { duration: "2m", target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_duration: ["p(95)<2000", "p(99)<5000"],
    http_req_failed: ["rate<0.01"],
  },
  summaryTrendStats: ["avg", "min", "max", "p(90)", "p(95)", "p(99)"],
};

const loadTestSettings = {
  targetBaseUrl: resolveEnv("TARGET_BASE_URL", "https://staging.voiceai.example.com/api/v1"),
  authToken: resolveEnv("LOAD_TEST_TOKEN", ""),
  testSuiteId: resolveEnv("LOAD_TEST_SUITE_ID", ""),
  rampDelaySeconds: Number.parseInt(resolveEnv("LOAD_TEST_RAMP_DELAY", "1"), 10),
};

const defaultSummaryFile = "load-results.json";

const buildRequestHeaders = () => {
  const headers = { "Content-Type": "application/json" };
  if (loadTestSettings.authToken) {
    headers.Authorization = `Bearer ${loadTestSettings.authToken}`;
  }
  return headers;
};

const createSummaryHandler = (outputPath = defaultSummaryFile) => {
  return (data) => {
    const json = JSON.stringify(data, null, 2);
    return {
      stdout: `k6 load test summary written to ${outputPath}`,
      [outputPath]: json,
    };
  };
};

module.exports = {
  testExecutionOptions,
  loadTestSettings,
  defaultSummaryFile,
  buildRequestHeaders,
  createSummaryHandler,
};
