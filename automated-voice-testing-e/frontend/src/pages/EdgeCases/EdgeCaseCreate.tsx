import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { ArrowLeft, Save, ChevronDown, Loader2, AlertTriangle } from 'lucide-react'
import { createEdgeCase } from '../../services/edgeCase.service'
import { multiTurnService } from '../../services/multiTurn.service'
import type { ScenarioScript, ScenarioStep } from '../../types/multiTurn'

const DEFAULT_SCENARIO = (details: string | null) => {
  if (!details) {
    return JSON.stringify({}, null, 2)
  }

  try {
    const parsed = JSON.parse(details)
    return JSON.stringify(parsed, null, 2)
  } catch {
    return details
  }
}

const NORMALISE_TAGS = (value: string): string[] =>
  value
    .split(',')
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0)

const EdgeCaseCreate: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const failureReason = searchParams.get('failureReason')
  const failureCategory = searchParams.get('failureCategory')
  const failureDetails = searchParams.get('failureDetails')
  const urlScriptId = searchParams.get('scriptId')

  // Scenario/Step selection state
  const [scenarios, setScenarios] = useState<ScenarioScript[]>([])
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>(urlScriptId || '')
  const [selectedScenario, setSelectedScenario] = useState<ScenarioScript | null>(null)
  const [selectedStepOrder, setSelectedStepOrder] = useState<number | null>(null)
  const [loadingScenarios, setLoadingScenarios] = useState(true)
  const [loadingScenarioDetail, setLoadingScenarioDetail] = useState(false)

  const [title, setTitle] = useState(
    failureReason ? `Edge case: ${failureReason}` : 'New edge case'
  )
  const [description, setDescription] = useState(
    failureReason
      ? `Edge case created from failure: ${failureReason}`
      : 'Describe the edge case scenario'
  )
  const [category, setCategory] = useState(failureCategory || 'ambiguity')
  const [severity, setSeverity] = useState('medium')
  const [tagsInput, setTagsInput] = useState('')
  const [scenarioJson, setScenarioJson] = useState(DEFAULT_SCENARIO(failureDetails))
  const [status, setStatus] = useState('active')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch scenarios on mount
  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        setLoadingScenarios(true)
        const response = await multiTurnService.listScenarios({ page_size: 100 })
        setScenarios(response.scenarios || [])
      } catch (err) {
        console.error('Failed to load scenarios:', err)
      } finally {
        setLoadingScenarios(false)
      }
    }
    fetchScenarios()
  }, [])

  // Fetch scenario details when selection changes
  useEffect(() => {
    if (!selectedScenarioId) {
      setSelectedScenario(null)
      setSelectedStepOrder(null)
      return
    }

    const fetchScenarioDetails = async () => {
      try {
        setLoadingScenarioDetail(true)
        const scenario = await multiTurnService.getScenario(selectedScenarioId)
        setSelectedScenario(scenario)
        setSelectedStepOrder(null)

        // Update title with scenario name if not already set
        if (title === 'New edge case') {
          setTitle(`Edge Case: ${scenario.name}`)
        }
      } catch (err) {
        console.error('Failed to load scenario details:', err)
        setSelectedScenario(null)
      } finally {
        setLoadingScenarioDetail(false)
      }
    }
    fetchScenarioDetails()
  }, [selectedScenarioId])

  // Auto-populate scenario definition when step is selected
  useEffect(() => {
    if (!selectedScenario || selectedStepOrder === null) return

    const step = selectedScenario.steps?.find(s => s.step_order === selectedStepOrder)
    if (!step) return

    const scenarioDefinition = {
      scenario_id: selectedScenario.id,
      scenario_name: selectedScenario.name,
      scenario_description: selectedScenario.description || '',
      step_order: step.step_order,
      user_utterance: step.user_utterance,
      expected_response: '',  // To be filled by user
      actual_response: '',    // To be filled by user
      language_code: step.step_metadata?.primary_language ||
                     selectedScenario.script_metadata?.languages?.[0] || 'en-US',
      language_variants: step.step_metadata?.language_variants || [],
    }

    setScenarioJson(JSON.stringify(scenarioDefinition, null, 2))

    // Update title to include step
    setTitle(`Edge Case: ${selectedScenario.name} - Step ${step.step_order}`)

    // Add language tag
    const lang = scenarioDefinition.language_code
    if (lang && !tagsInput.includes(lang)) {
      setTagsInput(prev => prev ? `${prev}, ${lang}` : lang)
    }
  }, [selectedScenario, selectedStepOrder])

  const scenarioDefinition = useMemo(() => {
    try {
      return JSON.parse(scenarioJson)
    } catch {
      return null
    }
  }, [scenarioJson])

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!scenarioDefinition) {
      setError('Scenario definition must be valid JSON.')
      return
    }

    setSubmitting(true)
    setError(null)

    try {
      // Use selected scenario ID if available, otherwise use URL param
      const finalScriptId = selectedScenarioId || urlScriptId || null

      const payload = await createEdgeCase({
        title: title.trim(),
        description: description.trim(),
        category,
        severity,
        status,
        tags: NORMALISE_TAGS(tagsInput),
        scenarioDefinition,
        scriptId: finalScriptId,
      })

      navigate(`/edge-cases/${payload.id}`, { replace: true })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create edge case'
      setError(message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 mb-6 shadow-md">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
              <AlertTriangle className="w-6 h-6" style={{ color: '#2A6B6E' }} />
              Create Edge Case
            </h1>
            <div className="text-sm text-[var(--color-content-muted)] mt-1">
              Review the failure details and provide additional context before saving.
            </div>
          </div>
          <button
            onClick={() => navigate('/edge-cases')}
            className="p-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-default)] hover:bg-[var(--color-interactive-active)]"
          >
            <ArrowLeft size={18} />
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 rounded-lg mb-5 flex items-center gap-3 bg-danger-light  text-[var(--color-status-danger)] border-l-4 border-danger " role="alert">
          <div className="text-xl">⚠️</div>
          <div className="flex-1">
            <div className="font-semibold">{error}</div>
          </div>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
        <div className="space-y-6">
          {/* Scenario Selection Section */}
          <div className="bg-[var(--color-surface-inset)]/50 rounded-lg p-4 border border-[var(--color-border-default)]">
            <h3 className="text-sm font-semibold text-[var(--color-content-primary)] mb-3">
              Select from Existing Scenario (Optional)
            </h3>
            <p className="text-xs text-[var(--color-content-muted)] mb-4">
              Choose a scenario and step to auto-populate the edge case details, or fill in manually below.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Scenario Dropdown */}
              <div>
                <label htmlFor="scenario-select" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                  Scenario
                </label>
                <div className="relative">
                  <select
                    id="scenario-select"
                    value={selectedScenarioId}
                    onChange={(e) => setSelectedScenarioId(e.target.value)}
                    disabled={loadingScenarios}
                    className="w-full px-4 py-2.5 pr-10 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 appearance-none disabled:opacity-50"
                  >
                    <option value="">-- Select a scenario --</option>
                    {scenarios.map((scenario) => (
                      <option key={scenario.id} value={scenario.id}>
                        {scenario.name}
                      </option>
                    ))}
                  </select>
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                    {loadingScenarios ? (
                      <Loader2 className="w-4 h-4 text-[var(--color-content-muted)] animate-spin" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-[var(--color-content-muted)]" />
                    )}
                  </div>
                </div>
              </div>

              {/* Step Dropdown */}
              <div>
                <label htmlFor="step-select" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                  Step
                </label>
                <div className="relative">
                  <select
                    id="step-select"
                    value={selectedStepOrder ?? ''}
                    onChange={(e) => setSelectedStepOrder(e.target.value ? Number(e.target.value) : null)}
                    disabled={!selectedScenario || loadingScenarioDetail}
                    className="w-full px-4 py-2.5 pr-10 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 appearance-none disabled:opacity-50"
                  >
                    <option value="">-- Select a step --</option>
                    {selectedScenario?.steps?.sort((a, b) => a.step_order - b.step_order).map((step) => (
                      <option key={step.id} value={step.step_order}>
                        Step {step.step_order}: {step.user_utterance.substring(0, 40)}
                        {step.user_utterance.length > 40 ? '...' : ''}
                      </option>
                    ))}
                  </select>
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                    {loadingScenarioDetail ? (
                      <Loader2 className="w-4 h-4 text-[var(--color-content-muted)] animate-spin" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-[var(--color-content-muted)]" />
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Selected Step Preview */}
            {selectedScenario && selectedStepOrder !== null && (
              <div className="mt-4 p-3 bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)]">
                <p className="text-xs font-medium text-[var(--color-content-muted)] mb-1">Selected Step Preview</p>
                <p className="text-sm text-[var(--color-content-primary)]">
                  {selectedScenario.steps?.find(s => s.step_order === selectedStepOrder)?.user_utterance || 'No utterance'}
                </p>
              </div>
            )}
          </div>

          {/* Title */}
          <div>
            <label htmlFor="edge-case-title" className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
              Edge case title
            </label>
            <input
              id="edge-case-title"
              type="text"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              required
              className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder-[var(--color-content-muted)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
            />
          </div>

          {/* Description */}
          <div>
            <label htmlFor="edge-case-description" className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
              Description
            </label>
            <textarea
              id="edge-case-description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              rows={3}
              className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder-[var(--color-content-muted)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 resize-none"
            />
          </div>

          {/* Category and Severity */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="edge-case-category" className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
                Category
              </label>
              <select
                id="edge-case-category"
                value={category}
                onChange={(event) => setCategory(event.target.value)}
                className="w-full px-4 py-2.5 pr-10 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
              >
                <option value="timeout">Timeout</option>
                <option value="ambiguity">Ambiguity</option>
                <option value="context_loss">Context loss</option>
                <option value="audio_quality">Audio quality</option>
              </select>
            </div>

            <div>
              <label htmlFor="edge-case-severity" className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
                Severity
              </label>
              <select
                id="edge-case-severity"
                value={severity}
                onChange={(event) => setSeverity(event.target.value)}
                className="w-full px-4 py-2.5 pr-10 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </div>

          {/* Status */}
          <div>
            <label htmlFor="edge-case-status" className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
              Status
            </label>
            <select
              id="edge-case-status"
              value={status}
              onChange={(event) => setStatus(event.target.value)}
              className="w-full px-4 py-2.5 pr-10 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
            >
              <option value="active">Active</option>
              <option value="investigating">Investigating</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          {/* Tags */}
          <div>
            <label htmlFor="edge-case-tags" className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
              Tags <span className="text-[var(--color-content-muted)] font-normal">(comma-separated)</span>
            </label>
            <input
              id="edge-case-tags"
              type="text"
              value={tagsInput}
              onChange={(event) => setTagsInput(event.target.value)}
              placeholder="timeout, external-service"
              className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder-[var(--color-content-muted)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
            />
          </div>

          {/* Related Script - Show if selected from dropdown or from URL */}
          {(selectedScenarioId || urlScriptId) && (
            <div>
              <label htmlFor="edge-case-script" className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
                Related scenario
              </label>
              <div className="flex items-center gap-2">
                <input
                  id="edge-case-script"
                  type="text"
                  value={selectedScenario?.name || urlScriptId || ''}
                  readOnly
                  aria-readonly="true"
                  className="flex-1 px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] cursor-not-allowed"
                />
                {selectedScenarioId && (
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedScenarioId('')
                      setSelectedScenario(null)
                      setSelectedStepOrder(null)
                    }}
                    className="px-3 py-2.5 text-sm text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)]"
                  >
                    Clear
                  </button>
                )}
              </div>
              <p className="text-xs text-[var(--color-content-muted)] mt-1">
                ID: {selectedScenarioId || urlScriptId}
              </p>
            </div>
          )}

          {/* Scenario Definition */}
          <div>
            <label htmlFor="edge-case-scenario" className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
              Scenario definition <span className="text-[var(--color-content-muted)] font-normal">(JSON format)</span>
            </label>
            <textarea
              id="edge-case-scenario"
              value={scenarioJson}
              onChange={(event) => setScenarioJson(event.target.value)}
              rows={8}
              className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder-[var(--color-content-muted)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 font-mono resize-none"
            />
            {!scenarioDefinition && scenarioJson.trim() && (
              <p className="text-xs text-[var(--color-status-danger)] mt-1">Invalid JSON format</p>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex gap-3 justify-end pt-4 border-t border-[var(--color-border-default)]">
            <button
              type="button"
              onClick={() => navigate('/edge-cases')}
              className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-default)] hover:bg-[var(--color-interactive-active)]"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || !scenarioDefinition}
              className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 text-white hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none disabled:hover:translate-y-0"
              style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
            >
              <Save size={14} />
              {submitting ? 'Creating…' : 'Create edge case'}
            </button>
          </div>
        </div>
      </form>
    </>
  )
}

export default EdgeCaseCreate
