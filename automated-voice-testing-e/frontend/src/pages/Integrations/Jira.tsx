import { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, AlertCircle, Trash2 } from 'lucide-react';
import { SiJira } from 'react-icons/si';
import type { AppDispatch, RootState } from '../../store';
import {
  clearJiraIntegrationError,
  clearJiraIntegrationSuccess,
  fetchJiraIntegrationConfig,
  saveJiraIntegrationConfig,
  type JiraIntegrationState,
  type JiraIntegrationUpdatePayload,
} from '../../store/slices/jiraIntegrationSlice';

interface ProjectRow {
  id: string;
  mappingId: string;
  projectKey: string;
  issueType: string;
  browseUrl: string;
}

const emptyRow = (suffix: number): ProjectRow => ({
  id: `new-${suffix}`,
  mappingId: '',
  projectKey: '',
  issueType: '',
  browseUrl: '',
});

const buildRows = (mapping: JiraIntegrationState['config']['projectMapping']): ProjectRow[] => {
  const entries = Object.entries(mapping || {});
  if (entries.length === 0) {
    return [emptyRow(0)];
  }

  return entries.map(([mappingId, value], index) => ({
    id: `${mappingId}-${index}`,
    mappingId,
    projectKey: value.projectKey ?? '',
    issueType: value.issueType ?? '',
    browseUrl: value.browseUrl ?? '',
  }));
};

const JiraIntegrationPage = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { config, loading, saving, error, success } = useSelector<RootState, JiraIntegrationState>(
    (state) => state.jiraIntegration
  );

  const [formState, setFormState] = useState({
    baseUrl: config.baseUrl,
    browseUrl: config.browseUrl,
    userEmail: config.userEmail,
    apiToken: '',
    autoCreateTickets: config.autoCreateTickets ?? false,
  });
  const [projectRows, setProjectRows] = useState<ProjectRow[]>(() => buildRows(config.projectMapping));

  const hasConfiguredToken = config.apiTokenSet;

  useEffect(() => {
    dispatch(fetchJiraIntegrationConfig());
  }, [dispatch]);

  useEffect(() => {
    setFormState({
      baseUrl: config.baseUrl,
      browseUrl: config.browseUrl,
      userEmail: config.userEmail,
      apiToken: '',
      autoCreateTickets: config.autoCreateTickets ?? false,
    });
    setProjectRows(buildRows(config.projectMapping));
  }, [config.baseUrl, config.browseUrl, config.userEmail, config.projectMapping, config.apiTokenSet, config.autoCreateTickets]);

  const projectRowCount = useMemo(() => projectRows.length, [projectRows]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setFormState((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = event.target;
    setFormState((current) => ({
      ...current,
      [name]: checked,
    }));
  };

  const handleProjectFieldChange = (rowId: string, field: keyof ProjectRow, value: string) => {
    setProjectRows((rows) =>
      rows.map((row) => (row.id === rowId ? { ...row, [field]: value } : row))
    );
  };

  const handleAddRow = () => {
    setProjectRows((rows) => [...rows, emptyRow(rows.length + 1)]);
  };

  const handleRemoveRow = (rowId: string) => {
    setProjectRows((rows) => {
      const filtered = rows.filter((row) => row.id !== rowId);
      return filtered.length === 0 ? [emptyRow(Date.now())] : filtered;
    });
  };

  const handleDismissError = () => {
    dispatch(clearJiraIntegrationError());
  };

  const handleDismissSuccess = () => {
    dispatch(clearJiraIntegrationSuccess());
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const projectMapping = projectRows.reduce<Record<string, { projectKey: string; issueType: string; browseUrl?: string }>>(
      (acc, row) => {
        const mappingId = row.mappingId.trim();
        const projectKey = row.projectKey.trim();
        if (!mappingId || !projectKey) {
          return acc;
        }
        const entry: { projectKey: string; issueType: string; browseUrl?: string } = {
          projectKey,
          issueType: row.issueType.trim() || 'Bug',
        };
        const browseUrl = row.browseUrl.trim();
        if (browseUrl) {
          entry.browseUrl = browseUrl;
        }
        acc[mappingId] = entry;
        return acc;
      },
      {}
    );

    const payload: JiraIntegrationUpdatePayload = {
      baseUrl: formState.baseUrl.trim(),
      browseUrl: formState.browseUrl.trim(),
      userEmail: formState.userEmail.trim(),
      projectMapping,
      autoCreateTickets: formState.autoCreateTickets,
    };

    if (config.timeoutSeconds != null) {
      payload.timeoutSeconds = config.timeoutSeconds;
    }

    const apiToken = formState.apiToken.trim();
    if (apiToken) {
      payload.apiToken = apiToken;
    }

    try {
      await dispatch(saveJiraIntegrationConfig(payload)).unwrap();
      setFormState((current) => ({
        ...current,
        apiToken: '',
      }));
    } catch {
      // Errors handled via slice state; no-op.
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
            <div className="p-2.5 bg-[var(--color-status-info)] rounded-lg shadow-lg">
              <SiJira className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[var(--color-content-primary)]">Jira Integration</h1>
              <p className="text-sm text-[var(--color-content-secondary)] mt-1">
                Configure Jira connection to synchronize defects and issue status updates
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

        {/* Main Configuration Form */}
        <form onSubmit={handleSubmit} className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md border border-[var(--color-border-default)] space-y-6">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-[var(--color-content-primary)]">Connection Settings</h2>
              <div className="flex items-center gap-2">
                {hasConfiguredToken ? (
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
            {hasConfiguredToken && (
              <p className="text-sm text-[var(--color-content-secondary)]">
                An API token is already configured. Provide a new token to rotate credentials.
              </p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="baseUrl" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Jira REST API URL *
              </label>
              <input
                type="text"
                id="baseUrl"
                name="baseUrl"
                value={formState.baseUrl}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
              />
            </div>
            <div>
              <label htmlFor="browseUrl" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Jira browse URL
              </label>
              <input
                type="text"
                id="browseUrl"
                name="browseUrl"
                value={formState.browseUrl}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
              />
            </div>
            <div>
              <label htmlFor="userEmail" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Jira user email *
              </label>
              <input
                type="email"
                id="userEmail"
                name="userEmail"
                value={formState.userEmail}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
              />
            </div>
            <div>
              <label htmlFor="apiToken" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                API token
              </label>
              <input
                type="password"
                id="apiToken"
                name="apiToken"
                value={formState.apiToken}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
              />
            </div>
          </div>

          <hr className="border-[var(--color-border-default)]" />

          <div className="bg-[var(--color-surface-inset)]/50 rounded-lg p-4 space-y-4 border border-[var(--color-border-default)]">
            <div>
              <h3 className="font-bold text-[var(--color-content-primary)] mb-1">Automation Settings</h3>
              <p className="text-xs text-[var(--color-content-secondary)]">Configure automatic ticket creation</p>
            </div>
            <div>
              <label className="flex items-center gap-2 text-[var(--color-content-secondary)]">
                <input
                  type="checkbox"
                  name="autoCreateTickets"
                  checked={formState.autoCreateTickets}
                  onChange={handleCheckboxChange}
                  className="w-4 h-4 rounded border-[var(--color-border-strong)] text-[var(--color-status-info)] focus:ring-[var(--color-status-info)]"
                />
                <span className="text-sm font-medium">Auto-create Jira tickets for test failures</span>
              </label>
              <p className="text-xs text-[var(--color-content-secondary)] mt-2 ml-6">
                Automatically create Jira tickets whenever tests fail during suite execution
              </p>
            </div>
          </div>

          <hr className="border-[var(--color-border-default)]" />

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-[var(--color-content-primary)] mb-1">Project Mappings</h3>
                <p className="text-xs text-[var(--color-content-secondary)]">
                  Define how defect categories map to Jira projects and issue types
                </p>
              </div>
              <button
                type="button"
                onClick={handleAddRow}
                className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:shadow-lg hover:-translate-y-0.5 active:scale-95"
                style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
              >
                Add Mapping
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {projectRows.map((row) => (
              <div key={row.id} className="border border-[var(--color-border-default)] bg-[var(--color-surface-inset)]/50 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">Mapping ID</label>
                    <input
                      type="text"
                      value={row.mappingId}
                      onChange={(event) =>
                        handleProjectFieldChange(row.id, 'mappingId', event.target.value)
                      }
                      className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">Project key</label>
                    <input
                      type="text"
                      value={row.projectKey}
                      onChange={(event) =>
                        handleProjectFieldChange(row.id, 'projectKey', event.target.value)
                      }
                      className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">Issue type</label>
                    <input
                      type="text"
                      value={row.issueType}
                      onChange={(event) =>
                        handleProjectFieldChange(row.id, 'issueType', event.target.value)
                      }
                      className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">Browse URL</label>
                    <input
                      type="text"
                      value={row.browseUrl}
                      onChange={(event) =>
                        handleProjectFieldChange(row.id, 'browseUrl', event.target.value)
                      }
                      className="w-full px-3 py-2 border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-status-info)]"
                    />
                  </div>
                </div>
                {projectRowCount > 1 && (
                  <div className="flex justify-end mt-4">
                    <button
                      type="button"
                      onClick={() => handleRemoveRow(row.id)}
                      className="text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)] flex items-center gap-2"
                    >
                      <Trash2 className="w-4 h-4" />
                      Remove
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="flex justify-end pt-4 border-t border-[var(--color-border-default)]">
            <button
              type="submit"
              disabled={saving || loading}
              className="px-6 py-3 rounded-lg text-sm font-semibold text-white transition-all hover:shadow-lg hover:-translate-y-0.5 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
            >
              {saving ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default JiraIntegrationPage;
