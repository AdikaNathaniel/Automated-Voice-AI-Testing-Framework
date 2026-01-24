/**
 * ConfigurationEditor Page
 *
 * Provides a Monaco-powered JSON editor for updating configuration payloads with
 * client-side validation and basic metadata controls.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { ArrowLeft, Save, AlertCircle, XCircle, Settings } from 'lucide-react';

import {
  getConfiguration,
  updateConfiguration,
} from '../../services/configuration.service';
import ActivationToggle from '../../components/Configuration/ActivationToggle';
import type { ConfigurationDetail } from '../../types/configuration';

const CONFIG_EDITOR_HEIGHT = '420px';

const formatJson = (value: Record<string, unknown> | null) => {
  try {
    return JSON.stringify(value ?? {}, null, 2);
  } catch {
    return '{\n}';
  }
};

const ConfigurationEditor: React.FC = () => {
  const { configId } = useParams<{ configId: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [config, setConfig] = useState<ConfigurationDetail | null>(null);
  const [description, setDescription] = useState('');
  const [isActive, setIsActive] = useState(true);
  const [jsonValue, setJsonValue] = useState('{ }');
  const [parsedConfig, setParsedConfig] = useState<Record<string, unknown> | null>(null);
  const [jsonError, setJsonError] = useState<string | null>(null);

  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const fetchConfiguration = async () => {
      if (!configId) {
        setLoadError('Configuration identifier is missing.');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setLoadError(null);

        const detail = await getConfiguration(configId);
        if (cancelled) {
          return;
        }

        setConfig(detail);
        setDescription(detail.description ?? '');
        setIsActive(Boolean(detail.isActive));
        setJsonValue(formatJson(detail.configData));
        setParsedConfig(detail.configData ?? {});
        setJsonError(null);
      } catch (error: unknown) {
        if (!cancelled) {
          let message = 'Failed to load configuration.';
          if (error instanceof Error) {
            message = error.message;
          }
          setLoadError(message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchConfiguration();
    return () => {
      cancelled = true;
    };
  }, [configId]);

  const handleEditorChange = useCallback((value: string | undefined) => {
    const nextValue = value ?? '';
    setJsonValue(nextValue);
    setJsonError(null);

    try {
      const parsed = nextValue.trim() === '' ? {} : JSON.parse(nextValue);
      if (parsed === null || Array.isArray(parsed) || typeof parsed !== 'object') {
        throw new Error('Configuration data must be a JSON object.');
      }
      setParsedConfig(parsed as Record<string, unknown>);
      setJsonError(null);
    } catch {
      setParsedConfig(null);
      setJsonError('Invalid JSON format');
    }
  }, []);

  const handleFormat = () => {
    try {
      const parsed = parsedConfig ?? JSON.parse(jsonValue);
      const formatted = JSON.stringify(parsed, null, 2);
      setJsonValue(formatted);
      setJsonError(null);
      setParsedConfig(parsed as Record<string, unknown>);
    } catch {
      setJsonError('Invalid JSON format');
    }
  };

  const persistConfig = async (nextState: {
    configData?: Record<string, unknown>;
    description?: string;
    isActive?: boolean;
  }) => {
    if (!configId) {
      throw new Error('Configuration identifier missing.');
    }
    const updated = await updateConfiguration(configId, {
      configData: nextState.configData ?? parsedConfig ?? {},
      description: nextState.description ?? description,
      isActive: nextState.isActive ?? isActive,
    });

    setConfig(updated);
    setDescription(updated.description ?? '');
    setIsActive(Boolean(updated.isActive));
    setJsonValue(formatJson(updated.configData));
    setParsedConfig(updated.configData);
    return updated;
  };

  const handleSave = async () => {
    if (!configId || parsedConfig === null) {
      setJsonError('Invalid JSON format');
      return;
    }

    try {
      setSaving(true);
      setSaveError(null);
      setSaveSuccess(null);

      await persistConfig({ configData: parsedConfig, description, isActive });

      setSaveSuccess('Configuration saved successfully.');
      setJsonError(null);
    } catch (error: unknown) {
      let message = 'Failed to save configuration.';
      if (error instanceof Error) {
        message = error.message;
      }
      setSaveError(message);
    } finally {
      setSaving(false);
    }
  };

  const handleToggleActivation = async (nextActive: boolean) => {
    await persistConfig({ isActive: nextActive });
    setSaveSuccess(`Configuration ${nextActive ? 'activated' : 'deactivated'} successfully.`);
  };

  const saveDisabled = useMemo(
    () => jsonError !== null || parsedConfig === null || saving,
    [jsonError, parsedConfig, saving]
  );

  if (loading) {
    return (
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
        <div className="flex flex-col items-center justify-center p-20">
          <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#2A6B6E' }}></div>
          <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Configuration...</div>
        </div>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="p-4 rounded-lg mb-5 flex items-center gap-3 bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] border-l-4 border-[var(--color-status-danger)]">
        <div className="text-xl">⚠️</div>
        <div className="flex-1">
          <div className="font-semibold">{loadError}</div>
        </div>
      </div>
    );
  }

  if (!config) {
    return null;
  }

  return (
    <>
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 mb-6 shadow-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(-1)}
              className="inline-flex items-center px-4 py-2.5 rounded-lg text-sm font-semibold transition-all gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-interactive-active)]"
              aria-label="Back to configurations"
            >
              <ArrowLeft size={16} />
              Back
            </button>
            <div>
              <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
                <Settings className="w-6 h-6" style={{ color: '#2A6B6E' }} />
                Edit Configuration
              </h1>
              <div className="text-sm text-[var(--color-content-muted)] mt-1">
                Modify configuration metadata and payload. Changes are validated before saving.
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-6">

        {saveError && (
          <div className="p-4 rounded-lg flex items-center gap-3 bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] border-l-4 border-[var(--color-status-danger)]">
            <div className="text-xl">⚠️</div>
            <div className="flex-1">
              <div className="font-semibold">{saveError}</div>
            </div>
            <button
              onClick={() => setSaveError(null)}
              className="text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)] transition-colors"
              aria-label="Dismiss error"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>
        )}

        {saveSuccess && (
          <div className="p-4 rounded-lg flex items-center gap-3 bg-[var(--color-status-success-bg)] text-[var(--color-status-success)] border-l-4 border-[var(--color-status-success)]">
            <div className="text-xl">✅</div>
            <div className="flex-1">
              <div className="font-semibold">{saveSuccess}</div>
            </div>
            <button
              onClick={() => setSaveSuccess(null)}
              className="text-[var(--color-status-success)] hover:text-[var(--color-status-success)] transition-colors"
              aria-label="Dismiss success message"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>
        )}

        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label htmlFor="config-key" className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
                  Configuration Key
                </label>
                <input
                  id="config-key"
                  type="text"
                  value={config.configKey}
                  readOnly
                  className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-inset)] text-[var(--color-content-muted)] cursor-not-allowed"
                />
              </div>
              <div>
                <label htmlFor="description" className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
                  Description
                </label>
                <input
                  id="description"
                  type="text"
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                  className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg focus:outline-none focus:border-[#2A6B6E] focus:ring-2 focus:ring-[#2A6B6E]/10 bg-[var(--color-surface-raised)] text-[var(--color-content-primary)]"
                />
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={Boolean(isActive)}
                  onChange={(event) => setIsActive(event.target.checked)}
                  className="h-4 w-4 text-[#2A6B6E] focus:ring-[#2A6B6E] border-[var(--color-border-default)] rounded"
                />
                <span className="ml-2 text-sm text-[var(--color-content-primary)] font-medium">
                  {isActive ? 'Active (pending save)' : 'Inactive (pending save)'}
                </span>
              </label>
              <ActivationToggle
                isActive={Boolean(config.isActive)}
                configurationName={config.configKey}
                onToggle={handleToggleActivation}
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="block text-sm font-semibold text-[var(--color-content-primary)]">
                  Configuration Payload (JSON)
                </label>
                <button
                  onClick={handleFormat}
                  disabled={!!jsonError}
                  className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all ${
                    jsonError
                      ? 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)] cursor-not-allowed'
                      : 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-interactive-active)]'
                  }`}
                >
                  Format JSON
                </button>
              </div>
              <div
                className={`rounded-lg overflow-hidden border ${
                  jsonError ? 'border-[var(--color-status-danger)]' : 'border-[var(--color-border-default)]'
                }`}
              >
                <Editor
                  height={CONFIG_EDITOR_HEIGHT}
                  defaultLanguage="json"
                  value={jsonValue}
                  onChange={handleEditorChange}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    scrollBeyondLastLine: false,
                    wordWrap: 'on',
                  }}
                />
              </div>
              {jsonError && (
                <div className="p-3 rounded-lg flex items-center gap-3 bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] border-l-4 border-[var(--color-status-danger)]">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span className="text-sm font-semibold">{jsonError}</span>
                </div>
              )}
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-[var(--color-border-default)]">
              <button
                onClick={handleSave}
                disabled={saveDisabled}
                className={`inline-flex items-center px-6 py-2.5 rounded-lg text-sm font-semibold transition-all gap-2 ${
                  saveDisabled
                    ? 'bg-[var(--color-interactive-active)] text-[var(--color-content-muted)] cursor-not-allowed'
                    : 'text-white hover:shadow-lg hover:-translate-y-0.5'
                }`}
                style={!saveDisabled ? { background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' } : undefined}
              >
                {saving ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Saving...
                  </>
                ) : (
                  <>
                    <Save size={14} />
                    Save Changes
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ConfigurationEditor;
