import http from "k6/http";
import { check, sleep } from "k6";
import { SharedArray } from "k6/data";

import config from "./testExecutionConfig.cjs";

const {
  testExecutionOptions,
  loadTestSettings,
  buildRequestHeaders,
  createSummaryHandler,
} = config;

export const options = testExecutionOptions;
export const handleSummary = createSummaryHandler();

const defaultPayloads = [
  { utterance: "turn on the kitchen lights", languageCode: "en-US" },
  { utterance: "set the thermostat to 72 degrees", languageCode: "en-US" },
  { utterance: "enciende las luces de la sala", languageCode: "es-ES" },
  { utterance: "réduis la température à 19 degrés", languageCode: "fr-FR" },
  { utterance: "テレビをつけて", languageCode: "ja-JP" },
];

const requestBodies = new SharedArray("test-execution-inputs", () => defaultPayloads);

const requestHeaders = buildRequestHeaders();
const executionEndpoint = `${loadTestSettings.targetBaseUrl.replace(/\/$/, "")}/test-executions`;

export default function testExecutionScenario() {
  const index = Math.floor(Math.random() * requestBodies.length);
  const testCase = requestBodies[index];

  const body = JSON.stringify({
    suiteId: loadTestSettings.testSuiteId || "demo-suite",
    languageCode: testCase.languageCode,
    input: testCase.utterance,
  });

  const response = http.post(executionEndpoint, body, { headers: requestHeaders });

  check(response, {
    "response status is 2xx": (res) => res.status >= 200 && res.status < 300,
    "response includes execution id": (res) => {
      try {
        const parsed = res.json();
        return Boolean(parsed?.executionId);
      } catch (error) {
        return false;
      }
    },
  });

  sleep(loadTestSettings.rampDelaySeconds);
}
