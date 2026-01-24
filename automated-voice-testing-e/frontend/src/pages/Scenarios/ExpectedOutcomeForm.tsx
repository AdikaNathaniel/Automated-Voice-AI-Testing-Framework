/**
 * Expected Outcome Form Component
 *
 * Configures expected outcomes for scenario steps:
 * - Outcome code and name
 * - Expected command kind (Houndify CommandKind)
 * - ASR confidence threshold
 * - Response content patterns (contains, not_contains, regex)
 * - Entity validation
 * - Custom validation rules
 */

import React, { useState, useCallback } from 'react';
import { Plus, Trash2, ChevronDown, ChevronUp, Code, FormInput } from 'lucide-react';

/**
 * Expected response content structure for deterministic validation
 */
export interface ExpectedResponseContent {
  contains?: string[];
  not_contains?: string[];
  regex?: string[];
  regex_not_match?: string[];
}

/**
 * Check if content is a valid ExpectedResponseContent object
 */
const isResponseContentObject = (content: unknown): content is ExpectedResponseContent => {
  if (!content || typeof content !== 'object') return false;
  const obj = content as Record<string, unknown>;
  const validKeys = ['contains', 'not_contains', 'regex', 'regex_not_match'];
  return Object.keys(obj).every(key => validKeys.includes(key));
};

/**
 * Convert content to ExpectedResponseContent object
 */
const toResponseContentObject = (
  content: string | Record<string, unknown> | undefined
): ExpectedResponseContent => {
  if (!content) return {};
  if (typeof content === 'string') {
    // If it's a non-empty string, treat it as a single contains pattern
    const trimmed = content.trim();
    return trimmed ? { contains: [trimmed] } : {};
  }
  if (isResponseContentObject(content)) {
    return content;
  }
  return {};
};

/**
 * Check if response content object is empty
 */
const isResponseContentEmpty = (content: ExpectedResponseContent): boolean => {
  return (
    (!content.contains || content.contains.length === 0) &&
    (!content.not_contains || content.not_contains.length === 0) &&
    (!content.regex || content.regex.length === 0) &&
    (!content.regex_not_match || content.regex_not_match.length === 0)
  );
};

/**
 * Sub-component for structured response content form
 */
interface ResponseContentFormProps {
  value: ExpectedResponseContent;
  onChange: (content: ExpectedResponseContent) => void;
}

const ResponseContentForm: React.FC<ResponseContentFormProps> = ({ value, onChange }) => {
  const [newContains, setNewContains] = useState('');
  const [newNotContains, setNewNotContains] = useState('');
  const [newRegex, setNewRegex] = useState('');
  const [newRegexNotMatch, setNewRegexNotMatch] = useState('');

  const addItem = (field: keyof ExpectedResponseContent, item: string, clearFn: () => void) => {
    if (!item.trim()) return;
    const current = value[field] || [];
    if (!current.includes(item.trim())) {
      onChange({ ...value, [field]: [...current, item.trim()] });
    }
    clearFn();
  };

  const removeItem = (field: keyof ExpectedResponseContent, index: number) => {
    const current = value[field] || [];
    onChange({ ...value, [field]: current.filter((_, i) => i !== index) });
  };

  const renderPatternList = (
    field: keyof ExpectedResponseContent,
    label: string,
    placeholder: string,
    newValue: string,
    setNewValue: (v: string) => void,
    description: string,
    isRegex: boolean = false
  ) => {
    const items = value[field] || [];
    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-[var(--color-content-secondary)]">{label}</label>
        <p className="text-xs text-[var(--color-content-muted)]">{description}</p>
        {/* Existing items */}
        {items.length > 0 && (
          <div className="space-y-1">
            {items.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 p-2 bg-[var(--color-surface-inset)]/50 rounded border border-[var(--color-border-default)] text-sm"
              >
                <span className={isRegex ? 'font-mono text-[var(--color-status-purple)]' : 'text-[var(--color-content-secondary)]'}>
                  {item}
                </span>
                <button
                  type="button"
                  onClick={() => removeItem(field, idx)}
                  className="ml-auto text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)]"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}
        {/* Add new item */}
        <div className="flex gap-2">
          <input
            type="text"
            value={newValue}
            onChange={(e) => setNewValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                addItem(field, newValue, () => setNewValue(''));
              }
            }}
            className={`flex-1 px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary text-sm ${
              isRegex ? 'font-mono' : ''
            }`}
            placeholder={placeholder}
          />
          <button
            type="button"
            onClick={() => addItem(field, newValue, () => setNewValue(''))}
            className="px-3 py-2 bg-[var(--color-interactive-active)] text-[var(--color-content-secondary)] rounded-md hover:bg-[var(--color-interactive-active)] text-sm"
          >
            Add
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {renderPatternList(
        'contains',
        'Must Contain',
        'e.g., sunny, temperature',
        newContains,
        setNewContains,
        'AI response MUST include these phrases (case-insensitive)'
      )}
      {renderPatternList(
        'not_contains',
        'Must NOT Contain',
        'e.g., error, sorry, unknown',
        newNotContains,
        setNewNotContains,
        'AI response must NOT include these phrases (case-insensitive)'
      )}
      {renderPatternList(
        'regex',
        'Must Match Regex',
        'e.g., \\d+ degrees, [A-Z][a-z]+',
        newRegex,
        setNewRegex,
        'AI response must match these regex patterns',
        true
      )}
      {renderPatternList(
        'regex_not_match',
        'Must NOT Match Regex',
        'e.g., error.*occurred, I don\'t know',
        newRegexNotMatch,
        setNewRegexNotMatch,
        'AI response must NOT match these regex patterns',
        true
      )}
    </div>
  );
};

export interface ExpectedOutcomeData {
  id?: string;
  outcome_code: string;
  name: string;
  description?: string;
  // Houndify-specific fields
  expected_command_kind?: string;
  expected_asr_confidence_min?: number;
  expected_response_content?: string | Record<string, any>; // Can be string or object
  expected_native_data_schema?: Record<string, any>;
  conversation_requirements?: Record<string, any>;
  // General fields
  entities?: Record<string, any>;
  validation_rules?: Record<string, any>;
}

interface ExpectedOutcomeFormProps {
  outcomes: ExpectedOutcomeData[];
  onChange: (outcomes: ExpectedOutcomeData[]) => void;
  stepNumber?: number;
}

export const ExpectedOutcomeForm: React.FC<ExpectedOutcomeFormProps> = ({
  outcomes,
  onChange,
  stepNumber,
}) => {
  const [expandedOutcomes, setExpandedOutcomes] = useState<Set<number>>(new Set([0]));
  const [entityInputs, setEntityInputs] = useState<Record<number, { key: string; value: string }>>(
    {}
  );
  // Track which outcomes are in raw JSON mode (default is structured mode)
  const [rawJsonMode, setRawJsonMode] = useState<Set<number>>(new Set());

  // Helper to convert expected_response_content to string for display
  const formatResponseContent = (content: string | Record<string, any> | undefined): string => {
    if (!content) return '';
    if (typeof content === 'string') return content;
    return JSON.stringify(content, null, 2);
  };

  // Helper to parse expected_response_content from string
  const parseResponseContent = (value: string): string | Record<string, any> => {
    if (!value.trim()) return '';

    // Try to parse as JSON
    try {
      return JSON.parse(value);
    } catch {
      // If not valid JSON, return as string
      return value;
    }
  };

  // Helper to format JSON fields for display
  const formatJsonField = (value: Record<string, any> | undefined): string => {
    if (!value || Object.keys(value).length === 0) return '';
    return JSON.stringify(value, null, 2);
  };

  // Helper to parse JSON fields
  const parseJsonField = (value: string): Record<string, any> | undefined => {
    if (!value.trim()) return undefined;
    try {
      return JSON.parse(value);
    } catch {
      return undefined;
    }
  };

  const addOutcome = () => {
    const newOutcome: ExpectedOutcomeData = {
      outcome_code: `outcome_${outcomes.length + 1}`,
      name: `Outcome ${outcomes.length + 1}`,
      description: '',
      expected_command_kind: '',
      expected_asr_confidence_min: 0.7,
      expected_response_content: '',
      expected_native_data_schema: undefined,
      conversation_requirements: undefined,
      entities: {},
      validation_rules: {},
    };
    onChange([...outcomes, newOutcome]);
    setExpandedOutcomes(new Set([...expandedOutcomes, outcomes.length]));
  };

  const removeOutcome = (index: number) => {
    onChange(outcomes.filter((_, i) => i !== index));
    setExpandedOutcomes(new Set([...expandedOutcomes].filter((i) => i < outcomes.length - 1)));
  };

  const updateOutcome = (index: number, updates: Partial<ExpectedOutcomeData>) => {
    const newOutcomes = [...outcomes];
    newOutcomes[index] = { ...newOutcomes[index], ...updates };
    onChange(newOutcomes);
  };

  const toggleExpanded = (index: number) => {
    const newExpanded = new Set(expandedOutcomes);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedOutcomes(newExpanded);
  };

  const addEntity = (outcomeIndex: number) => {
    const input = entityInputs[outcomeIndex];
    if (!input || !input.key.trim()) return;

    const outcome = outcomes[outcomeIndex];
    const newEntities = {
      ...outcome.entities,
      [input.key.trim()]: input.value.trim(),
    };
    updateOutcome(outcomeIndex, { entities: newEntities });
    setEntityInputs({ ...entityInputs, [outcomeIndex]: { key: '', value: '' } });
  };

  const removeEntity = (outcomeIndex: number, entityKey: string) => {
    const outcome = outcomes[outcomeIndex];
    const newEntities = { ...outcome.entities };
    delete newEntities[entityKey];
    updateOutcome(outcomeIndex, { entities: newEntities });
  };

  const updateEntityInput = (outcomeIndex: number, field: 'key' | 'value', value: string) => {
    setEntityInputs({
      ...entityInputs,
      [outcomeIndex]: {
        ...(entityInputs[outcomeIndex] || { key: '', value: '' }),
        [field]: value,
      },
    });
  };

  // Toggle between structured and raw JSON mode for response content
  const toggleResponseContentMode = (index: number) => {
    const newRawMode = new Set(rawJsonMode);
    if (newRawMode.has(index)) {
      newRawMode.delete(index);
    } else {
      newRawMode.add(index);
    }
    setRawJsonMode(newRawMode);
  };

  // Update response content from structured form
  const updateResponseContent = (index: number, content: ExpectedResponseContent) => {
    // Clean up empty arrays before saving
    const cleaned: ExpectedResponseContent = {};
    if (content.contains && content.contains.length > 0) {
      cleaned.contains = content.contains;
    }
    if (content.not_contains && content.not_contains.length > 0) {
      cleaned.not_contains = content.not_contains;
    }
    if (content.regex && content.regex.length > 0) {
      cleaned.regex = content.regex;
    }
    if (content.regex_not_match && content.regex_not_match.length > 0) {
      cleaned.regex_not_match = content.regex_not_match;
    }
    // Store as empty object if nothing defined (will auto-pass validation)
    updateOutcome(index, {
      expected_response_content: Object.keys(cleaned).length > 0 ? cleaned : undefined,
    });
  };

  // Supported Houndify CommandKinds (matches LLMMockClient ALLOWED_COMMAND_KINDS)
  const commandKinds = [
    'WeatherCommand',
    'MusicCommand',
    'NavigationCommand',
    'PhoneCommand',
    'ClientMatchCommand',
    'NoResultCommand',
    'UnknownCommand',
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h4 className="text-md font-semibold text-[var(--color-content-primary)]">
          Expected Outcomes {stepNumber && `(Step ${stepNumber})`}
        </h4>
        <button
          type="button"
          onClick={addOutcome}
          className="flex items-center gap-2 px-3 py-1.5 text-white text-sm rounded-md hover:opacity-90"
          style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
        >
          <Plus className="w-4 h-4" />
          Add Outcome
        </button>
      </div>

      {outcomes.length === 0 ? (
        <div className="text-center py-8 bg-[var(--color-surface-inset)]/50 rounded-lg border-2 border-dashed border-[var(--color-border-strong)]">
          <p className="text-[var(--color-content-muted)] text-sm mb-3">No expected outcomes configured</p>
          <button
            type="button"
            onClick={addOutcome}
            className="px-3 py-1.5 text-white text-sm rounded-md hover:opacity-90"
            style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
          >
            Add First Outcome
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {outcomes.map((outcome, index) => (
            <div key={index} className="border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)]">
              {/* Outcome Header */}
              <div className="flex items-center gap-3 p-3 bg-[var(--color-status-emerald-bg)] border-b border-[var(--color-border-default)]">
                <div className="flex-1">
                  <span className="font-semibold text-[var(--color-content-primary)]">{outcome.name}</span>
                  <span className="ml-2 text-xs text-[var(--color-content-muted)]">({outcome.outcome_code})</span>
                </div>
                <button
                  type="button"
                  onClick={() => toggleExpanded(index)}
                  className="text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)]"
                >
                  {expandedOutcomes.has(index) ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => removeOutcome(index)}
                  className="text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)]"
                  title="Remove outcome"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              {/* Outcome Content */}
              {expandedOutcomes.has(index) && (
                <div className="p-4 space-y-4">
                  {/* Outcome Code and Name */}
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                        Outcome Code <span className="text-[var(--color-status-danger)]">*</span>
                      </label>
                      <input
                        type="text"
                        value={outcome.outcome_code}
                        onChange={(e) => updateOutcome(index, { outcome_code: e.target.value })}
                        className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                        placeholder="outcome_1"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                        Name <span className="text-[var(--color-status-danger)]">*</span>
                      </label>
                      <input
                        type="text"
                        value={outcome.name}
                        onChange={(e) => updateOutcome(index, { name: e.target.value })}
                        className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                        placeholder="Success Outcome"
                        required
                      />
                    </div>
                  </div>

                  {/* Description */}
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                      Description
                    </label>
                    <textarea
                      value={outcome.description || ''}
                      onChange={(e) => updateOutcome(index, { description: e.target.value })}
                      rows={2}
                      className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                      placeholder="Describe what this outcome validates..."
                    />
                  </div>

                  {/* Houndify Settings Section */}
                  <div className="border-t border-[var(--color-border-default)] pt-4 mt-4">
                    <h5 className="text-sm font-semibold text-[var(--color-content-primary)] mb-3">Houndify Validation Settings</h5>

                    {/* Command Kind and ASR Confidence */}
                    <div className="grid grid-cols-2 gap-3 mb-3">
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                          Expected Command Kind
                        </label>
                        <select
                          value={outcome.expected_command_kind || ''}
                          onChange={(e) =>
                            updateOutcome(index, { expected_command_kind: e.target.value })
                          }
                          className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                        >
                          <option value="">Select command kind...</option>
                          {commandKinds.map((kind) => (
                            <option key={kind} value={kind}>
                              {kind}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                          Min ASR Confidence (0.0 - 1.0)
                        </label>
                        <input
                          type="number"
                          min="0"
                          max="1"
                          step="0.1"
                          value={outcome.expected_asr_confidence_min || 0.7}
                          onChange={(e) =>
                            updateOutcome(index, {
                              expected_asr_confidence_min: parseFloat(e.target.value),
                            })
                          }
                          className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                        />
                      </div>
                    </div>

                    {/* Expected Native Data Schema */}
                    <div className="mb-3">
                      <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                        Expected Native Data Schema (JSON)
                      </label>
                      <p className="text-xs text-[var(--color-content-muted)] mb-1">
                        Define validation rules for Houndify NativeData field
                      </p>
                      <textarea
                        value={formatJsonField(outcome.expected_native_data_schema)}
                        onChange={(e) =>
                          updateOutcome(index, {
                            expected_native_data_schema: parseJsonField(e.target.value),
                          })
                        }
                        rows={3}
                        className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                        placeholder='{"required_fields": ["Artist"], "field_types": {"Artist": "string"}}'
                      />
                    </div>

                    {/* Conversation Requirements */}
                    <div>
                      <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                        Conversation Requirements (JSON)
                      </label>
                      <p className="text-xs text-[var(--color-content-muted)] mb-1">
                        Multi-turn conversation state requirements
                      </p>
                      <textarea
                        value={formatJsonField(outcome.conversation_requirements)}
                        onChange={(e) =>
                          updateOutcome(index, {
                            conversation_requirements: parseJsonField(e.target.value),
                          })
                        }
                        rows={3}
                        className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                        placeholder='{"requires_context": true, "context_vars": ["location"]}'
                      />
                    </div>
                  </div>

                  {/* Expected Response Content - Structured Form with Raw JSON Toggle */}
                  <div className="border-t border-[var(--color-border-default)] pt-4 mt-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h5 className="text-sm font-semibold text-[var(--color-content-primary)]">
                          Response Content Validation (Optional)
                        </h5>
                        <p className="text-xs text-[var(--color-content-muted)]">
                          Define patterns the AI response must match or avoid
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => toggleResponseContentMode(index)}
                        className="flex items-center gap-1.5 px-2 py-1 text-xs text-[var(--color-content-secondary)] bg-[var(--color-surface-inset)] rounded hover:bg-[var(--color-interactive-active)]"
                        title={rawJsonMode.has(index) ? 'Switch to structured form' : 'Switch to raw JSON'}
                      >
                        {rawJsonMode.has(index) ? (
                          <>
                            <FormInput className="w-3 h-3" />
                            Structured
                          </>
                        ) : (
                          <>
                            <Code className="w-3 h-3" />
                            Raw JSON
                          </>
                        )}
                      </button>
                    </div>

                    {rawJsonMode.has(index) ? (
                      /* Raw JSON Mode */
                      <div>
                        <p className="text-xs text-[var(--color-content-muted)] mb-1">
                          Edit response content validation rules as JSON
                        </p>
                        <textarea
                          value={formatResponseContent(outcome.expected_response_content)}
                          onChange={(e) =>
                            updateOutcome(index, {
                              expected_response_content: parseResponseContent(e.target.value),
                            })
                          }
                          rows={6}
                          className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                          placeholder='{"contains": ["sunny"], "not_contains": ["error"]}'
                        />
                      </div>
                    ) : (
                      /* Structured Form Mode */
                      <ResponseContentForm
                        value={toResponseContentObject(outcome.expected_response_content)}
                        onChange={(content) => updateResponseContent(index, content)}
                      />
                    )}
                  </div>

                  {/* Entities */}
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                      Expected Entities
                    </label>
                    <div className="space-y-2">
                      {/* Existing Entities */}
                      {outcome.entities && Object.keys(outcome.entities).length > 0 && (
                        <div className="space-y-1 mb-2">
                          {Object.entries(outcome.entities).map(([key, value]) => (
                            <div
                              key={key}
                              className="flex items-center gap-2 p-2 bg-[var(--color-surface-inset)]/50 rounded border border-[var(--color-border-default)]"
                            >
                              <span className="text-sm font-medium text-[var(--color-content-secondary)]">{key}:</span>
                              <span className="text-sm text-[var(--color-content-secondary)]">{String(value)}</span>
                              <button
                                type="button"
                                onClick={() => removeEntity(index, key)}
                                className="ml-auto text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)]"
                              >
                                <Trash2 className="w-3 h-3" />
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                      {/* Add Entity */}
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={entityInputs[index]?.key || ''}
                          onChange={(e) => updateEntityInput(index, 'key', e.target.value)}
                          className="flex-1 px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                          placeholder="Entity name (e.g., location)"
                        />
                        <input
                          type="text"
                          value={entityInputs[index]?.value || ''}
                          onChange={(e) => updateEntityInput(index, 'value', e.target.value)}
                          className="flex-1 px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                          placeholder="Expected value"
                        />
                        <button
                          type="button"
                          onClick={() => addEntity(index)}
                          className="px-3 py-2 bg-[var(--color-interactive-active)] text-[var(--color-content-secondary)] rounded-md hover:bg-[var(--color-interactive-active)] text-sm"
                        >
                          Add
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ExpectedOutcomeForm;
