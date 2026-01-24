/**
 * ValidatorStats page tests.
 *
 * Ensures validator statistics page renders personal stats,
 * leaderboard, and accuracy trend information sourced from Redux state.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { Provider } from 'react-redux';
import { MemoryRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import { render, screen } from '@testing-library/react';
import ValidatorStats from '../Validation/ValidatorStats';
import * as validationSlice from '../../store/slices/validationSlice';
import authReducer from '../../store/slices/authSlice';

const validationReducer = validationSlice.default;
const { fetchValidatorStatistics } = validationSlice;

const createValidationState = () =>
  validationReducer(undefined, { type: 'validation/init' });

const buildStore = (preloadedState?: unknown) =>
  configureStore({
    reducer: {
      auth: authReducer,
      validation: validationReducer,
    },
    preloadedState,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        serializableCheck: false,
        immutableCheck: false,
      }),
  });

describe('ValidatorStats page', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders personal stats, leaderboard, and accuracy sections', () => {
    const validationState = {
      ...createValidationState(),
      loading: false,
      validatorSummary: {
        completedValidations: 125,
        approvals: 100,
        rejections: 20,
        accuracy: 0.92,
        averageTimeSeconds: 37,
        currentStreakDays: 6,
      },
      validatorLeaderboard: [
        {
          rank: 1,
          validatorId: 'validator-1',
          displayName: 'Alicia Keys',
          completedValidations: 320,
          accuracy: 0.97,
          averageTimeSeconds: 41,
        },
        {
          rank: 2,
          validatorId: 'validator-2',
          displayName: 'John Legend',
          completedValidations: 275,
          accuracy: 0.93,
          averageTimeSeconds: 44,
        },
      ],
      validatorAccuracyTrend: [
        { date: '2024-01-10', accuracy: 0.94, validations: 15 },
        { date: '2024-01-11', accuracy: 0.91, validations: 12 },
      ],
    };

    const originalThunk = fetchValidatorStatistics;
    const fetchSpy = vi
      .spyOn(validationSlice, 'fetchValidatorStatistics')
      .mockReturnValue({ type: 'validation/fetchValidatorStatistics' } as unknown);

    Object.assign(validationSlice.fetchValidatorStatistics, {
      pending: originalThunk.pending,
      fulfilled: originalThunk.fulfilled,
      rejected: originalThunk.rejected,
    });

    const store = buildStore({
      validation: validationState,
      auth: authReducer(undefined, { type: 'auth/init' }),
    });

    render(
      <Provider store={store}>
        <MemoryRouter>
          <ValidatorStats />
        </MemoryRouter>
      </Provider>
    );

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(screen.getByText('125 validations')).toBeInTheDocument();
    expect(screen.getByText('92% accuracy')).toBeInTheDocument();
    expect(
      screen.getByText(/100 approvals · 20 rejections/)
    ).toBeInTheDocument();
    expect(screen.getByText(/Alicia Keys/)).toBeInTheDocument();
    expect(screen.getByText(/John Legend/)).toBeInTheDocument();
    expect(screen.getByText('2024-01-10')).toBeInTheDocument();
    expect(screen.getByText('2024-01-11')).toBeInTheDocument();
  });

  it('shows loading indicator when stats are being fetched', () => {
    const validationState = {
      ...createValidationState(),
      loading: true,
      validatorSummary: null,
      validatorLeaderboard: [],
      validatorAccuracyTrend: [],
    };

    const originalThunk = fetchValidatorStatistics;
    vi.spyOn(validationSlice, 'fetchValidatorStatistics').mockReturnValue({
      type: 'validation/fetchValidatorStatistics',
    } as unknown);

    Object.assign(validationSlice.fetchValidatorStatistics, {
      pending: originalThunk.pending,
      fulfilled: originalThunk.fulfilled,
      rejected: originalThunk.rejected,
    });

    const store = buildStore({
      validation: validationState,
      auth: authReducer(undefined, { type: 'auth/init' }),
    });

    render(
      <Provider store={store}>
        <MemoryRouter>
          <ValidatorStats />
        </MemoryRouter>
      </Provider>
    );

    expect(screen.getByText(/loading validator statistics/i)).toBeInTheDocument();
  });
});
