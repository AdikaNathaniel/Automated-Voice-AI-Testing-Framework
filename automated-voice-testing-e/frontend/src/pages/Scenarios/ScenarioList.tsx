/**
 * Scenario List Page
 *
 * Displays all multi-turn conversation scenarios with:
 * - Filtering by status and category
 * - Search functionality
 * - Execute scenario button with language selection
 * - View scenario details
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Eye, Plus, Edit2, Trash2, Copy, Globe, X, FileText, MoreVertical } from 'lucide-react';
import { SearchInput, Dropdown } from '../../components/common';
import { multiTurnService } from '../../services/multiTurn.service';
import type { ScenarioScript } from '../../types/multiTurn';
import Modal from '../../components/Modal/Modal';
import { useModal } from '../../hooks/useModal';
import { LanguageSelector } from '../../components/Scenarios/LanguageSelector';

const ScenarioList: React.FC = () => {
  const navigate = useNavigate();
  const { modalState, showError, showSuccess, closeModal } = useModal();
  const [scenarios, setScenarios] = useState<ScenarioScript[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [executing, setExecuting] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  // Language selection modal state
  const [executeModal, setExecuteModal] = useState<ScenarioScript | null>(null);
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>([]);

  useEffect(() => {
    loadScenarios();
  }, [statusFilter]);

  const loadScenarios = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await multiTurnService.listScenarios({
        is_active: statusFilter === 'active' ? true : statusFilter === 'inactive' ? false : undefined,
      });
      setScenarios(response.scenarios || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load scenarios');
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteClick = (scenario: ScenarioScript) => {
    // If scenario has multiple languages, show selection modal
    if (scenario.languages && scenario.languages.length > 1) {
      setExecuteModal(scenario);
      setSelectedLanguages([]); // Empty = all languages
    } else {
      // Single language or no languages - execute directly
      handleExecuteScenario(scenario.id);
    }
  };

  const handleExecuteScenario = async (scriptId: string, languageCodes?: string[]) => {
    try {
      setExecuting(scriptId);
      setExecuteModal(null);
      const result = await multiTurnService.executeScenario(scriptId, {
        script_id: scriptId,
        language_codes: languageCodes && languageCodes.length > 0 ? languageCodes : undefined,
      });
      // Navigate to execution detail page
      navigate(`/scenarios/executions/${result.execution_id}`);
    } catch (err: any) {
      showError(`Failed to execute scenario: ${err.message}`);
    } finally {
      setExecuting(null);
    }
  };

  const handleExecuteWithLanguages = () => {
    if (executeModal) {
      handleExecuteScenario(executeModal.id, selectedLanguages);
    }
  };

  const handleLanguageChange = (languages: string[]) => {
    setSelectedLanguages(languages);
  };

  const handleDeleteScenario = async (scriptId: string) => {
    try {
      await multiTurnService.deleteScenario(scriptId);
      setDeleteConfirm(null);
      loadScenarios(); // Reload the list
      showSuccess('Scenario deleted successfully');
    } catch (err: any) {
      showError(`Failed to delete scenario: ${err.message}`);
    }
  };

  const handleDuplicateScenario = async (scenario: ScenarioScript) => {
    try {
      // Get full scenario details
      const fullScenario = await multiTurnService.getScenario(scenario.id);

      // Deep clone steps and strip IDs and outcome_codes to avoid unique constraint violations
      const clonedSteps = (fullScenario.steps || []).map((step: any) => {
        const { id, script_id, created_at, updated_at, ...stepData } = step;

        // Clone expected outcomes and remove id and outcome_code
        const clonedOutcomes = (step.expected_outcomes || []).map((outcome: any) => {
          const { id, outcome_code, scenario_step_id, created_at, updated_at, ...outcomeData } = outcome;
          return outcomeData;
        });

        return {
          ...stepData,
          expected_outcomes: clonedOutcomes,
        };
      });

      // Create a copy with modified name
      const duplicateData = {
        name: `${fullScenario.name} (Copy)`,
        description: fullScenario.description,
        version: '1.0.0',
        is_active: fullScenario.is_active,
        script_metadata: fullScenario.script_metadata,
        approval_status: 'draft',
        steps: clonedSteps,
      };

      const newScenario = await multiTurnService.createScenario(duplicateData);
      navigate(`/scenarios/${newScenario.id}/edit`);
    } catch (err: any) {
      showError(`Failed to duplicate scenario: ${err.message}`);
    }
  };

  const filteredScenarios = scenarios.filter((scenario) =>
    scenario.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (scenario.description && scenario.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <FileText className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            Scenarios
          </h1>
          <p className="text-sm text-[var(--color-content-muted)] mt-1">Execute and manage single and multi-turn conversation test scenarios</p>
        </div>
        <button
          onClick={() => navigate('/scenarios/new')}
          className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 text-white hover:shadow-lg hover:-translate-y-0.5"
          style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
        >
          <Plus size={14} /> Create New Scenario
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-[var(--color-surface-raised)] p-4 rounded-xl mb-5 shadow-sm flex flex-col sm:flex-row gap-3 sm:items-center">
        <SearchInput
          placeholder="Search scenarios..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <Dropdown
          value={statusFilter}
          onChange={setStatusFilter}
          options={[
            { value: 'all', label: 'All Scenarios' },
            { value: 'active', label: 'Active Only' },
            { value: 'inactive', label: 'Inactive Only' },
          ]}
        />
      </div>

      {/* Loading State */}
      {loading && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
          <div className="flex flex-col items-center justify-center p-20">
            <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#2A6B6E' }}></div>
            <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Scenarios...</div>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
          <div className="p-10 text-center text-[var(--color-status-danger)]">{error}</div>
        </div>
      )}

      {/* Scenarios Grid */}
      {!loading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredScenarios.map((scenario) => (
            <ScenarioCard
              key={scenario.id}
              scenario={scenario}
              onExecute={handleExecuteClick}
              onDelete={handleDeleteScenario}
              onDuplicate={handleDuplicateScenario}
              executing={executing === scenario.id}
              deleteConfirm={deleteConfirm}
              setDeleteConfirm={setDeleteConfirm}
            />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && filteredScenarios.length === 0 && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
          <div className="text-center py-12">
            <p className="text-[var(--color-content-secondary)]">No scenarios found</p>
          </div>
        </div>
      )}

      {/* Language Selection Modal */}
      {executeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-[var(--color-border-default)] flex-shrink-0">
              <div className="flex-1 min-w-0 pr-4">
                <h3 className="text-xl font-bold text-[var(--color-content-primary)]">Execute Scenario</h3>
                <p className="text-sm text-[var(--color-content-muted)] mt-1 truncate">{executeModal.name}</p>
              </div>
              <button
                onClick={() => setExecuteModal(null)}
                className="flex-shrink-0 text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)] transition-colors"
                aria-label="Close modal"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Modal Body - Scrollable */}
            <div className="p-6 overflow-y-auto flex-1">
              <p className="text-sm text-[var(--color-content-secondary)] mb-5">
                Select which language variants to execute for this scenario:
              </p>

              <LanguageSelector
                availableLanguages={executeModal.languages || []}
                selectedLanguages={selectedLanguages}
                onChange={handleLanguageChange}
                label="Language Variants"
                showAllOption={true}
              />
            </div>

            {/* Modal Footer */}
            <div className="flex gap-3 p-6 border-t border-[var(--color-border-default)] flex-shrink-0">
              <button
                onClick={() => setExecuteModal(null)}
                className="flex-1 px-4 py-2.5 border-2 border-[var(--color-border-strong)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-hover)] font-medium transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleExecuteWithLanguages}
                disabled={executeModal.languages && executeModal.languages.length > 0 && selectedLanguages.length === 0 && executeModal.languages.length === 0}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 text-white rounded-lg transition-all hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
              >
                <Play className="w-4 h-4" />
                Execute Scenario
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal for alerts */}
      <Modal
        isOpen={modalState.isOpen}
        onClose={closeModal}
        onConfirm={modalState.onConfirm}
        title={modalState.title}
        message={modalState.message}
        type={modalState.type}
        confirmText={modalState.confirmText}
        cancelText={modalState.cancelText}
        showCancel={modalState.showCancel}
      />
    </>
  );
};

/**
 * Language display information
 */
const languageInfo: Record<string, { flag: string; name: string }> = {
  en: { flag: '🇺🇸', name: 'English' },
  'en-US': { flag: '🇺🇸', name: 'English (US)' },
  'en-GB': { flag: '🇬🇧', name: 'English (UK)' },
  'en-AU': { flag: '🇦🇺', name: 'English (AU)' },
  es: { flag: '🇪🇸', name: 'Spanish' },
  'es-ES': { flag: '🇪🇸', name: 'Spanish (Spain)' },
  'es-MX': { flag: '🇲🇽', name: 'Spanish (Mexico)' },
  'es-AR': { flag: '🇦🇷', name: 'Spanish (Argentina)' },
  fr: { flag: '🇫🇷', name: 'French' },
  'fr-FR': { flag: '🇫🇷', name: 'French (France)' },
  'fr-CA': { flag: '🇨🇦', name: 'French (Canada)' },
  de: { flag: '🇩🇪', name: 'German' },
  'de-DE': { flag: '🇩🇪', name: 'German' },
  it: { flag: '🇮🇹', name: 'Italian' },
  'it-IT': { flag: '🇮🇹', name: 'Italian' },
  pt: { flag: '🇵🇹', name: 'Portuguese' },
  'pt-PT': { flag: '🇵🇹', name: 'Portuguese (Portugal)' },
  'pt-BR': { flag: '🇧🇷', name: 'Portuguese (Brazil)' },
  ja: { flag: '🇯🇵', name: 'Japanese' },
  'ja-JP': { flag: '🇯🇵', name: 'Japanese' },
  ko: { flag: '🇰🇷', name: 'Korean' },
  'ko-KR': { flag: '🇰🇷', name: 'Korean' },
  zh: { flag: '🇨🇳', name: 'Chinese' },
  'zh-CN': { flag: '🇨🇳', name: 'Chinese (Simplified)' },
  'zh-TW': { flag: '🇹🇼', name: 'Chinese (Traditional)' },
  ru: { flag: '🇷🇺', name: 'Russian' },
  'ru-RU': { flag: '🇷🇺', name: 'Russian' },
  ar: { flag: '🇸🇦', name: 'Arabic' },
  'ar-SA': { flag: '🇸🇦', name: 'Arabic' },
  hi: { flag: '🇮🇳', name: 'Hindi' },
  'hi-IN': { flag: '🇮🇳', name: 'Hindi' },
  nl: { flag: '🇳🇱', name: 'Dutch' },
  'nl-NL': { flag: '🇳🇱', name: 'Dutch' },
  pl: { flag: '🇵🇱', name: 'Polish' },
  'pl-PL': { flag: '🇵🇱', name: 'Polish' },
  sv: { flag: '🇸🇪', name: 'Swedish' },
  'sv-SE': { flag: '🇸🇪', name: 'Swedish' },
  tr: { flag: '🇹🇷', name: 'Turkish' },
  'tr-TR': { flag: '🇹🇷', name: 'Turkish' },
};

const getLanguageDisplay = (lang: string): { flag?: string; name: string; code: string } => {
  const info = languageInfo[lang] || languageInfo[lang.split('-')[0]];
  return {
    flag: info?.flag,
    name: info?.name || lang,
    code: lang.toUpperCase()
  };
};

/**
 * Scenario Card Component
 */
interface ScenarioCardProps {
  scenario: ScenarioScript;
  onExecute: (scenario: ScenarioScript) => void;
  onDelete: (scriptId: string) => void;
  onDuplicate: (scenario: ScenarioScript) => void;
  executing: boolean;
  deleteConfirm: string | null;
  setDeleteConfirm: (id: string | null) => void;
}

const ScenarioCard: React.FC<ScenarioCardProps> = ({
  scenario,
  onExecute,
  onDelete,
  onDuplicate,
  executing,
  deleteConfirm,
  setDeleteConfirm
}) => {
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);

  const getStatusConfig = () => {
    if (!scenario.is_active) {
      return { label: 'Inactive', bg: 'bg-[var(--color-surface-inset)]', text: 'text-[var(--color-content-secondary)]', dot: 'bg-[var(--color-content-muted)]' };
    }
    switch (scenario.approval_status) {
      case 'approved':
        return { label: 'Approved', bg: 'bg-[var(--color-status-emerald-bg)]', text: 'text-[var(--color-status-emerald)]', dot: 'bg-[var(--color-status-success)]' };
      case 'pending_review':
        return { label: 'Pending', bg: 'bg-[var(--color-status-amber-bg)]', text: 'text-[var(--color-status-amber)]', dot: 'bg-[var(--color-status-warning)]' };
      case 'draft':
        return { label: 'Draft', bg: 'bg-[var(--color-surface-inset)]', text: 'text-[var(--color-content-secondary)]', dot: 'bg-[var(--color-content-muted)]' };
      case 'rejected':
        return { label: 'Rejected', bg: 'bg-[var(--color-status-rose-bg)]', text: 'text-[var(--color-status-rose)]', dot: 'bg-[var(--color-status-danger)]' };
      default:
        return null;
    }
  };

  const status = getStatusConfig();

  return (
    <div className="group bg-[var(--color-surface-raised)] rounded-2xl border border-[var(--color-border-default)]/80 hover:border-[var(--color-accent-500)]/40 shadow-sm hover:shadow-lg hover:shadow-[#2A6B6E]/5 transition-all duration-300 flex flex-col h-full overflow-hidden">
      {/* Top accent bar */}
      <div
        className="h-1 w-full opacity-60 group-hover:opacity-100 transition-opacity"
        style={{ background: scenario.is_active ? 'linear-gradient(90deg, #2A6B6E 0%, #11484D 100%)' : '#9CA3AF' }}
      />

      {/* Card Content */}
      <div className="p-5 flex-1 flex flex-col">
        {/* Header Row */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-base font-semibold text-[var(--color-content-primary)] truncate leading-tight">
              {scenario.name}
            </h3>
            <div className="flex items-center gap-2 mt-2">
              {status && (
                <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${status.bg} ${status.text}`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${status.dot}`} />
                  {status.label}
                </span>
              )}
              {scenario.version && (
                <span className="text-xs text-[var(--color-content-muted)] font-mono">
                  v{scenario.version}
                </span>
              )}
            </div>
          </div>

          {/* Dropdown Menu */}
          <div className="relative flex-shrink-0">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-1.5 rounded-lg text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] transition-colors"
            >
              <MoreVertical className="w-5 h-5" />
            </button>
            {showMenu && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />
                <div className="absolute right-0 mt-1 w-44 bg-[var(--color-surface-raised)] rounded-xl shadow-xl border border-[var(--color-border-default)] py-1.5 z-20 overflow-hidden">
                  <button
                    onClick={() => {
                      setShowMenu(false);
                      navigate(`/scenarios/${scenario.id}/edit`);
                    }}
                    className="w-full px-4 py-2.5 text-left text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]/70 flex items-center gap-3 transition-colors"
                  >
                    <Edit2 className="w-4 h-4 text-[var(--color-content-muted)]" />
                    Edit Scenario
                  </button>
                  <button
                    onClick={() => {
                      setShowMenu(false);
                      onDuplicate(scenario);
                    }}
                    className="w-full px-4 py-2.5 text-left text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]/70 flex items-center gap-3 transition-colors"
                  >
                    <Copy className="w-4 h-4 text-[var(--color-content-muted)]" />
                    Duplicate
                  </button>
                  <div className="my-1.5 border-t border-[var(--color-border-subtle)]" />
                  <button
                    onClick={() => {
                      setShowMenu(false);
                      setDeleteConfirm(scenario.id);
                    }}
                    className="w-full px-4 py-2.5 text-left text-sm text-[var(--color-status-rose)] hover:bg-[var(--color-status-rose-bg)] flex items-center gap-3 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </button>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Description */}
        {scenario.description ? (
          <p className="text-sm text-[var(--color-content-muted)] line-clamp-2 mb-4 leading-relaxed">
            {scenario.description}
          </p>
        ) : (
          <p className="text-sm text-[var(--color-content-muted)] italic mb-4">
            No description
          </p>
        )}

        {/* Info Pills */}
        <div className="flex items-center gap-2 flex-wrap mb-4">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-[var(--color-surface-inset)]/70 text-[var(--color-content-secondary)] rounded-lg text-xs font-medium">
            <FileText className="w-3.5 h-3.5" />
            {scenario.steps_count || 0} steps
          </span>
          {scenario.script_metadata?.category && (
            <span className="px-2.5 py-1 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] rounded-lg text-xs font-medium uppercase tracking-wide">
              {scenario.script_metadata.category}
            </span>
          )}
        </div>

        {/* Languages */}
        {scenario.languages && scenario.languages.length > 0 && (
          <div className="flex items-center gap-1.5 flex-wrap">
            {scenario.languages.slice(0, 4).map((lang) => {
              const { flag, name } = getLanguageDisplay(lang);
              return (
                <span
                  key={lang}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-gradient-to-br from-[var(--color-interactive-hover)] to-[var(--color-interactive-hover)]/50 border border-[var(--color-border-default)]/50 text-[var(--color-content-secondary)] rounded-md text-xs"
                  title={name}
                >
                  {flag ? (
                    <span>{flag}</span>
                  ) : (
                    <Globe className="w-3 h-3 text-[var(--color-content-muted)]" />
                  )}
                  <span className="font-medium">{lang.split('-')[0].toUpperCase()}</span>
                </span>
              );
            })}
            {scenario.languages.length > 4 && (
              <span className="px-2 py-1 text-xs text-[var(--color-content-muted)] font-medium">
                +{scenario.languages.length - 4}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Actions Footer */}
      <div className="px-5 py-4 bg-[var(--color-surface-base)]/30 border-t border-[var(--color-border-subtle)]/50 flex gap-3">
        <button
          onClick={() => navigate(`/scenarios/${scenario.id}`)}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-[var(--color-surface-raised)] border border-[var(--color-border-default)] rounded-xl text-[var(--color-content-secondary)] font-medium text-sm hover:bg-[var(--color-interactive-hover)] hover:border-[var(--color-border-strong)] transition-all"
        >
          <Eye className="w-4 h-4" />
          View
        </button>
        <button
          onClick={() => onExecute(scenario)}
          disabled={executing || !scenario.is_active}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 text-white rounded-xl font-medium text-sm transition-all disabled:cursor-not-allowed disabled:opacity-50 hover:shadow-md hover:-translate-y-0.5 active:translate-y-0"
          style={
            !executing && scenario.is_active
              ? { background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }
              : { background: '#9CA3AF' }
          }
        >
          {executing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white" />
              Running...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Execute
            </>
          )}
        </button>
      </div>

      {/* Delete Confirmation */}
      {deleteConfirm === scenario.id && (
        <div className="px-5 py-3 bg-[var(--color-status-rose-bg)] border-t border-[var(--color-status-rose-bg)] flex items-center justify-between">
          <span className="text-sm font-medium text-[var(--color-status-rose)]">Delete this scenario?</span>
          <div className="flex gap-2">
            <button
              onClick={() => setDeleteConfirm(null)}
              className="px-3.5 py-1.5 text-sm font-medium text-[var(--color-content-secondary)] hover:bg-[var(--color-status-rose-bg)] rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={() => onDelete(scenario.id)}
              className="px-3.5 py-1.5 text-sm font-medium bg-[var(--color-status-danger)] text-white rounded-lg hover:opacity-90 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScenarioList;
