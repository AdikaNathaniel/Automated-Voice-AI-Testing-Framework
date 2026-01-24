import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export type GitHubSyncDirection = 'pull' | 'push' | 'both';

export interface GitHubAccountSummary {
  login: string;
  avatarUrl: string;
  htmlUrl: string;
}

export interface GitHubRepositorySummary {
  id: number;
  name: string;
  fullName: string;
  private: boolean;
  defaultBranch: string;
}

export interface GitHubSyncSettings {
  repository: string;
  syncDirection: GitHubSyncDirection;
  autoSync: boolean;
  createIssues: boolean;
}

export interface GitHubIntegrationState {
  isConnected: boolean;
  account: GitHubAccountSummary | null;
  connectionUrl: string | null;
  syncSettings: GitHubSyncSettings;
  repositories: GitHubRepositorySummary[];
  lastSyncedAt: string | null;
  loading: boolean;
  savingSettings: boolean;
  error: string | null;
}

export const initialState: GitHubIntegrationState = {
  isConnected: false,
  account: null,
  connectionUrl: null,
  syncSettings: {
    repository: '',
    syncDirection: 'both',
    autoSync: true,
    createIssues: true,
  },
  repositories: [],
  lastSyncedAt: null,
  loading: false,
  savingSettings: false,
  error: null,
};

interface GitHubIntegrationStatusResponse {
  connected: boolean;
  account: GitHubAccountSummary | null;
  authorizationUrl: string | null;
  syncSettings: GitHubSyncSettings | null;
  repositories: GitHubRepositorySummary[] | null;
  lastSyncedAt: string | null;
}

const authorizationHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return {
    Authorization: token ? `Bearer ${token}` : 'Bearer ',
  };
};

export const fetchGitHubIntegrationStatus = createAsyncThunk<
  GitHubIntegrationStatusResponse,
  void,
  { rejectValue: string }
>('githubIntegration/fetchStatus', async (_, { rejectWithValue }) => {
  try {
    const response = await axios.get<GitHubIntegrationStatusResponse>(
      `${API_BASE_URL}/integrations/github/status`,
      {
        headers: authorizationHeaders(),
      }
    );
    return response.data;
  } catch (error: unknown) {
    let message = 'Failed to fetch GitHub integration status';
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      message = axiosError.response?.data?.detail ?? message;
    }
    return rejectWithValue(message);
  }
});

export const startGitHubConnection = createAsyncThunk<
  { authorizationUrl: string; oauthConfigured?: boolean },
  void,
  { rejectValue: string }
>('githubIntegration/startConnection', async (_, { rejectWithValue }) => {
  try {
    const response = await axios.post<{ success: boolean; data: { authorizationUrl: string; oauthConfigured?: boolean } }>(
      `${API_BASE_URL}/integrations/github/connect`,
      undefined,
      {
        headers: authorizationHeaders(),
      }
    );

    // Extract data from SuccessResponse wrapper
    return response.data.data;
  } catch (error: unknown) {
    let message = 'Failed to initiate GitHub connection';
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      message = axiosError.response?.data?.detail ?? message;
    }
    return rejectWithValue(message);
  }
});

export const disconnectGitHubIntegration = createAsyncThunk<void, void, { rejectValue: string }>(
  'githubIntegration/disconnect',
  async (_, { rejectWithValue }) => {
    try {
      await axios.post(
        `${API_BASE_URL}/integrations/github/disconnect`,
        undefined,
        { headers: authorizationHeaders() }
      );
    } catch (error: unknown) {
      let message = 'Failed to disconnect GitHub integration';
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string } } };
        message = axiosError.response?.data?.detail ?? message;
      }
      return rejectWithValue(message);
    }
  }
);

export const updateGitHubSyncSettings = createAsyncThunk<
  GitHubSyncSettings,
  GitHubSyncSettings,
  { rejectValue: string }
>('githubIntegration/updateSyncSettings', async (settings, { rejectWithValue }) => {
  try {
    const response = await axios.put<GitHubSyncSettings>(
      `${API_BASE_URL}/integrations/github/sync-settings`,
      settings,
      {
        headers: authorizationHeaders(),
      }
    );
    return response.data;
  } catch (error: unknown) {
    let message = 'Failed to update GitHub sync settings';
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      message = axiosError.response?.data?.detail ?? message;
    }
    return rejectWithValue(message);
  }
});

const githubIntegrationSlice = createSlice({
  name: 'githubIntegration',
  initialState,
  reducers: {
    clearGitHubIntegrationError(state) {
      state.error = null;
    },
    clearGitHubConnectionUrl(state) {
      state.connectionUrl = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchGitHubIntegrationStatus.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchGitHubIntegrationStatus.fulfilled, (state, action) => {
        state.loading = false;
        state.isConnected = action.payload.connected;
        state.account = action.payload.account;
        state.connectionUrl = action.payload.authorizationUrl;
        state.syncSettings = action.payload.syncSettings ?? initialState.syncSettings;
        state.repositories = action.payload.repositories ?? [];
        state.lastSyncedAt = action.payload.lastSyncedAt ?? null;
        state.error = null;
      })
      .addCase(fetchGitHubIntegrationStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? 'Failed to fetch GitHub integration status';
        state.isConnected = false;
      })
      .addCase(startGitHubConnection.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.connectionUrl = null;
      })
      .addCase(startGitHubConnection.fulfilled, (state, action) => {
        state.loading = false;
        state.connectionUrl = action.payload.authorizationUrl;
      })
      .addCase(startGitHubConnection.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? 'Failed to initiate GitHub connection';
      })
      .addCase(disconnectGitHubIntegration.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(disconnectGitHubIntegration.fulfilled, () => {
        return { ...initialState };
      })
      .addCase(disconnectGitHubIntegration.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? 'Failed to disconnect GitHub integration';
      })
      .addCase(updateGitHubSyncSettings.pending, (state) => {
        state.savingSettings = true;
        state.error = null;
      })
      .addCase(updateGitHubSyncSettings.fulfilled, (state, action) => {
        state.savingSettings = false;
        state.syncSettings = action.payload;
        state.error = null;
      })
      .addCase(updateGitHubSyncSettings.rejected, (state, action) => {
        state.savingSettings = false;
        state.error = action.payload ?? 'Failed to update GitHub sync settings';
      });
  },
});

export const { clearGitHubIntegrationError, clearGitHubConnectionUrl } = githubIntegrationSlice.actions;

export default githubIntegrationSlice.reducer;
