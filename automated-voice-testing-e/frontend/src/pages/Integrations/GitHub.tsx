import { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, AlertCircle, ExternalLink } from 'lucide-react';
import { SiGithub } from 'react-icons/si';
import { Dropdown } from '../../components/common';
import type { RootState, AppDispatch } from '../../store';
import {
  clearGitHubConnectionUrl,
  clearGitHubIntegrationError,
  disconnectGitHubIntegration,
  fetchGitHubIntegrationStatus,
  startGitHubConnection,
  updateGitHubSyncSettings,
  type GitHubIntegrationState,
  type GitHubSyncDirection,
  type GitHubSyncSettings,
} from '../../store/slices/githubIntegrationSlice';

const formatLastSynced = (timestamp: string | null): string => {
  if (!timestamp) {
    return 'Never synced';
  }
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return 'Never synced';
  }
  return date.toLocaleString();
};

const cloneSyncSettings = (settings: GitHubSyncSettings): GitHubSyncSettings => ({
  repository: settings.repository,
  syncDirection: settings.syncDirection,
  autoSync: settings.autoSync,
  createIssues: settings.createIssues,
});

const GitHubIntegrationPage = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const {
    isConnected,
    account,
    connectionUrl,
    syncSettings,
    repositories,
    lastSyncedAt,
    loading,
    savingSettings,
    error,
  } = useSelector<RootState, GitHubIntegrationState>((state) => state.githubIntegration);

  const [formState, setFormState] = useState<GitHubSyncSettings>(cloneSyncSettings(syncSettings));
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [oauthSuccess, setOauthSuccess] = useState<string | null>(null);

  // Handle OAuth callback parameters
  useEffect(() => {
    const success = searchParams.get('success');
    const oauthError = searchParams.get('error');
    const username = searchParams.get('username');
    const errorMessage = searchParams.get('message');

    if (success === 'true' && username) {
      setOauthSuccess(`Successfully connected GitHub account: ${username}`);
      // Refresh integration status to get the updated state
      dispatch(fetchGitHubIntegrationStatus());
      // Clear the URL parameters
      setSearchParams({});
    } else if (oauthError) {
      const errorMessages: Record<string, string> = {
        'oauth_not_configured': 'GitHub OAuth is not configured. Please contact your administrator.',
        'invalid_state': 'Invalid OAuth state. Please try connecting again.',
        'oauth_failed': errorMessage ? `OAuth failed: ${errorMessage}` : 'GitHub OAuth failed. Please try again.',
        'unexpected_error': 'An unexpected error occurred. Please try again.',
        'storage_failed': 'Failed to save GitHub connection. Please try again.',
      };
      setLocalError(errorMessages[oauthError] || 'An error occurred during GitHub connection.');
      // Clear the URL parameters
      setSearchParams({});
    }
  }, [searchParams, setSearchParams, dispatch]);

  useEffect(() => {
    dispatch(fetchGitHubIntegrationStatus());
  }, [dispatch]);

  useEffect(() => {
    setFormState(cloneSyncSettings(syncSettings));
  }, [syncSettings.repository, syncSettings.syncDirection, syncSettings.autoSync, syncSettings.createIssues]);

  const availableRepositories = useMemo(() => repositories ?? [], [repositories]);

  const handleRepositoryChange = (repo: string) => {
    setFormState((current) => ({
      ...current,
      repository: repo,
    }));
    setSaveSuccess(false);
  };

  const handleSyncDirectionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormState((current) => ({
      ...current,
      syncDirection: event.target.value as GitHubSyncDirection,
    }));
    setSaveSuccess(false);
  };

  const handleCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = event.target;
    setFormState((current) => ({
      ...current,
      [name]: checked,
    }));
    setSaveSuccess(false);
  };

  const handleConnect = async () => {
    setLocalError(null);
    setOauthSuccess(null);
    try {
      const result = await dispatch(startGitHubConnection()).unwrap();
      // If we got an authorization URL, redirect to it
      if (result?.authorizationUrl) {
        window.location.href = result.authorizationUrl;
      }
    } catch (err: unknown) {
      const message = typeof err === 'string' ? err : 'Failed to start GitHub connection';
      setLocalError(message);
    }
  };

  const handleDisconnect = async () => {
    setLocalError(null);
    try {
      await dispatch(disconnectGitHubIntegration()).unwrap();
    } catch (err: unknown) {
      const message = typeof err === 'string' ? err : 'Failed to disconnect GitHub integration';
      setLocalError(message);
    }
  };

  const handleClearConnectionUrl = () => {
    dispatch(clearGitHubConnectionUrl());
  };

  const handleDismissError = () => {
    dispatch(clearGitHubIntegrationError());
    setLocalError(null);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSaveSuccess(false);
    setLocalError(null);

    try {
      await dispatch(updateGitHubSyncSettings(formState)).unwrap();
      setSaveSuccess(true);
    } catch (err: unknown) {
      const message = typeof err === 'string' ? err : 'Failed to update sync settings';
      setLocalError(message);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Back Button */}
      <button
        onClick={() => navigate('/integrations')}
        className="flex items-center gap-2 text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)] transition-colors mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Integrations
      </button>

      <div className="space-y-6">
        {/* Header with Brand Icon */}
        <div className="bg-gradient-to-r from-[var(--color-surface-raised)] to-[var(--color-surface-raised)]/50 rounded-xl p-8 shadow-md border border-[var(--color-border-default)]">
          <div className="flex items-center gap-4">
            <div className="p-2.5 bg-[var(--color-interactive-hover)] rounded-lg shadow-lg">
              <SiGithub className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[var(--color-content-primary)]">GitHub Integration</h1>
              <p className="text-sm text-[var(--color-content-secondary)] mt-1">
                Connect GitHub to sync test cases and automatically create issues for test failures
              </p>
            </div>
          </div>
        </div>

        {/* How it works banner */}
        <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)] rounded-lg p-4">
          <h3 className="text-sm font-semibold text-[var(--color-status-info)] mb-2">
            How GitHub Integration Works
          </h3>
          <p className="text-sm text-[var(--color-status-info)] mb-3">
            This is an <strong>outgoing</strong> integration that fires <strong>after</strong> your tests complete:
          </p>
          <div className="space-y-2 text-sm text-[var(--color-status-info)]">
            <div className="flex items-start gap-2">
              <span className="text-[var(--color-status-info)]">1.</span>
              <span>CI/CD webhook triggers test suite to run</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-[var(--color-status-info)]">2.</span>
              <span>Tests execute and results are collected</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-[var(--color-status-info)]">3.</span>
              <span><strong>GitHub integration fires:</strong> Automatically creates issues for failed tests if enabled</span>
            </div>
          </div>
        </div>

        {oauthSuccess && (
          <div className="bg-[var(--color-status-success-bg)] border border-[var(--color-status-success)] rounded-lg p-4 flex items-start justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-[var(--color-status-success)]" />
              <p className="text-[var(--color-status-success)] font-medium">{oauthSuccess}</p>
            </div>
            <button onClick={() => setOauthSuccess(null)} className="text-[var(--color-status-success)] hover:text-[var(--color-status-success)]">
              Dismiss
            </button>
          </div>
        )}

        {(error || localError) && (
          <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4 flex items-start justify-between" data-testid="github-integration-error">
            <p className="text-[var(--color-status-danger)]">{localError ?? error}</p>
            <button onClick={handleDismissError} className="text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)]">
              Dismiss
            </button>
          </div>
        )}

        {connectionUrl && (
          <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)] rounded-lg p-4 flex items-start justify-between">
            <p className="text-[var(--color-status-info)]">
              OAuth request created.{' '}
              <a
                href={connectionUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[var(--color-status-info)] hover:underline inline-flex items-center gap-1"
              >
                Complete GitHub connection
                <ExternalLink className="w-4 h-4" />
              </a>
            </p>
            <button onClick={handleClearConnectionUrl} className="text-[var(--color-status-info)] hover:text-[var(--color-status-info)]">
              Dismiss
            </button>
          </div>
        )}

        {/* Account Connection Card */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md border border-[var(--color-border-default)]">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-[var(--color-content-primary)]">Account Connection</h2>
              <div className="flex items-center gap-2">
                {isConnected ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-[var(--color-status-success)]" />
                    <span className="text-sm font-semibold text-[var(--color-status-success)]">Connected</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-4 h-4 text-[var(--color-status-warning)]" />
                    <span className="text-sm font-semibold text-[var(--color-status-warning)]">Not Connected</span>
                  </>
                )}
              </div>
            </div>

            {!isConnected && (
              <>
                <p className="text-sm text-[var(--color-content-secondary)]">
                  Connect your GitHub account to enable repository sync, commit status updates, and automatic issue creation
                </p>
                <button
                  onClick={handleConnect}
                  disabled={loading}
                  className="px-6 py-3 rounded-lg text-sm font-semibold text-white transition-all hover:shadow-lg hover:-translate-y-0.5 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
                >
                  {loading ? 'Connecting...' : 'Connect GitHub'}
                </button>
              </>
            )}

            {isConnected && account && (
              <div className="flex flex-col sm:flex-row gap-4 items-center">
                <img
                  src={account.avatarUrl}
                  alt={`${account.login} avatar`}
                  className="w-16 h-16 rounded-full border-2 border-[var(--color-border-default)]"
                />
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-[var(--color-content-primary)]">{account.login}</h3>
                  <a
                    href={account.htmlUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[var(--color-status-info)] hover:underline inline-flex items-center gap-1 text-sm"
                  >
                    View GitHub profile
                    <ExternalLink className="w-3 h-3" />
                  </a>
                  <p className="text-sm text-[var(--color-content-secondary)] mt-1">
                    Last synced: {formatLastSynced(lastSyncedAt)}
                  </p>
                </div>
              </div>
            )}
          </div>
          {isConnected && (
            <div className="flex justify-end mt-4 pt-4 border-t border-[var(--color-border-default)]">
              <button
                onClick={handleDisconnect}
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)] transition-colors disabled:opacity-50"
              >
                Disconnect
              </button>
            </div>
          )}
        </div>

        {/* Sync Settings Form */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md border border-[var(--color-border-default)]">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-[var(--color-content-primary)] mb-1">Sync Settings</h2>
              <p className="text-sm text-[var(--color-content-secondary)]">
                Configure repository and sync behavior for GitHub automation
              </p>
            </div>

            <div>
              <label htmlFor="github-repository-select" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Repository
              </label>
              <Dropdown
                id="github-repository-select"
                value={formState.repository}
                onChange={handleRepositoryChange}
                disabled={!isConnected || availableRepositories.length === 0 || loading}
                placeholder={availableRepositories.length === 0 ? 'No repositories available' : 'Select repository'}
                options={availableRepositories.map((repo) => ({
                  value: repo.fullName,
                  label: `${repo.fullName}${repo.private ? ' (Private)' : ''}`,
                }))}
              />
            </div>

            <div className="bg-[var(--color-surface-inset)]/50 rounded-lg p-4 border border-[var(--color-border-default)]">
              <h3 className="text-sm font-bold text-[var(--color-content-primary)] mb-3">Sync Direction</h3>
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm text-[var(--color-content-secondary)]">
                  <input
                    type="radio"
                    name="syncDirection"
                    value="both"
                    checked={formState.syncDirection === 'both'}
                    onChange={handleSyncDirectionChange}
                    disabled={!isConnected || loading}
                    className="w-4 h-4 text-[var(--color-status-info)] focus:ring-[var(--color-status-info)]"
                  />
                  <span className="font-medium">Bi-directional sync</span>
                </label>
                <label className="flex items-center gap-2 text-sm text-[var(--color-content-secondary)]">
                  <input
                    type="radio"
                    name="syncDirection"
                    value="pull"
                    checked={formState.syncDirection === 'pull'}
                    onChange={handleSyncDirectionChange}
                    disabled={!isConnected || loading}
                    className="w-4 h-4 text-[var(--color-status-info)] focus:ring-[var(--color-status-info)]"
                  />
                  <span className="font-medium">Pull from GitHub</span>
                </label>
                <label className="flex items-center gap-2 text-sm text-[var(--color-content-secondary)]">
                  <input
                    type="radio"
                    name="syncDirection"
                    value="push"
                    checked={formState.syncDirection === 'push'}
                    onChange={handleSyncDirectionChange}
                    disabled={!isConnected || loading}
                    className="w-4 h-4 text-[var(--color-status-info)] focus:ring-[var(--color-status-info)]"
                  />
                  <span className="font-medium">Push to GitHub</span>
                </label>
              </div>
            </div>

            <div className="bg-[var(--color-surface-inset)]/50 rounded-lg p-4 border border-[var(--color-border-default)] space-y-4">
              <div>
                <h3 className="text-sm font-bold text-[var(--color-content-primary)] mb-3">Automation Options</h3>
              </div>
              <div>
                <label className="flex items-center gap-2 text-sm text-[var(--color-content-secondary)]">
                  <input
                    type="checkbox"
                    name="autoSync"
                    checked={formState.autoSync}
                    onChange={handleCheckboxChange}
                    disabled={!isConnected || loading}
                    className="w-4 h-4 rounded border-[var(--color-border-strong)] text-[var(--color-status-info)] focus:ring-[var(--color-status-info)]"
                  />
                  <span className="font-medium">Automatic sync</span>
                </label>
                <p className="text-xs text-[var(--color-content-secondary)] mt-1 ml-6">
                  Automatically sync when new test runs complete or when GitHub issues change
                </p>
              </div>

              <div>
                <label className="flex items-center gap-2 text-sm text-[var(--color-content-secondary)]">
                  <input
                    type="checkbox"
                    name="createIssues"
                    checked={formState.createIssues}
                    onChange={handleCheckboxChange}
                    disabled={!isConnected || loading}
                    className="w-4 h-4 rounded border-[var(--color-border-strong)] text-[var(--color-status-info)] focus:ring-[var(--color-status-info)]"
                  />
                  <span className="font-medium">Create GitHub issues for failed tests</span>
                </label>
                <p className="text-xs text-[var(--color-content-secondary)] mt-1 ml-6">
                  Automatically create GitHub issues whenever tests fail during suite execution
                </p>
              </div>
            </div>

            <hr className="border-[var(--color-border-default)]" />

            <div className="flex flex-col sm:flex-row gap-4 items-center">
              {saveSuccess && (
                <div className="flex-1 bg-[var(--color-status-success-bg)] border border-[var(--color-status-success)] rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-[var(--color-status-success)]" />
                    <p className="text-sm font-medium text-[var(--color-status-success)]">Sync settings updated successfully</p>
                  </div>
                </div>
              )}
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={!isConnected || savingSettings || loading || !formState.repository}
                  className="px-6 py-3 rounded-lg text-sm font-semibold text-white transition-all hover:shadow-lg hover:-translate-y-0.5 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
                >
                  {savingSettings ? 'Saving...' : 'Save Settings'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default GitHubIntegrationPage;
