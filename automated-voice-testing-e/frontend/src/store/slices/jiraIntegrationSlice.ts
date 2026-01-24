import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface JiraProjectConfig {
  projectKey: string;
  issueType: string;
  browseUrl?: string;
  priorityMap?: Record<string, string>;
  labels?: string[];
}

export interface JiraIntegrationConfig {
  baseUrl: string;
  browseUrl: string;
  userEmail: string;
  apiTokenSet: boolean;
  autoCreateTickets?: boolean;
  timeoutSeconds?: number | null;
  projectMapping: Record<string, JiraProjectConfig>;
}

export interface JiraIntegrationUpdatePayload {
  baseUrl: string;
  browseUrl: string;
  userEmail: string;
  apiToken?: string;
  autoCreateTickets?: boolean;
  timeoutSeconds?: number | null;
  projectMapping: Record<string, JiraProjectConfig>;
}

export interface JiraIntegrationState {
  config: JiraIntegrationConfig;
  loading: boolean;
  saving: boolean;
  error: string | null;
  success: string | null;
}

const defaultConfig: JiraIntegrationConfig = {
  baseUrl: '',
  browseUrl: '',
  userEmail: '',
  apiTokenSet: false,
  autoCreateTickets: false,
  timeoutSeconds: null,
  projectMapping: {},
};

export const initialState: JiraIntegrationState = {
  config: defaultConfig,
  loading: false,
  saving: false,
  error: null,
  success: null,
};

const authorizationHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return {
    Authorization: token ? `Bearer ${token}` : 'Bearer ',
  };
};

export const fetchJiraIntegrationConfig = createAsyncThunk<
  JiraIntegrationConfig,
  void,
  { rejectValue: string }
>('jiraIntegration/fetchConfig', async (_, { rejectWithValue }) => {
  try {
    const response = await axios.get<JiraIntegrationConfig>(
      `${API_BASE_URL}/integrations/jira/config`,
      {
        headers: authorizationHeaders(),
      }
    );
    return response.data;
  } catch (error: unknown) {
    let message = 'Failed to fetch Jira integration configuration';
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      message = axiosError.response?.data?.detail ?? message;
    }
    return rejectWithValue(message);
  }
});

export const saveJiraIntegrationConfig = createAsyncThunk<
  JiraIntegrationConfig,
  JiraIntegrationUpdatePayload,
  { rejectValue: string }
>('jiraIntegration/saveConfig', async (payload, { rejectWithValue }) => {
  try {
    const response = await axios.put<JiraIntegrationConfig>(
      `${API_BASE_URL}/integrations/jira/config`,
      payload,
      {
        headers: authorizationHeaders(),
      }
    );
    return response.data;
  } catch (error: unknown) {
    let message = 'Failed to update Jira integration configuration';
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      message = axiosError.response?.data?.detail ?? message;
    }
    return rejectWithValue(message);
  }
});

const jiraIntegrationSlice = createSlice({
  name: 'jiraIntegration',
  initialState,
  reducers: {
    clearJiraIntegrationError(state) {
      state.error = null;
    },
    clearJiraIntegrationSuccess(state) {
      state.success = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchJiraIntegrationConfig.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchJiraIntegrationConfig.fulfilled, (state, action) => {
        state.loading = false;
        state.config = action.payload;
        state.error = null;
      })
      .addCase(fetchJiraIntegrationConfig.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? 'Failed to fetch Jira integration configuration';
      })
      .addCase(saveJiraIntegrationConfig.pending, (state) => {
        state.saving = true;
        state.error = null;
        state.success = null;
      })
      .addCase(saveJiraIntegrationConfig.fulfilled, (state, action) => {
        state.saving = false;
        state.config = action.payload;
        state.success = 'Configuration saved successfully';
      })
      .addCase(saveJiraIntegrationConfig.rejected, (state, action) => {
        state.saving = false;
        state.error = action.payload ?? 'Failed to update Jira integration configuration';
      });
  },
});

export const { clearJiraIntegrationError, clearJiraIntegrationSuccess } = jiraIntegrationSlice.actions;

export default jiraIntegrationSlice.reducer;
