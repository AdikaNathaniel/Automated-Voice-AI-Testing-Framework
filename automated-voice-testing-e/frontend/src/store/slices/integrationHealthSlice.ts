/**
 * Integration Health Redux Slice
 *
 * Manages state for integration health monitoring, fetching health status
 * from the backend to display real-time integration health indicators.
 */

import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface IntegrationHealthStatus {
  configured: boolean;
  connected: boolean;
  status: 'healthy' | 'degraded' | 'critical' | 'unconfigured';
  lastSuccessfulOperation: string | null;
  lastError: string | null;
  lastErrorAt: string | null;
}

export interface IntegrationHealthResponse {
  github: IntegrationHealthStatus;
  jira: IntegrationHealthStatus;
  slack: IntegrationHealthStatus;
  overallStatus: 'healthy' | 'degraded' | 'critical' | 'unconfigured';
  checkedAt: string;
}

export interface IntegrationHealthState {
  health: IntegrationHealthResponse | null;
  loading: boolean;
  error: string | null;
  lastFetched: string | null;
}

export const initialState: IntegrationHealthState = {
  health: null,
  loading: false,
  error: null,
  lastFetched: null,
};

const authorizationHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return {
    Authorization: token ? `Bearer ${token}` : 'Bearer ',
  };
};

export const fetchIntegrationHealth = createAsyncThunk<
  IntegrationHealthResponse,
  void,
  { rejectValue: string }
>('integrationHealth/fetch', async (_, { rejectWithValue }) => {
  try {
    const response = await axios.get<IntegrationHealthResponse>(
      `${API_BASE_URL}/integrations/health`,
      {
        headers: authorizationHeaders(),
      }
    );
    return response.data;
  } catch (error: unknown) {
    let message = 'Failed to fetch integration health status';
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      message = axiosError.response?.data?.detail ?? message;
    }
    return rejectWithValue(message);
  }
});

const integrationHealthSlice = createSlice({
  name: 'integrationHealth',
  initialState,
  reducers: {
    clearIntegrationHealthError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchIntegrationHealth.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchIntegrationHealth.fulfilled, (state, action) => {
        state.loading = false;
        state.health = action.payload;
        state.lastFetched = new Date().toISOString();
        state.error = null;
      })
      .addCase(fetchIntegrationHealth.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? 'Failed to fetch integration health status';
      });
  },
});

export const { clearIntegrationHealthError } = integrationHealthSlice.actions;

export default integrationHealthSlice.reducer;
