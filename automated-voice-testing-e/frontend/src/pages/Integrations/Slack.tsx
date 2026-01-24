import { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, AlertCircle } from 'lucide-react';
import { SiSlack } from 'react-icons/si';
import type { AppDispatch, RootState } from '../../store';
import {
  clearSlackIntegrationError,
  clearSlackIntegrationSuccess,
  disconnectSlackIntegration,
  fetchSlackIntegrationConfig,
  saveSlackIntegrationConfig,
  type SlackIntegrationState,
  type SlackIntegrationUpdatePayload,
} from '../../store/slices/slackIntegrationSlice';

type PreferenceKey = keyof SlackIntegrationState['config']['notificationPreferences'];

const SlackIntegrationPage = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { config, loading, saving, disconnecting, error, success } = useSelector<
    RootState,
    SlackIntegrationState
  >((state) => state.slackIntegration);

  const [formState, setFormState] = useState(() => ({
    defaultChannel: config.defaultChannel,
    webhookUrl: '',
    notificationPreferences: {
      suiteRun: { ...config.notificationPreferences.suiteRun },
      criticalDefect: { ...config.notificationPreferences.criticalDefect },
      systemAlert: { ...config.notificationPreferences.systemAlert },
      edgeCase: { ...config.notificationPreferences.edgeCase },
    },
  }));

  useEffect(() => {
    dispatch(fetchSlackIntegrationConfig());
  }, [dispatch]);

  useEffect(() => {
    setFormState((prev) => ({
      ...prev,
      defaultChannel: config.defaultChannel,
      // Don't reset webhookUrl - it's a sensitive field not returned from API
      notificationPreferences: {
        suiteRun: { ...config.notificationPreferences.suiteRun },
        criticalDefect: { ...config.notificationPreferences.criticalDefect },
        systemAlert: { ...config.notificationPreferences.systemAlert },
        edgeCase: { ...config.notificationPreferences.edgeCase },
      },
    }));
  }, [
    config.defaultChannel,
    config.notificationPreferences.suiteRun,
    config.notificationPreferences.criticalDefect,
    config.notificationPreferences.systemAlert,
    config.notificationPreferences.edgeCase,
  ]);

  const isFormDisabled = useMemo(() => loading || saving || disconnecting, [loading, saving, disconnecting]);

  const handleDismissError = () => {
    dispatch(clearSlackIntegrationError());
  };

  const handleDismissSuccess = () => {
    dispatch(clearSlackIntegrationSuccess());
  };

  const handleToggleChange = (preference: PreferenceKey) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const enabled = event.target.checked;
    setFormState((previous) => ({
      ...previous,
      notificationPreferences: {
        ...previous.notificationPreferences,
        [preference]: {
          ...previous.notificationPreferences[preference],
          enabled,
        },
      },
    }));
  };

  const handleChannelChange = (preference: PreferenceKey) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const channel = event.target.value;
    setFormState((previous) => ({
      ...previous,
      notificationPreferences: {
        ...previous.notificationPreferences,
        [preference]: {
          ...previous.notificationPreferences[preference],
          channel,
        },
      },
    }));
  };

  const handleDefaultChannelChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = event.target;
    setFormState((previous) => ({
      ...previous,
      defaultChannel: value,
    }));
  };

  const handleWebhookUrlChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = event.target;
    setFormState((previous) => ({
      ...previous,
      webhookUrl: value,
    }));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const payload: SlackIntegrationUpdatePayload = {
      defaultChannel: formState.defaultChannel.trim(),
      notificationPreferences: {
        suiteRun: {
          enabled: formState.notificationPreferences.suiteRun.enabled,
          channel: formState.notificationPreferences.suiteRun.channel.trim(),
        },
        criticalDefect: {
          enabled: formState.notificationPreferences.criticalDefect.enabled,
          channel: formState.notificationPreferences.criticalDefect.channel.trim(),
        },
        systemAlert: {
          enabled: formState.notificationPreferences.systemAlert.enabled,
          channel: formState.notificationPreferences.systemAlert.channel.trim(),
        },
        edgeCase: {
          enabled: formState.notificationPreferences.edgeCase.enabled,
          channel: formState.notificationPreferences.edgeCase.channel.trim(),
        },
      },
    };

    // Only include webhookUrl if user entered one (it's a sensitive field)
    if (formState.webhookUrl.trim()) {
      payload.webhookUrl = formState.webhookUrl.trim();
    }

    try {
      await dispatch(saveSlackIntegrationConfig(payload)).unwrap();
      // Clear webhook URL field after successful save for security
      if (formState.webhookUrl.trim()) {
        setFormState((prev) => ({ ...prev, webhookUrl: '' }));
      }
    } catch {
      // Slice state handles error display.
    }
  };

  const handleDisconnect = async () => {
    try {
      await dispatch(disconnectSlackIntegration()).unwrap();
    } catch {
      // Slice state handles error display.
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
            <div className="p-2.5 bg-[var(--color-status-purple)] rounded-lg shadow-lg">
              <SiSlack className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[var(--color-content-primary)]">Slack Integration</h1>
              <p className="text-sm text-[var(--color-content-secondary)] mt-1">
                Connect Slack to broadcast automated testing updates to your team channels
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4 flex items-start justify-between">
            <p className="text-[var(--color-status-danger)]">{error}</p>
            <button onClick={handleDismissError} className="text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)]">
              Dismiss
            </button>
          </div>
        )}

        {success && (
          <div className="bg-[var(--color-status-success-bg)] border border-[var(--color-status-success)] rounded-lg p-4 flex items-start justify-between">
            <p className="text-[var(--color-status-success)]">{success}</p>
            <button onClick={handleDismissSuccess} className="text-[var(--color-status-success)] hover:text-[var(--color-status-success)]">
              Dismiss
            </button>
          </div>
        )}

        {/* Workspace Connection Card */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md border border-[var(--color-border-default)]">
          <div className="flex gap-4 items-start">
            <div className="w-16 h-16 rounded-full bg-[var(--color-interactive-active)] flex items-center justify-center text-2xl font-bold text-[var(--color-content-secondary)] flex-shrink-0">
              {config.workspaceIconUrl ? (
                <img src={config.workspaceIconUrl} alt={config.workspaceName ?? 'Slack workspace'} className="w-16 h-16 rounded-full" />
              ) : (
                config.workspaceName?.charAt(0) ?? 'S'
              )}
            </div>
            <div className="flex-1">
              <h2 className="text-lg font-bold text-[var(--color-content-primary)] mb-2">Workspace Connection</h2>
              <div className="flex items-center gap-2 mb-4">
                {config.isConnected ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-[var(--color-status-success)]" />
                    <p className="text-sm font-semibold text-[var(--color-status-success)]">
                      Connected {config.workspaceName ? `to ${config.workspaceName}` : ''}
                    </p>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-4 h-4 text-[var(--color-status-warning)]" />
                    <p className="text-sm font-semibold text-[var(--color-status-warning)]">
                      Not Connected
                    </p>
                  </>
                )}
              </div>
              {!config.isConnected && (
                <p className="text-sm text-[var(--color-content-secondary)]">
                  Add a webhook URL below to enable Slack notifications for your team.
                </p>
              )}
            </div>
          </div>
          <hr className="my-4 border-[var(--color-border-default)]" />

          <div className="space-y-4">
            <div>
              <label htmlFor="webhookUrl" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Slack Webhook URL
              </label>
              <input
                type="password"
                id="webhookUrl"
                value={formState.webhookUrl}
                onChange={handleWebhookUrlChange}
                disabled={isFormDisabled}
                placeholder={config.isConnected ? '(webhook configured - enter new URL to update)' : 'https://hooks.slack.com/services/...'}
                className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
              />
              <p className="text-sm text-[var(--color-content-muted)] mt-1">
                Create an incoming webhook in your Slack workspace settings.
                <a
                  href="https://api.slack.com/messaging/webhooks"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[var(--color-status-info)] hover:underline ml-1"
                >
                  Learn more
                </a>
              </p>
            </div>
          </div>

          {config.isConnected && (
            <>
              <hr className="my-4 border-[var(--color-border-default)]" />
              <div className="flex items-center justify-end">
                <button
                  onClick={handleDisconnect}
                  disabled={isFormDisabled}
                  className="text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)]"
                >
                  Disconnect workspace
                </button>
              </div>
            </>
          )}
        </div>

        {/* Notification Settings Form */}
        <form onSubmit={handleSubmit} className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md border border-[var(--color-border-default)] space-y-6">
          <div>
            <h2 className="text-lg font-bold text-[var(--color-content-primary)] mb-1">Notification Settings</h2>
            <p className="text-sm text-[var(--color-content-secondary)]">
              Configure which Slack channels receive automated updates
            </p>
          </div>

          <div>
            <label htmlFor="defaultChannel" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
              Default notification channel
            </label>
            <input
              type="text"
              id="defaultChannel"
              name="defaultChannel"
              value={formState.defaultChannel}
              onChange={handleDefaultChannelChange}
              disabled={isFormDisabled}
              className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-sm text-[var(--color-content-secondary)] mt-1">
              Used when a specific notification channel is not provided.
            </p>
          </div>

          <hr className="border-[var(--color-border-default)]" />

          {/* Suite Run Notifications */}
          <div className="bg-[var(--color-surface-inset)]/50 rounded-lg p-4 space-y-4 border border-[var(--color-border-default)]">
            <div>
              <h3 className="font-bold text-[var(--color-content-primary)] mb-1">Suite Run Completion</h3>
              <p className="text-xs text-[var(--color-content-secondary)]">Get notified when test suites finish running</p>
            </div>
            <label className="flex items-center gap-2 text-[var(--color-content-secondary)]">
              <input
                type="checkbox"
                checked={formState.notificationPreferences.suiteRun.enabled}
                onChange={handleToggleChange('suiteRun')}
                disabled={isFormDisabled}
                className="w-4 h-4 text-[var(--color-status-info)] bg-[var(--color-surface-inset)] border-[var(--color-border-default)] rounded focus:ring-[var(--color-status-info)]"
              />
              <span className="text-sm font-medium">Enable suite run notifications</span>
            </label>
            <div>
              <label htmlFor="suiteRunChannel" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Channel
              </label>
              <input
                type="text"
                id="suiteRunChannel"
                value={formState.notificationPreferences.suiteRun.channel}
                onChange={handleChannelChange('suiteRun')}
                disabled={isFormDisabled}
                placeholder="#test-results"
                className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
              />
            </div>
          </div>

          {/* Critical Defect Notifications */}
          <div className="bg-[var(--color-surface-inset)]/50 rounded-lg p-4 space-y-4 border border-[var(--color-border-default)]">
            <div>
              <h3 className="font-bold text-[var(--color-content-primary)] mb-1">Critical Defects</h3>
              <p className="text-xs text-[var(--color-content-secondary)]">Get notified when critical defects are detected</p>
            </div>
            <label className="flex items-center gap-2 text-[var(--color-content-secondary)]">
              <input
                type="checkbox"
                checked={formState.notificationPreferences.criticalDefect.enabled}
                onChange={handleToggleChange('criticalDefect')}
                disabled={isFormDisabled}
                className="w-4 h-4 text-[var(--color-status-info)] bg-[var(--color-surface-inset)] border-[var(--color-border-default)] rounded focus:ring-[var(--color-status-info)]"
              />
              <span className="text-sm font-medium">Enable critical defect notifications</span>
            </label>
            <div>
              <label htmlFor="criticalDefectChannel" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Channel
              </label>
              <input
                type="text"
                id="criticalDefectChannel"
                value={formState.notificationPreferences.criticalDefect.channel}
                onChange={handleChannelChange('criticalDefect')}
                disabled={isFormDisabled}
                placeholder="#critical-alerts"
                className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
              />
            </div>
          </div>

          {/* System Alert Notifications */}
          <div className="bg-[var(--color-surface-inset)]/50 rounded-lg p-4 space-y-4 border border-[var(--color-border-default)]">
            <div>
              <h3 className="font-bold text-[var(--color-content-primary)] mb-1">System Alerts</h3>
              <p className="text-xs text-[var(--color-content-secondary)]">Get notified about system-level events and issues</p>
            </div>
            <label className="flex items-center gap-2 text-[var(--color-content-secondary)]">
              <input
                type="checkbox"
                checked={formState.notificationPreferences.systemAlert.enabled}
                onChange={handleToggleChange('systemAlert')}
                disabled={isFormDisabled}
                className="w-4 h-4 text-[var(--color-status-info)] bg-[var(--color-surface-inset)] border-[var(--color-border-default)] rounded focus:ring-[var(--color-status-info)]"
              />
              <span className="text-sm font-medium">Enable system alert notifications</span>
            </label>
            <div>
              <label htmlFor="systemAlertChannel" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Channel
              </label>
              <input
                type="text"
                id="systemAlertChannel"
                value={formState.notificationPreferences.systemAlert.channel}
                onChange={handleChannelChange('systemAlert')}
                disabled={isFormDisabled}
                placeholder="#system-alerts"
                className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
              />
            </div>
          </div>

          {/* Edge Case Notifications */}
          <div className="bg-[var(--color-surface-inset)]/50 rounded-lg p-4 space-y-4 border border-[var(--color-border-default)]">
            <div>
              <h3 className="font-bold text-[var(--color-content-primary)] mb-1">Edge Case Discoveries</h3>
              <p className="text-xs text-[var(--color-content-secondary)]">
                Get notified when new high-severity edge cases are discovered during validation
              </p>
            </div>
            <label className="flex items-center gap-2 text-[var(--color-content-secondary)]">
              <input
                type="checkbox"
                checked={formState.notificationPreferences.edgeCase.enabled}
                onChange={handleToggleChange('edgeCase')}
                disabled={isFormDisabled}
                className="w-4 h-4 text-[var(--color-status-info)] bg-[var(--color-surface-inset)] border-[var(--color-border-default)] rounded focus:ring-[var(--color-status-info)]"
              />
              <span className="text-sm font-medium">Enable edge case notifications</span>
            </label>
            <div>
              <label htmlFor="edgeCaseChannel" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Channel
              </label>
              <input
                type="text"
                id="edgeCaseChannel"
                value={formState.notificationPreferences.edgeCase.channel}
                onChange={handleChannelChange('edgeCase')}
                disabled={isFormDisabled}
                placeholder="#edge-cases"
                className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
              />
              <p className="text-xs text-[var(--color-content-muted)] mt-2">
                Only critical and high severity edge cases trigger notifications by default
              </p>
            </div>
          </div>

          <hr className="border-[var(--color-border-default)]" />

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isFormDisabled}
              className="px-6 py-3 rounded-lg text-sm font-semibold text-white transition-all hover:shadow-lg hover:-translate-y-0.5 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
            >
              {saving ? 'Saving...' : config.isConnected ? 'Save Settings' : 'Connect and Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SlackIntegrationPage;
