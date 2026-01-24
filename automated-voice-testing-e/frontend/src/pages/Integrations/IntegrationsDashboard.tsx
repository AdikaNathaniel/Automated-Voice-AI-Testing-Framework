import { useEffect, useMemo } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Info, ArrowRight, Zap, Bell, CheckCircle2, AlertCircle, Activity, RefreshCw } from 'lucide-react';
import { SiSlack, SiJira, SiGithub } from 'react-icons/si';
import type { AppDispatch, RootState } from '../../store';
import {
  fetchSlackIntegrationConfig,
  type SlackIntegrationState,
} from '../../store/slices/slackIntegrationSlice';
import {
  fetchJiraIntegrationConfig,
  type JiraIntegrationState,
} from '../../store/slices/jiraIntegrationSlice';
import {
  fetchGitHubIntegrationStatus,
  type GitHubIntegrationState,
} from '../../store/slices/githubIntegrationSlice';
import {
  fetchIntegrationHealth,
  type IntegrationHealthState,
} from '../../store/slices/integrationHealthSlice';
import IntegrationLogs from '../../components/Integrations/IntegrationLogs';
import IntegrationHealthCard from '../../components/Integrations/IntegrationHealthCard';

const IntegrationsDashboard = () => {
  const dispatch = useDispatch<AppDispatch>();
  const slack = useSelector<RootState, SlackIntegrationState>((state) => state.slackIntegration);
  const jira = useSelector<RootState, JiraIntegrationState>((state) => state.jiraIntegration);
  const github = useSelector<RootState, GitHubIntegrationState>((state) => state.githubIntegration);
  const integrationHealth = useSelector<RootState, IntegrationHealthState>((state) => state.integrationHealth);

  useEffect(() => {
    void dispatch(fetchSlackIntegrationConfig());
    void dispatch(fetchJiraIntegrationConfig());
    void dispatch(fetchGitHubIntegrationStatus());
    void dispatch(fetchIntegrationHealth());
  }, [dispatch]);

  const handleRefreshHealth = () => {
    void dispatch(fetchIntegrationHealth());
  };

  const isLoading = slack.loading || jira.loading || github.loading;
  const errors = useMemo(
    () => [slack.error, jira.error, github.error].filter((value): value is string => Boolean(value)),
    [slack.error, jira.error, github.error]
  );

  return (
    <>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <Zap className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            Integrations Dashboard
          </h1>
          <p className="text-sm text-[var(--color-content-secondary)] mt-1">
            Monitor connection status and configure external integrations for automated workflows
          </p>
        </div>
      </div>

      {/* Explanation Banner */}
      <div className="bg-gradient-to-r from-[var(--color-status-info-bg)] to-[var(--color-status-indigo-bg)] rounded-xl p-6 mb-6 border border-[var(--color-status-info-bg)]">
        <div className="flex items-start gap-4">
          <div className="p-2 bg-[var(--color-status-info-bg)]/50 rounded-lg">
            <Info className="w-6 h-6 text-[var(--color-status-info)]" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">
              How Integrations Work
            </h3>
            <p className="text-sm text-[var(--color-content-secondary)] mb-4">
              Integrations handle <strong>outgoing</strong> actions after your tests complete. They work alongside CI/CD webhooks to create a complete automated testing workflow.
            </p>

            {/* Visual Flow */}
            <div className="bg-[var(--color-surface-raised)] rounded-lg p-4 mb-4">
              <div className="flex items-center justify-between gap-2 flex-wrap">
                <div className="flex items-center gap-2 min-w-[140px]">
                  <div className="p-2 bg-[var(--color-surface-inset)] rounded">
                    <Zap className="w-4 h-4 text-[var(--color-content-secondary)]" />
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-[var(--color-content-primary)]">CI/CD Webhooks</div>
                    <div className="text-xs text-[var(--color-content-muted)]">Trigger tests</div>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-[var(--color-content-muted)]" />
                <div className="flex items-center gap-2 min-w-[140px]">
                  <div className="p-2 bg-[var(--color-status-success-bg)] rounded">
                    <Zap className="w-4 h-4 text-[var(--color-status-success)]" />
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-[var(--color-content-primary)]">Tests Run</div>
                    <div className="text-xs text-[var(--color-content-muted)]">Suite executes</div>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-[var(--color-content-muted)]" />
                <div className="flex items-center gap-2 min-w-[140px]">
                  <div className="p-2 bg-gradient-to-r from-[#2A6B6E] to-[#11484D] rounded">
                    <Bell className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-[var(--color-content-primary)]">Integrations Fire</div>
                    <div className="text-xs text-[var(--color-content-muted)]">Report results</div>
                  </div>
                </div>
              </div>
            </div>

            {/* What each integration does */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="bg-[var(--color-surface-raised)] rounded-lg p-3 border border-[var(--color-border-default)]">
                <div className="flex items-center gap-2 mb-2">
                  <div className="p-1.5 bg-[var(--color-interactive-hover)] rounded">
                    <SiGithub className="w-4 h-4 text-white" />
                  </div>
                  <h4 className="text-xs font-semibold text-[var(--color-content-primary)]">GitHub</h4>
                </div>
                <p className="text-xs text-[var(--color-content-secondary)]">
                  Auto-creates <strong>issues</strong> when tests fail
                </p>
              </div>
              <div className="bg-[var(--color-surface-raised)] rounded-lg p-3 border border-[var(--color-border-default)]">
                <div className="flex items-center gap-2 mb-2">
                  <div className="p-1.5 bg-[var(--color-status-info)] rounded">
                    <SiJira className="w-4 h-4 text-white" />
                  </div>
                  <h4 className="text-xs font-semibold text-[var(--color-content-primary)]">Jira</h4>
                </div>
                <p className="text-xs text-[var(--color-content-secondary)]">
                  Auto-creates <strong>tickets</strong> for defects
                </p>
              </div>
              <div className="bg-[var(--color-surface-raised)] rounded-lg p-3 border border-[var(--color-border-default)]">
                <div className="flex items-center gap-2 mb-2">
                  <div className="p-1.5 bg-[var(--color-status-purple)] rounded">
                    <SiSlack className="w-4 h-4 text-white" />
                  </div>
                  <h4 className="text-xs font-semibold text-[var(--color-content-primary)]">Slack</h4>
                </div>
                <p className="text-xs text-[var(--color-content-secondary)]">
                  Sends <strong>notifications</strong> to your team
                </p>
              </div>
            </div>

            {/* Setup Tip */}
            <div className="mt-4 p-3 bg-[var(--color-status-info-bg)] rounded-lg border border-[var(--color-status-info-bg)]">
              <p className="text-xs text-[var(--color-status-info)]">
                <strong>Setup Tip:</strong> Configure <RouterLink to="/cicd-config" className="underline hover:text-[var(--color-status-info)]">CI/CD Webhooks</RouterLink> first to trigger tests, then configure integrations here to handle the results.
              </p>
            </div>
          </div>
        </div>
      </div>

      {isLoading && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
          <div className="flex flex-col items-center justify-center p-20">
            <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#2A6B6E' }}></div>
            <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Integrations...</div>
          </div>
        </div>
      )}

      {errors.length > 0 && (
        <div className="p-4 rounded-lg flex items-center gap-3 bg-danger-light  text-[var(--color-status-danger)] border-l-4 border-danger mb-5">
          <div className="text-xl">⚠️</div>
          <div className="flex-1">
            <div className="font-semibold">{errors[0]}</div>
          </div>
        </div>
      )}

      {/* Integration Health Status Section */}
      {integrationHealth.health && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5" style={{ color: '#2A6B6E' }} />
              <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">
                Integration Health
              </h2>
              {integrationHealth.health.overallStatus !== 'healthy' &&
                integrationHealth.health.overallStatus !== 'unconfigured' && (
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                      integrationHealth.health.overallStatus === 'critical'
                        ? 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]'
                        : 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]'
                    }`}
                  >
                    {integrationHealth.health.overallStatus === 'critical'
                      ? 'Issues Detected'
                      : 'Attention Needed'}
                  </span>
                )}
            </div>
            <button
              onClick={handleRefreshHealth}
              disabled={integrationHealth.loading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-[var(--color-content-secondary)] bg-[var(--color-surface-inset)] hover:bg-[var(--color-interactive-hover)] transition-colors disabled:opacity-50"
            >
              <RefreshCw
                className={`w-4 h-4 ${integrationHealth.loading ? 'animate-spin' : ''}`}
              />
              Refresh
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <IntegrationHealthCard
              title="Slack"
              icon={<SiSlack className="w-5 h-5" />}
              iconBgColor="bg-[var(--color-status-purple)]"
              health={integrationHealth.health.slack}
              configPath="/integrations/slack"
            />
            <IntegrationHealthCard
              title="Jira"
              icon={<SiJira className="w-5 h-5" />}
              iconBgColor="bg-[var(--color-status-info)]"
              health={integrationHealth.health.jira}
              configPath="/integrations/jira"
            />
            <IntegrationHealthCard
              title="GitHub"
              icon={<SiGithub className="w-5 h-5" />}
              iconBgColor="bg-[var(--color-interactive-hover)]"
              health={integrationHealth.health.github}
              configPath="/integrations/github"
            />
          </div>
          {integrationHealth.lastFetched && (
            <p className="text-xs text-[var(--color-content-muted)] mt-2 text-right">
              Last checked: {new Date(integrationHealth.lastFetched).toLocaleTimeString()}
            </p>
          )}
        </div>
      )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <IntegrationCard
            icon={<SiSlack className="w-6 h-6" />}
            iconBgColor="bg-[var(--color-status-purple)]"
            title="Slack"
            description="Team notifications and alerts."
            status={slack.config.isConnected ? 'Connected' : 'Not connected'}
            statusColor={slack.config.isConnected ? 'success' : 'warning'}
            details={
              <div className="space-y-2">
                <p className="text-sm text-[var(--color-content-secondary)]">
                  <span className="font-medium text-[var(--color-content-secondary)]">Workspace:</span> {slack.config.workspaceName ?? '—'}
                </p>
                <p className="text-sm text-[var(--color-content-secondary)]">
                  <span className="font-medium text-[var(--color-content-secondary)]">Default channel:</span> {slack.config.defaultChannel || '—'}
                </p>
                <p className="text-sm text-[var(--color-content-secondary)]">
                  <span className="font-medium text-[var(--color-content-secondary)]">Suite run alerts:</span> {slack.config.notificationPreferences.suiteRun.enabled ? slack.config.notificationPreferences.suiteRun.channel || 'Enabled' : 'Disabled'}
                </p>
              </div>
            }
            managePath="/integrations/slack"
            manageLabel="Manage Slack"
          />

          <IntegrationCard
            icon={<SiJira className="w-6 h-6" />}
            iconBgColor="bg-[var(--color-status-info)]"
            title="Jira"
            description="Defect tracking and synchronisation."
            status={jira.config.apiTokenSet ? 'Connected' : 'Not connected'}
            statusColor={jira.config.apiTokenSet ? 'success' : 'warning'}
            details={
              <div className="space-y-2">
                <p className="text-sm text-[var(--color-content-secondary)]">
                  <span className="font-medium text-[var(--color-content-secondary)]">Base URL:</span> {jira.config.baseUrl || '—'}
                </p>
                <p className="text-sm text-[var(--color-content-secondary)]">
                  <span className="font-medium text-[var(--color-content-secondary)]">User:</span> {jira.config.userEmail || '—'}
                </p>
                <p className="text-sm text-[var(--color-content-secondary)]">
                  <span className="font-medium text-[var(--color-content-secondary)]">Auto-create tickets:</span> {jira.config.autoCreateTickets ? 'Enabled' : 'Disabled'}
                </p>
                <p className="text-sm text-[var(--color-content-secondary)]">
                  <span className="font-medium text-[var(--color-content-secondary)]">Project mappings:</span> {Object.keys(jira.config.projectMapping || {}).length}
                </p>
              </div>
            }
            managePath="/integrations/jira"
            manageLabel="Manage Jira"
          />

          <IntegrationCard
            icon={<SiGithub className="w-6 h-6" />}
            iconBgColor="bg-[var(--color-interactive-hover)]"
            title="GitHub"
            description="Repository sync and automatic issue creation."
            status={github.isConnected ? 'Connected' : 'Not connected'}
            statusColor={github.isConnected ? 'success' : 'warning'}
            details={
              <div className="space-y-2">
                <p className="text-sm text-[var(--color-content-secondary)]">
                  <span className="font-medium text-[var(--color-content-secondary)]">Account:</span> {github.account?.login ?? '—'}
                </p>
                <p className="text-sm text-[var(--color-content-secondary)]">
                  <span className="font-medium text-[var(--color-content-secondary)]">Repository:</span> {github.syncSettings.repository || '—'}
                </p>
                <p className="text-sm text-[var(--color-content-secondary)]">
                  <span className="font-medium text-[var(--color-content-secondary)]">Auto-create issues:</span> {github.syncSettings.createIssues ? 'Enabled' : 'Disabled'}
                </p>
              </div>
            }
            managePath="/integrations/github"
            manageLabel="Manage GitHub"
          />
        </div>

        <div className="mt-6">
          <IntegrationLogs />
        </div>
      </>
  );
};

interface IntegrationCardProps {
  icon: React.ReactNode;
  iconBgColor: string;
  title: string;
  description: string;
  status: string;
  statusColor: 'success' | 'warning';
  details: React.ReactNode;
  managePath: string;
  manageLabel: string;
}

const IntegrationCard = ({
  icon,
  iconBgColor,
  title,
  description,
  status,
  statusColor,
  details,
  managePath,
  manageLabel,
}: IntegrationCardProps) => (
  <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md hover:shadow-xl border border-[var(--color-border-default)] hover:-translate-y-1 transition-all duration-300 h-full flex flex-col">
    <div className="flex-1 space-y-4">
      {/* Header with Icon */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={`${iconBgColor} p-3 rounded-lg shadow-sm`}>
            <div className="text-white">
              {icon}
            </div>
          </div>
          <div>
            <h2 className="text-lg font-bold text-[var(--color-content-primary)]">{title}</h2>
            <p className="text-sm text-[var(--color-content-secondary)] mt-0.5">{description}</p>
          </div>
        </div>
      </div>

      {/* Status Badge */}
      <div className="flex items-center gap-2">
        {statusColor === 'success' ? (
          <CheckCircle2 className="w-4 h-4 text-[var(--color-status-success)]" />
        ) : (
          <AlertCircle className="w-4 h-4 text-[var(--color-status-warning)]" />
        )}
        <span className={`text-sm font-semibold ${statusColor === 'success' ? 'text-[var(--color-status-success)]' : 'text-[var(--color-status-warning)]'}`}>
          {status}
        </span>
      </div>

      <hr className="border-[var(--color-border-default)]" />

      {/* Details */}
      <div className="space-y-2">
        {details}
      </div>
    </div>

    {/* Action Button */}
    <div className="mt-6 pt-4 border-t border-[var(--color-border-default)]">
      <RouterLink
        to={managePath}
        className="w-full block text-center px-6 py-3 rounded-lg text-sm font-semibold transition-all text-white hover:shadow-lg hover:-translate-y-0.5 active:scale-95"
        style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
      >
        {manageLabel}
      </RouterLink>
    </div>
  </div>
);

export default IntegrationsDashboard;
