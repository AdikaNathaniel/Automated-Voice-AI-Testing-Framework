/**
 * Edge Case Edit Page
 *
 * Edit existing edge cases:
 * - Load existing edge case data
 * - Allow editing all fields
 * - Show unsaved changes warning
 * - Handle updates
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save, Loader2, AlertCircle } from 'lucide-react';
import { getEdgeCase, updateEdgeCase } from '../../services/edgeCase.service';
import type { EdgeCase } from '../../types/edgeCase';

const NORMALISE_TAGS = (value: string): string[] =>
  value
    .split(',')
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0);

export const EdgeCaseEdit: React.FC = () => {
  const navigate = useNavigate();
  const { edgeCaseId } = useParams<{ edgeCaseId: string }>();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Form fields
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [severity, setSeverity] = useState('medium');
  const [status, setStatus] = useState('active');
  const [tagsInput, setTagsInput] = useState('');
  const [scenarioJson, setScenarioJson] = useState('{}');

  useEffect(() => {
    if (edgeCaseId) {
      loadEdgeCase();
    }
  }, [edgeCaseId]);

  useEffect(() => {
    // Warn user about unsaved changes when leaving page
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges]);

  const loadEdgeCase = async () => {
    if (!edgeCaseId) return;

    try {
      setLoading(true);
      setError(null);
      const edgeCase = await getEdgeCase(edgeCaseId);

      setTitle(edgeCase.title);
      setDescription(edgeCase.description || '');
      setCategory(edgeCase.category || '');
      setSeverity(edgeCase.severity || 'medium');
      setStatus(edgeCase.status);
      setTagsInput(edgeCase.tags.join(', '));
      setScenarioJson(JSON.stringify(edgeCase.scenarioDefinition || {}, null, 2));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load edge case');
    } finally {
      setLoading(false);
    }
  };

  const handleFieldChange = () => {
    setHasUnsavedChanges(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!edgeCaseId) return;

    setError(null);

    // Validate
    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    let parsedScenario: Record<string, unknown>;
    try {
      parsedScenario = JSON.parse(scenarioJson);
    } catch {
      setError('Scenario definition must be valid JSON');
      return;
    }

    try {
      setSubmitting(true);
      await updateEdgeCase(edgeCaseId, {
        title: title.trim(),
        description: description.trim() || null,
        category: category.trim() || null,
        severity: severity as 'low' | 'medium' | 'high' | 'critical' | null,
        status: status as 'new' | 'active' | 'resolved' | 'wont_fix',
        tags: NORMALISE_TAGS(tagsInput),
        scenarioDefinition: parsedScenario,
      });

      setHasUnsavedChanges(false);
      navigate(`/edge-cases/${edgeCaseId}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update edge case');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = () => {
    if (hasUnsavedChanges) {
      if (window.confirm('You have unsaved changes. Are you sure you want to leave?')) {
        navigate(`/edge-cases/${edgeCaseId}`);
      }
    } else {
      navigate(`/edge-cases/${edgeCaseId}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 text-[var(--color-content-secondary)]">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span className="text-lg">Loading edge case...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <button
            onClick={handleCancel}
            className="p-2 hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
            aria-label="Back to edge case detail"
          >
            <ArrowLeft className="w-5 h-5 text-[var(--color-content-secondary)]" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)]">
              Edit Edge Case
            </h1>
            <p className="text-sm text-[var(--color-content-secondary)] mt-1">
              Update edge case details and configuration
            </p>
          </div>
        </div>

        {hasUnsavedChanges && (
          <div className="flex items-center gap-2 text-[var(--color-status-amber)] text-sm">
            <AlertCircle className="w-4 h-4" />
            <span>Unsaved changes</span>
          </div>
        )}
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mb-6 p-4 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-[var(--color-status-danger)] flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-[var(--color-status-danger)]">
                Error
              </h3>
              <p className="text-sm text-[var(--color-status-danger)] mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information Card */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
          <h2 className="text-lg font-semibold text-[var(--color-content-primary)] mb-4">
            Basic Information
          </h2>

          <div className="space-y-4">
            {/* Title */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Title *
              </label>
              <input
                type="text"
                id="title"
                value={title}
                onChange={(e) => {
                  setTitle(e.target.value);
                  handleFieldChange();
                }}
                className="w-full px-4 py-2.5 bg-[var(--color-surface-raised)] border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-primary)] focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
                placeholder="Brief description of the edge case"
                required
              />
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Description
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => {
                  setDescription(e.target.value);
                  handleFieldChange();
                }}
                rows={4}
                className="w-full px-4 py-2.5 bg-[var(--color-surface-raised)] border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-primary)] focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors resize-none"
                placeholder="Detailed explanation of what makes this an edge case..."
              />
            </div>
          </div>
        </div>

        {/* Classification Card */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
          <h2 className="text-lg font-semibold text-[var(--color-content-primary)] mb-4">
            Classification
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Category */}
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Category
              </label>
              <select
                id="category"
                value={category}
                onChange={(e) => {
                  setCategory(e.target.value);
                  handleFieldChange();
                }}
                className="w-full px-4 py-2.5 bg-[var(--color-surface-raised)] border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-primary)] focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
              >
                <option value="">Select category</option>
                <option value="ambiguity">Ambiguity</option>
                <option value="audio_quality">Audio Quality</option>
                <option value="context_loss">Context Loss</option>
                <option value="multi_intent">Multi Intent</option>
                <option value="noise">Noise</option>
                <option value="pronunciation">Pronunciation</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Severity */}
            <div>
              <label htmlFor="severity" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Severity
              </label>
              <select
                id="severity"
                value={severity}
                onChange={(e) => {
                  setSeverity(e.target.value);
                  handleFieldChange();
                }}
                className="w-full px-4 py-2.5 bg-[var(--color-surface-raised)] border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-primary)] focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            {/* Status */}
            <div>
              <label htmlFor="status" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Status
              </label>
              <select
                id="status"
                value={status}
                onChange={(e) => {
                  setStatus(e.target.value);
                  handleFieldChange();
                }}
                className="w-full px-4 py-2.5 bg-[var(--color-surface-raised)] border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-primary)] focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
              >
                <option value="new">New</option>
                <option value="active">Active</option>
                <option value="resolved">Resolved</option>
                <option value="wont_fix">Won't Fix</option>
              </select>
            </div>

            {/* Tags */}
            <div>
              <label htmlFor="tags" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Tags
              </label>
              <input
                type="text"
                id="tags"
                value={tagsInput}
                onChange={(e) => {
                  setTagsInput(e.target.value);
                  handleFieldChange();
                }}
                className="w-full px-4 py-2.5 bg-[var(--color-surface-raised)] border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-primary)] focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors"
                placeholder="tag1, tag2, tag3"
              />
              <p className="text-xs text-[var(--color-content-muted)] mt-1">
                Comma-separated list of tags
              </p>
            </div>
          </div>
        </div>

        {/* Scenario Definition Card */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
          <h2 className="text-lg font-semibold text-[var(--color-content-primary)] mb-4">
            Scenario Definition
          </h2>

          <div>
            <label htmlFor="scenario" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
              JSON Configuration
            </label>
            <textarea
              id="scenario"
              value={scenarioJson}
              onChange={(e) => {
                setScenarioJson(e.target.value);
                handleFieldChange();
              }}
              rows={12}
              className="w-full px-4 py-2.5 bg-[var(--color-surface-inset)] border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-primary)] focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors resize-none font-mono text-sm"
              placeholder="{ }"
              spellCheck={false}
            />
            <p className="text-xs text-[var(--color-content-muted)] mt-1">
              Must be valid JSON format
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-4">
          <button
            type="button"
            onClick={handleCancel}
            className="px-6 py-2.5 border border-[var(--color-border-strong)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-hover)] transition-colors font-medium"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting || !hasUnsavedChanges}
            className="px-6 py-2.5 bg-gradient-to-r from-[#2A6B6E] to-[#11484D] text-white rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium inline-flex items-center gap-2"
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Changes
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EdgeCaseEdit;
