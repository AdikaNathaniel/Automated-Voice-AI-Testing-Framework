import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface SlackNotificationPreference {
  enabled: boolean;
  channel: string;
}

export interface SlackIntegrationConfig {
  isConnected: boolean;
  workspaceName: string | null;
  workspaceIconUrl: string | null;
  connectUrl: string;
  defaultChannel: string;
  notificationPreferences: {
    suiteRun: SlackNotificationPreference;
    criticalDefect: SlackNotificationPreference;
    systemAlert: SlackNotificationPreference;
    edgeCase: SlackNotificationPreference;
  };
  botTokenSet: boolean;
  signingSecretSet: boolean;
}

export interface SlackIntegrationUpdatePayload {
  defaultChannel: string;
  notificationPreferences: {
    suiteRun: SlackNotificationPreference;
    criticalDefect: SlackNotificationPreference;
    systemAlert: SlackNotificationPreference;
    edgeCase: SlackNotificationPreference;
  };
  webhookUrl?: string;
}

export interface SlackIntegrationState {
  config: SlackIntegrationConfig;
  loading: boolean;
  saving: boolean;
  disconnecting: boolean;
  error: string | null;
  success: string | null;
}

const defaultPreference: SlackNotificationPreference = {
  enabled: true,
  channel: '',
};

const defaultConfig: SlackIntegrationConfig = {
  isConnected: false,
  workspaceName: null,
  workspaceIconUrl: null,
  connectUrl: '',
  defaultChannel: '',
  notificationPreferences: {
    suiteRun: { ...defaultPreference },
    criticalDefect: { ...defaultPreference },
    systemAlert: { ...defaultPreference },
    edgeCase: { ...defaultPreference },
  },
  botTokenSet: false,
  signingSecretSet: false,
};

export const initialState: SlackIntegrationState = {
  config: defaultConfig,
  loading: false,
  saving: false,
  disconnecting: false,
  error: null,
  success: null,
};

const authorizationHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return {
    Authorization: token ? `Bearer ${token}` : 'Bearer ',
  };
};

export const fetchSlackIntegrationConfig = createAsyncThunk<
  SlackIntegrationConfig,
  void,
  { rejectValue: string }
>('slackIntegration/fetchConfig', async (_, { rejectWithValue }) => {
  try {
    const response = await axios.get<SlackIntegrationConfig>(
      `${API_BASE_URL}/integrations/slack/config`,
      {
        headers: authorizationHeaders(),
      }
    );
    return response.data;
  } catch (error: unknown) {
    let message = 'Failed to fetch Slack integration configuration';
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      message = axiosError.response?.data?.detail ?? message;
    }
    return rejectWithValue(message);
  }
});

export const saveSlackIntegrationConfig = createAsyncThunk<
  SlackIntegrationConfig,
  SlackIntegrationUpdatePayload,
  { rejectValue: string }
>('slackIntegration/saveConfig', async (payload, { rejectWithValue }) => {
  try {
    const response = await axios.put<SlackIntegrationConfig>(
      `${API_BASE_URL}/integrations/slack/config`,
      payload,
      {
        headers: authorizationHeaders(),
      }
    );
    return response.data;
  } catch (error: unknown) {
    let message = 'Failed to update Slack integration configuration';
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      message = axiosError.response?.data?.detail ?? message;
    }
    return rejectWithValue(message);
  }
});

export const disconnectSlackIntegration = createAsyncThunk<
  SlackIntegrationConfig,
  void,
  { rejectValue: string }
>('slackIntegration/disconnect', async (_, { rejectWithValue }) => {
  try {
    const response = await axios.delete<SlackIntegrationConfig>(
      `${API_BASE_URL}/integrations/slack/config`,
      {
        headers: authorizationHeaders(),
      }
    );
    return response.data;
  } catch (error: unknown) {
    let message = 'Failed to disconnect Slack workspace';
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      message = axiosError.response?.data?.detail ?? message;
    }
    return rejectWithValue(message);
  }
});

const slackIntegrationSlice = createSlice({
  name: 'slackIntegration',
  initialState,
  reducers: {
    clearSlackIntegrationError(state) {
      state.error = null;
    },
    clearSlackIntegrationSuccess(state) {
      state.success = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSlackIntegrationConfig.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSlackIntegrationConfig.fulfilled, (state, action) => {
        state.loading = false;
        state.config = action.payload;
        state.error = null;
      })
      .addCase(fetchSlackIntegrationConfig.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? 'Failed to fetch Slack integration configuration';
      })
      .addCase(saveSlackIntegrationConfig.pending, (state) => {
        state.saving = true;
        state.error = null;
        state.success = null;
      })
      .addCase(saveSlackIntegrationConfig.fulfilled, (state, action) => {
        state.saving = false;
        state.config = action.payload;
        state.success = 'Configuration saved successfully';
      })
      .addCase(saveSlackIntegrationConfig.rejected, (state, action) => {
        state.saving = false;
        state.error = action.payload ?? 'Failed to update Slack integration configuration';
      })
      .addCase(disconnectSlackIntegration.pending, (state) => {
        state.disconnecting = true;
        state.error = null;
        state.success = null;
      })
      .addCase(disconnectSlackIntegration.fulfilled, (state, action) => {
        state.disconnecting = false;
        state.config = action.payload;
        state.success = 'Slack workspace disconnected';
      })
      .addCase(disconnectSlackIntegration.rejected, (state, action) => {
        state.disconnecting = false;
        state.error = action.payload ?? 'Failed to disconnect Slack workspace';
      });
  },
});

export const { clearSlackIntegrationError, clearSlackIntegrationSuccess } = slackIntegrationSlice.actions;

export default slackIntegrationSlice.reducer;
