/**
 * Validation Slice Timer Tests
 *
 * Ensures timer-related reducers correctly start, update,
 * and reset timing metadata for validation workflow.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import validationReducer, {
  setCurrentValidation,
  updateValidationTimer,
  submitValidation,
  releaseValidation,
  fetchValidatorStatistics,
} from '../validationSlice';
import { ValidationStatus, ValidationQueue, ValidationDecision, HumanValidationCreate } from '../../../types/validation';

const createInitialState = () =>
  validationReducer(undefined, { type: 'validation/init' });

const createQueueItem = (): ValidationQueue => ({
  id: 'queue-1',
  validationResultId: 'result-1',
  priority: 1,
  confidenceScore: 0.55,
  languageCode: 'en-US',
  status: ValidationStatus.PENDING,
  claimedBy: null,
  claimedAt: null,
});

describe('validationSlice timer behaviour', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('starts timer when setting current validation', () => {
    const fakeNow = new Date('2024-01-01T10:00:00Z').getTime();
    vi.setSystemTime(fakeNow);

    const item = createQueueItem();
    let state = createInitialState();

    state = validationReducer(state, setCurrentValidation(item));

    expect(state.current).toEqual(item);
    expect(state.timerStarted).toBe(fakeNow);
    expect(state.timeSpent).toBe(0);
  });

  it('updates timeSpent based on elapsed seconds', () => {
    const start = new Date('2024-01-01T10:00:00Z').getTime();
    vi.setSystemTime(start);

    const item = createQueueItem();
    let state = validationReducer(createInitialState(), setCurrentValidation(item));

    vi.setSystemTime(start + 5_200);
    state = validationReducer(state, updateValidationTimer());
    expect(state.timeSpent).toBe(5);

    vi.setSystemTime(start + 65_000);
    state = validationReducer(state, updateValidationTimer());
    expect(state.timeSpent).toBe(65);
  });

  it('resets timer when validation is submitted', () => {
    const start = new Date('2024-01-01T10:00:00Z').getTime();
    vi.setSystemTime(start);

    const item = createQueueItem();
    let state = validationReducer(createInitialState(), setCurrentValidation(item));

    vi.setSystemTime(start + 12_000);
    state = validationReducer(state, updateValidationTimer());
    expect(state.timeSpent).toBe(12);

    const validationData: HumanValidationCreate = {
      validationResultId: item.validationResultId,
      decision: 'pass',
      timeSpent: 12,
    };

    state = validationReducer(
      state,
      submitValidation.fulfilled({}, '', {
        queueId: item.id,
        validation: validationData,
      })
    );

    expect(state.current).toBeNull();
    expect(state.timerStarted).toBeNull();
    expect(state.timeSpent).toBe(0);
  });

  it('resets timer when validation is released', () => {
    const start = new Date('2024-01-01T10:00:00Z').getTime();
    vi.setSystemTime(start);

    const item = createQueueItem();
    let state = validationReducer(createInitialState(), setCurrentValidation(item));

    vi.setSystemTime(start + 7_000);
    state = validationReducer(state, updateValidationTimer());
    expect(state.timeSpent).toBe(7);

    state = validationReducer(
      state,
      releaseValidation.fulfilled({}, '', item.id)
    );

    expect(state.current).toBeNull();
    expect(state.timerStarted).toBeNull();
    expect(state.timeSpent).toBe(0);
  });
});

describe('validationSlice validator statistics', () => {
  it('initializes validator stats fields', () => {
    const state = createInitialState();

    expect(state.validatorSummary).toBeNull();
    expect(state.validatorLeaderboard).toEqual([]);
    expect(state.validatorAccuracyTrend).toEqual([]);
  });

  it('stores validator stats data on fetch success', () => {
    const initial = createInitialState();
    const payload = {
      personal: {
        completedValidations: 125,
        approvals: 100,
        rejections: 20,
        accuracy: 0.92,
        averageTimeSeconds: 37,
        currentStreakDays: 6,
      },
      leaderboard: [
        {
          rank: 1,
          validatorId: 'validator-1',
          displayName: 'Alicia Keys',
          completedValidations: 320,
          accuracy: 0.97,
          averageTimeSeconds: 41,
        },
      ],
      accuracyTrend: [
        { date: '2024-01-10', accuracy: 0.94, validations: 15 },
        { date: '2024-01-11', accuracy: 0.91, validations: 12 },
      ],
    };

    const next = validationReducer(
      initial,
      fetchValidatorStatistics.fulfilled(payload, 'id', undefined)
    );

    expect(next.validatorSummary).toEqual(payload.personal);
    expect(next.validatorLeaderboard).toEqual(payload.leaderboard);
    expect(next.validatorAccuracyTrend).toEqual(payload.accuracyTrend);
    expect(next.loading).toBe(false);
    expect(next.error).toBeNull();
  });

  it('captures error on fetch failure', () => {
    const initial = createInitialState();
    const error = new Error('Failed to load validator stats');

    const next = validationReducer(
      initial,
      fetchValidatorStatistics.rejected(error, 'id', undefined, {
        message: error.message,
      })
    );

    expect(next.loading).toBe(false);
    expect(next.error).toBe(error.message);
  });
});
