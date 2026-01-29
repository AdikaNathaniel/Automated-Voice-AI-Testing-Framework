/**
 * Enhanced Create Scenario Modal
 *
 * Complete scenario creation with full feature parity to page version:
 * - Step 1: Scenario metadata (name, description, category, validation mode)
 * - Step 2: Conversation steps with multi-language support & auto-translate
 * - Step 3: Expected outcomes configuration (optional advanced validation)
 * - Step 4: Review and create
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  X,
  Plus,
  Trash2,
  ChevronRight,
  ChevronLeft,
  FileText,
  MessageSquare,
  Sparkles,
  Check,
  AlertCircle,
  Loader2,
  Globe,
  Languages,
  Target,
  ChevronDown,
  ChevronUp,
  Code,
  FormInput,
  Volume2,
  Car,
  Building,
  Factory,
  Gauge,
  Info,
} from 'lucide-react';
import axios from 'axios';
import categoryService from '../../services/category.service';
import { Select } from '../common/FormInputs';

interface Category {
  id: string;
  name: string;
  display_name: string;
}

// Supported languages with display names and flags
const SUPPORTED_LANGUAGES = [
  { code: 'en-US', name: 'English (US)', flag: '🇺🇸' },
  { code: 'es-ES', name: 'Spanish (Spain)', flag: '🇪🇸' },
  { code: 'fr-FR', name: 'French (France)', flag: '🇫🇷' },
  { code: 'de-DE', name: 'German (Germany)', flag: '🇩🇪' },
  { code: 'it-IT', name: 'Italian (Italy)', flag: '🇮🇹' },
  { code: 'pt-BR', name: 'Portuguese (Brazil)', flag: '🇧🇷' },
  { code: 'ja-JP', name: 'Japanese (Japan)', flag: '🇯🇵' },
  { code: 'zh-CN', name: 'Chinese (Simplified)', flag: '🇨🇳' },
  { code: 'ko-KR', name: 'Korean (Korea)', flag: '🇰🇷' },
  { code: 'ar-SA', name: 'Arabic (Saudi Arabia)', flag: '🇸🇦' },
];

// Supported Houndify CommandKinds (matches LLMMockClient ALLOWED_COMMAND_KINDS)
const COMMAND_KINDS = [
  'WeatherCommand',
  'MusicCommand',
  'NavigationCommand',
  'PhoneCommand',
  'ClientMatchCommand',
  'NoResultCommand',
  'UnknownCommand',
];

interface LanguageVariant {
  language_code: string;
  user_utterance: string;
}

interface ExpectedResponseContent {
  contains?: string[];
  not_contains?: string[];
  regex?: string[];
  regex_not_match?: string[];
}

interface ExpectedOutcomeData {
  outcome_code: string;
  name: string;
  description?: string;
  expected_command_kind?: string;
  expected_asr_confidence_min?: number;
  expected_response_content?: ExpectedResponseContent;
  expected_native_data_schema?: Record<string, any>;
  conversation_requirements?: Record<string, any>;
  entities?: Record<string, string>;
}

interface StepData {
  step_order: number;
  user_utterance: string;
  follow_up_action?: string;
  step_metadata: {
    primary_language: string;
    language_variants: LanguageVariant[];
    [key: string]: any;
  };
  expected_outcomes: ExpectedOutcomeData[];
}

export interface CreateScenarioData {
  name: string;
  description: string;
  version: string;
  is_active: boolean;
  validation_mode: 'houndify' | 'llm_ensemble' | 'hybrid';
  script_metadata: {
    category: string;
    tags: string[];
    noise_config?: NoiseConfig;
  };
  steps: StepData[];
}

interface CreateScenarioModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateScenarioData) => Promise<void>;
}

type ModalStep = 'details' | 'steps' | 'outcomes' | 'review';

const VALIDATION_MODES = [
  { value: 'hybrid', label: 'Hybrid', description: 'Best of both - Houndify + LLM validation' },
  { value: 'houndify', label: 'Houndify Only', description: 'Fast, structured command validation' },
  { value: 'llm_ensemble', label: 'LLM Ensemble', description: 'Deep semantic understanding' },
] as const;

const FOLLOW_UP_ACTIONS = [
  { value: '', label: 'None' },
  { value: 'retry', label: 'Retry on Failure' },
  { value: 'skip_on_error', label: 'Skip on Error' },
  { value: 'end_conversation', label: 'End Conversation' },
] as const;

// Noise configuration types and profiles
interface NoiseConfig {
  enabled: boolean;
  profile: string;
  snr_db?: number;
  randomize_snr: boolean;
  snr_variance: number;
}

interface NoiseProfile {
  name: string;
  category: 'vehicle' | 'environmental' | 'industrial';
  description: string;
  default_snr_db: number;
  difficulty: 'easy' | 'medium' | 'hard' | 'very_hard' | 'extreme';
  estimated_wer_increase: number;
}

const NOISE_PROFILES: NoiseProfile[] = [
  // Vehicle
  { name: 'car_cabin_idle', category: 'vehicle', description: 'Parked car, engine running', default_snr_db: 25, difficulty: 'easy', estimated_wer_increase: 5 },
  { name: 'car_cabin_city', category: 'vehicle', description: 'City driving, moderate traffic', default_snr_db: 15, difficulty: 'medium', estimated_wer_increase: 12 },
  { name: 'car_cabin_highway', category: 'vehicle', description: 'Highway driving, wind noise', default_snr_db: 5, difficulty: 'hard', estimated_wer_increase: 25 },
  // Environmental
  { name: 'office_quiet', category: 'environmental', description: 'Quiet office environment', default_snr_db: 35, difficulty: 'easy', estimated_wer_increase: 2 },
  { name: 'office_busy', category: 'environmental', description: 'Busy open office', default_snr_db: 10, difficulty: 'hard', estimated_wer_increase: 18 },
  { name: 'crowd_sparse', category: 'environmental', description: 'Light crowd noise', default_snr_db: 15, difficulty: 'medium', estimated_wer_increase: 10 },
  { name: 'crowd_dense', category: 'environmental', description: 'Dense crowd, multiple voices', default_snr_db: 0, difficulty: 'very_hard', estimated_wer_increase: 35 },
  // Industrial
  { name: 'factory_light', category: 'industrial', description: 'Light machinery', default_snr_db: 10, difficulty: 'hard', estimated_wer_increase: 20 },
  { name: 'factory_heavy', category: 'industrial', description: 'Heavy machinery', default_snr_db: 0, difficulty: 'very_hard', estimated_wer_increase: 40 },
  { name: 'construction', category: 'industrial', description: 'Construction site', default_snr_db: -5, difficulty: 'extreme', estimated_wer_increase: 50 },
];

const DIFFICULTY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  easy: { bg: 'bg-[var(--color-status-emerald-bg)]', text: 'text-[var(--color-status-emerald)]', border: 'border-[var(--color-status-emerald-bg)]' },
  medium: { bg: 'bg-[var(--color-status-teal-bg)]', text: 'text-[var(--color-status-teal)]', border: 'border-[var(--color-status-teal-bg)]' },
  hard: { bg: 'bg-[var(--color-status-amber-bg)]', text: 'text-[var(--color-status-amber)]', border: 'border-[var(--color-status-amber-bg)]' },
  very_hard: { bg: 'bg-[var(--color-status-amber-bg)]', text: 'text-[var(--color-status-amber)]', border: 'border-[var(--color-status-amber-bg)]' },
  extreme: { bg: 'bg-[var(--color-status-danger-bg)]', text: 'text-[var(--color-status-danger)]', border: 'border-[var(--color-status-danger)]' },
};

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'vehicle': return Car;
    case 'environmental': return Building;
    case 'industrial': return Factory;
    default: return Volume2;
  }
};

const getLanguageInfo = (code: string) => {
  return SUPPORTED_LANGUAGES.find((l) => l.code === code) || { code, name: code, flag: '🌐' };
};

const createDefaultStep = (): StepData => ({
  step_order: 1,
  user_utterance: '',
  follow_up_action: '',
  step_metadata: {
    primary_language: 'en-US',
    language_variants: [{ language_code: 'en-US', user_utterance: '' }],
  },
  expected_outcomes: [],
});

export const CreateScenarioModal: React.FC<CreateScenarioModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [currentStep, setCurrentStep] = useState<ModalStep>('details');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);

  // Form state
  const [formData, setFormData] = useState<CreateScenarioData>({
    name: '',
    description: '',
    version: '1.0.0',
    is_active: true,
    validation_mode: 'hybrid',
    script_metadata: {
      category: '',
      tags: [],
      noise_config: {
        enabled: false,
        profile: 'car_cabin_city',
        snr_db: undefined,
        randomize_snr: false,
        snr_variance: 3,
      },
    },
    steps: [createDefaultStep()],
  });

  const [tagInput, setTagInput] = useState('');
  const [noiseConfigExpanded, setNoiseConfigExpanded] = useState(false);
  const [selectedNoiseCategory, setSelectedNoiseCategory] = useState<'vehicle' | 'environmental' | 'industrial'>('vehicle');
  const [selectedStepIndex, setSelectedStepIndex] = useState(0);
  const [isTranslating, setIsTranslating] = useState<number | null>(null);
  const [expandedOutcomes, setExpandedOutcomes] = useState<Set<string>>(new Set());
  const [showAdvancedOutcome, setShowAdvancedOutcome] = useState<Set<string>>(new Set());
  const [entityInputs, setEntityInputs] = useState<Record<string, { key: string; value: string }>>({});

  // Auto-translate language selector state
  const [showTranslateSelector, setShowTranslateSelector] = useState<number | null>(null);
  const [selectedTranslateLanguages, setSelectedTranslateLanguages] = useState<string[]>([]);

  // Response content mode toggle (structured vs raw JSON)
  const [rawJsonMode, setRawJsonMode] = useState<Set<string>>(new Set());

  // Response content pattern input state
  const [patternInputs, setPatternInputs] = useState<Record<string, {
    contains: string;
    not_contains: string;
    regex: string;
    regex_not_match: string;
  }>>({});

  // Load categories
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await categoryService.getCategories({});
        setCategories(response.categories || []);
      } catch (err) {
        console.error('Failed to load categories:', err);
      }
    };
    if (isOpen) {
      loadCategories();
    }
  }, [isOpen]);

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setCurrentStep('details');
      setError(null);
      setFormData({
        name: '',
        description: '',
        version: '1.0.0',
        is_active: true,
        validation_mode: 'hybrid',
        script_metadata: {
          category: '',
          tags: [],
          noise_config: {
            enabled: false,
            profile: 'car_cabin_city',
            snr_db: undefined,
            randomize_snr: false,
            snr_variance: 3,
          },
        },
        steps: [createDefaultStep()],
      });
      setTagInput('');
      setNoiseConfigExpanded(false);
      setSelectedNoiseCategory('vehicle');
      setSelectedStepIndex(0);
      setExpandedOutcomes(new Set());
      setShowAdvancedOutcome(new Set());
      setEntityInputs({});
      setShowTranslateSelector(null);
      setSelectedTranslateLanguages([]);
      setRawJsonMode(new Set());
      setPatternInputs({});
    }
  }, [isOpen]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isSubmitting) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, isSubmitting, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const updateFormData = useCallback((updates: Partial<CreateScenarioData>) => {
    setFormData((prev) => ({ ...prev, ...updates }));
    setError(null);
  }, []);

  // Tag management
  const addTag = () => {
    const tag = tagInput.trim().toLowerCase();
    if (tag && !formData.script_metadata.tags.includes(tag)) {
      updateFormData({
        script_metadata: {
          ...formData.script_metadata,
          tags: [...formData.script_metadata.tags, tag],
        },
      });
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    updateFormData({
      script_metadata: {
        ...formData.script_metadata,
        tags: formData.script_metadata.tags.filter((t) => t !== tagToRemove),
      },
    });
  };

  // Noise config management
  const updateNoiseConfig = (updates: Partial<NoiseConfig>) => {
    updateFormData({
      script_metadata: {
        ...formData.script_metadata,
        noise_config: {
          ...formData.script_metadata.noise_config!,
          ...updates,
        },
      },
    });
  };

  const getSelectedProfile = (): NoiseProfile | undefined => {
    return NOISE_PROFILES.find((p) => p.name === formData.script_metadata.noise_config?.profile);
  };

  const getEffectiveSNR = (): number => {
    const profile = getSelectedProfile();
    return formData.script_metadata.noise_config?.snr_db ?? profile?.default_snr_db ?? 15;
  };

  // Step management
  const addStep = () => {
    const newStep: StepData = {
      ...createDefaultStep(),
      step_order: formData.steps.length + 1,
    };
    updateFormData({ steps: [...formData.steps, newStep] });
  };

  const removeStep = (index: number) => {
    if (formData.steps.length <= 1) return;
    const newSteps = formData.steps.filter((_, i) => i !== index);
    newSteps.forEach((step, i) => {
      step.step_order = i + 1;
    });
    updateFormData({ steps: newSteps });
    if (selectedStepIndex >= newSteps.length) {
      setSelectedStepIndex(Math.max(0, newSteps.length - 1));
    }
  };

  const updateStep = (index: number, updates: Partial<StepData>) => {
    const newSteps = [...formData.steps];
    newSteps[index] = { ...newSteps[index], ...updates };

    // Keep user_utterance in sync with primary language variant
    if (updates.step_metadata?.language_variants) {
      const primaryLang = updates.step_metadata.primary_language || newSteps[index].step_metadata.primary_language;
      const primaryVariant = updates.step_metadata.language_variants.find(
        (v) => v.language_code === primaryLang
      );
      if (primaryVariant) {
        newSteps[index].user_utterance = primaryVariant.user_utterance;
      }
    }

    updateFormData({ steps: newSteps });
  };

  // Language variant management
  const addLanguageVariant = (stepIndex: number, languageCode: string) => {
    const step = formData.steps[stepIndex];
    if ((step.step_metadata.language_variants || []).some((v) => v.language_code === languageCode)) return;

    updateStep(stepIndex, {
      step_metadata: {
        ...step.step_metadata,
        language_variants: [
          ...step.step_metadata.language_variants,
          { language_code: languageCode, user_utterance: '' },
        ],
      },
    });
  };

  const removeLanguageVariant = (stepIndex: number, languageCode: string) => {
    const step = formData.steps[stepIndex];
    if (languageCode === step.step_metadata.primary_language) {
      setError('Cannot remove primary language');
      return;
    }
    updateStep(stepIndex, {
      step_metadata: {
        ...step.step_metadata,
        language_variants: step.step_metadata.language_variants.filter(
          (v) => v.language_code !== languageCode
        ),
      },
    });
  };

  const updateLanguageVariant = (stepIndex: number, languageCode: string, utterance: string) => {
    const step = formData.steps[stepIndex];
    const newVariants = (step.step_metadata.language_variants || []).map((v) =>
      v.language_code === languageCode ? { ...v, user_utterance: utterance } : v
    );
    updateStep(stepIndex, {
      step_metadata: { ...step.step_metadata, language_variants: newVariants },
    });
  };

  const setPrimaryLanguage = (stepIndex: number, languageCode: string) => {
    const step = formData.steps[stepIndex];
    const primaryVariant = step.step_metadata.language_variants?.find(
      (v) => v.language_code === languageCode
    );
    updateStep(stepIndex, {
      user_utterance: primaryVariant?.user_utterance || '',
      step_metadata: { ...step.step_metadata, primary_language: languageCode },
    });
  };

  // Get available languages for a step (not already added)
  const getAvailableLanguages = (stepIndex: number): string[] => {
    const step = formData.steps[stepIndex];
    return SUPPORTED_LANGUAGES
      .map((l) => l.code)
      .filter((code) => !(step.step_metadata.language_variants || []).some((v) => v.language_code === code));
  };

  // Open translate selector for a step
  const openTranslateSelector = (stepIndex: number) => {
    const step = formData.steps[stepIndex];
    const primaryVariant = step.step_metadata.language_variants?.find(
      (v) => v.language_code === step.step_metadata.primary_language
    );

    if (!primaryVariant?.user_utterance) {
      setError('Please fill in the primary language utterance first');
      return;
    }

    const available = getAvailableLanguages(stepIndex);
    if (available.length === 0) {
      setError('All languages already have variants');
      return;
    }

    setSelectedTranslateLanguages(available); // Pre-select all
    setShowTranslateSelector(stepIndex);
  };

  // Toggle language selection for translation
  const toggleTranslateLanguage = (langCode: string) => {
    setSelectedTranslateLanguages((prev) =>
      prev.includes(langCode)
        ? prev.filter((code) => code !== langCode)
        : [...prev, langCode]
    );
  };

  // Select all available languages for translation
  const selectAllTranslateLanguages = (stepIndex: number) => {
    setSelectedTranslateLanguages(getAvailableLanguages(stepIndex));
  };

  // Deselect all languages
  const deselectAllTranslateLanguages = () => {
    setSelectedTranslateLanguages([]);
  };

  // Perform translation with selected languages
  const performTranslation = async (stepIndex: number) => {
    if (selectedTranslateLanguages.length === 0) {
      setError('Please select at least one language to translate to');
      return;
    }

    const step = formData.steps[stepIndex];
    const primaryVariant = step.step_metadata.language_variants?.find(
      (v) => v.language_code === step.step_metadata.primary_language
    );

    if (!primaryVariant) {
      setError('Primary language variant not found');
      return;
    }

    setIsTranslating(stepIndex);
    setError(null);

    try {
      const response = await axios.post('/api/v1/auto-translation/auto-translate-step', {
        user_utterance: primaryVariant.user_utterance,
        source_lang: step.step_metadata.primary_language,
        target_languages: selectedTranslateLanguages,
      });

      const translations = response.data.data.translations;

      // Filter out languages that already exist (backend always includes source language)
      const existingLangCodes = (step.step_metadata.language_variants || []).map((v) => v.language_code);
      const newVariants = Object.entries(translations)
        .filter(([lang]) => !existingLangCodes.includes(lang))
        .map(([lang, trans]: [string, any]) => ({
          language_code: lang,
          user_utterance: trans.user_utterance,
        }));

      updateStep(stepIndex, {
        step_metadata: {
          ...step.step_metadata,
          language_variants: [...step.step_metadata.language_variants, ...newVariants],
        },
      });

      setShowTranslateSelector(null);
      setSelectedTranslateLanguages([]);
    } catch (err: any) {
      setError(`Translation failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsTranslating(null);
    }
  };

  // Expected Outcomes management
  const addOutcome = (stepIndex: number) => {
    const step = formData.steps[stepIndex];
    const newOutcome: ExpectedOutcomeData = {
      outcome_code: `outcome_${step.expected_outcomes.length + 1}`,
      name: `Outcome ${step.expected_outcomes.length + 1}`,
      description: '',
      expected_command_kind: '',
      expected_asr_confidence_min: 0.7,
      expected_response_content: { contains: [], not_contains: [], regex: [], regex_not_match: [] },
      expected_native_data_schema: undefined,
      conversation_requirements: undefined,
      entities: {},
    };
    updateStep(stepIndex, {
      expected_outcomes: [...step.expected_outcomes, newOutcome],
    });
    const key = `${stepIndex}-${step.expected_outcomes.length}`;
    setExpandedOutcomes((prev) => new Set([...prev, key]));
  };

  const removeOutcome = (stepIndex: number, outcomeIndex: number) => {
    const step = formData.steps[stepIndex];
    updateStep(stepIndex, {
      expected_outcomes: step.expected_outcomes.filter((_, i) => i !== outcomeIndex),
    });
  };

  const updateOutcome = (stepIndex: number, outcomeIndex: number, updates: Partial<ExpectedOutcomeData>) => {
    const step = formData.steps[stepIndex];
    const newOutcomes = [...step.expected_outcomes];
    newOutcomes[outcomeIndex] = { ...newOutcomes[outcomeIndex], ...updates };
    updateStep(stepIndex, { expected_outcomes: newOutcomes });
  };

  const toggleOutcomeExpanded = (key: string) => {
    setExpandedOutcomes((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const toggleAdvancedOutcome = (key: string) => {
    setShowAdvancedOutcome((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  // Toggle raw JSON mode for response content
  const toggleRawJsonMode = (key: string) => {
    setRawJsonMode((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  // Response content pattern helpers
  const addPattern = (
    stepIndex: number,
    outcomeIndex: number,
    field: 'contains' | 'not_contains' | 'regex' | 'regex_not_match',
    value: string
  ) => {
    if (!value.trim()) return;
    const outcome = formData.steps[stepIndex].expected_outcomes[outcomeIndex];
    const currentPatterns = outcome.expected_response_content?.[field] || [];
    if (!currentPatterns.includes(value.trim())) {
      updateOutcome(stepIndex, outcomeIndex, {
        expected_response_content: {
          ...outcome.expected_response_content,
          [field]: [...currentPatterns, value.trim()],
        },
      });
    }
    // Clear the input
    const key = `${stepIndex}-${outcomeIndex}`;
    setPatternInputs({
      ...patternInputs,
      [key]: { ...patternInputs[key], [field]: '' },
    });
  };

  const removePattern = (
    stepIndex: number,
    outcomeIndex: number,
    field: 'contains' | 'not_contains' | 'regex' | 'regex_not_match',
    index: number
  ) => {
    const outcome = formData.steps[stepIndex].expected_outcomes[outcomeIndex];
    const currentPatterns = outcome.expected_response_content?.[field] || [];
    updateOutcome(stepIndex, outcomeIndex, {
      expected_response_content: {
        ...outcome.expected_response_content,
        [field]: currentPatterns.filter((_, i) => i !== index),
      },
    });
  };

  const getPatternInput = (key: string, field: string): string => {
    return (patternInputs[key] as any)?.[field] || '';
  };

  const setPatternInput = (key: string, field: string, value: string) => {
    setPatternInputs({
      ...patternInputs,
      [key]: { ...patternInputs[key], [field]: value },
    });
  };

  // Format response content for raw JSON display
  const formatResponseContentJson = (content: ExpectedResponseContent | undefined): string => {
    if (!content || Object.keys(content).length === 0) return '';
    // Clean empty arrays
    const cleaned: ExpectedResponseContent = {};
    if (content.contains && content.contains.length > 0) cleaned.contains = content.contains;
    if (content.not_contains && content.not_contains.length > 0) cleaned.not_contains = content.not_contains;
    if (content.regex && content.regex.length > 0) cleaned.regex = content.regex;
    if (content.regex_not_match && content.regex_not_match.length > 0) cleaned.regex_not_match = content.regex_not_match;
    if (Object.keys(cleaned).length === 0) return '';
    return JSON.stringify(cleaned, null, 2);
  };

  // Parse response content from raw JSON
  const parseResponseContentJson = (value: string): ExpectedResponseContent | undefined => {
    if (!value.trim()) return undefined;
    try {
      return JSON.parse(value);
    } catch {
      return undefined;
    }
  };

  // Entity management for outcomes
  const addEntity = (outcomeKey: string, stepIndex: number, outcomeIndex: number) => {
    const input = entityInputs[outcomeKey];
    if (!input?.key?.trim()) return;

    const outcome = formData.steps[stepIndex].expected_outcomes[outcomeIndex];
    updateOutcome(stepIndex, outcomeIndex, {
      entities: { ...outcome.entities, [input.key.trim()]: input.value?.trim() || '' },
    });
    setEntityInputs({ ...entityInputs, [outcomeKey]: { key: '', value: '' } });
  };

  const removeEntity = (stepIndex: number, outcomeIndex: number, entityKey: string) => {
    const outcome = formData.steps[stepIndex].expected_outcomes[outcomeIndex];
    const newEntities = { ...outcome.entities };
    delete newEntities[entityKey];
    updateOutcome(stepIndex, outcomeIndex, { entities: newEntities });
  };

  // JSON field helpers
  const formatJson = (value: Record<string, any> | undefined): string => {
    if (!value || Object.keys(value).length === 0) return '';
    return JSON.stringify(value, null, 2);
  };

  const parseJson = (value: string): Record<string, any> | undefined => {
    if (!value.trim()) return undefined;
    try {
      return JSON.parse(value);
    } catch {
      return undefined;
    }
  };

  // Validation
  const validateDetails = (): boolean => {
    if (!formData.name.trim()) {
      setError('Scenario name is required');
      return false;
    }
    if (formData.name.trim().length < 3) {
      setError('Scenario name must be at least 3 characters');
      return false;
    }
    return true;
  };

  const validateSteps = (): boolean => {
    for (let i = 0; i < formData.steps.length; i++) {
      const step = formData.steps[i];
      const primaryVariant = step.step_metadata.language_variants?.find(
        (v) => v.language_code === step.step_metadata.primary_language
      );
      if (!primaryVariant?.user_utterance.trim()) {
        setError(`Step ${i + 1}: User utterance is required for primary language`);
        return false;
      }
    }
    return true;
  };

  // Navigation
  const handleNext = () => {
    setError(null);
    if (currentStep === 'details') {
      if (validateDetails()) setCurrentStep('steps');
    } else if (currentStep === 'steps') {
      if (validateSteps()) setCurrentStep('outcomes');
    } else if (currentStep === 'outcomes') {
      setCurrentStep('review');
    }
  };

  const handleBack = () => {
    setError(null);
    if (currentStep === 'steps') setCurrentStep('details');
    else if (currentStep === 'outcomes') setCurrentStep('steps');
    else if (currentStep === 'review') setCurrentStep('outcomes');
  };

  const handleSubmit = async () => {
    if (!validateDetails() || !validateSteps()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await onSubmit(formData);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to create scenario');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  const stepIndicators = [
    { key: 'details', label: 'Details', icon: FileText },
    { key: 'steps', label: 'Steps', icon: MessageSquare },
    { key: 'outcomes', label: 'Validation', icon: Target },
    { key: 'review', label: 'Review', icon: Sparkles },
  ] as const;

  const currentStepIndex = stepIndicators.findIndex((s) => s.key === currentStep);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-3xl bg-[var(--color-surface-raised)] rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex-shrink-0 px-6 pt-6 pb-4 border-b border-[var(--color-border-default)]">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-[var(--color-content-primary)] flex items-center gap-2">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center"
                style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
              >
                <Plus className="w-4 h-4 text-white" />
              </div>
              Create New Scenario
            </h2>
            <button
              onClick={onClose}
              disabled={isSubmitting}
              className="p-2 text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)] hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors disabled:opacity-50"
              aria-label="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Step Indicator */}
          <div className="flex items-center justify-center gap-1">
            {stepIndicators.map((step, index) => {
              const Icon = step.icon;
              const isActive = step.key === currentStep;
              const isCompleted = index < currentStepIndex;

              return (
                <React.Fragment key={step.key}>
                  <button
                    onClick={() => {
                      if (isCompleted) {
                        setCurrentStep(step.key);
                        setError(null);
                      }
                    }}
                    disabled={!isCompleted && !isActive}
                    className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-gradient-to-r from-[#2A6B6E] to-[#11484D] text-white shadow-md'
                        : isCompleted
                        ? 'bg-[var(--color-status-emerald-bg)] text-[var(--color-status-emerald)] cursor-pointer hover:bg-[var(--color-status-emerald-bg)]'
                        : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)] cursor-not-allowed'
                    }`}
                  >
                    {isCompleted ? <Check className="w-3.5 h-3.5" /> : <Icon className="w-3.5 h-3.5" />}
                    <span className="hidden sm:inline">{step.label}</span>
                  </button>
                  {index < stepIndicators.length - 1 && (
                    <ChevronRight className="w-3.5 h-3.5 text-[var(--color-content-muted)]" />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="flex-shrink-0 mx-6 mt-4 p-3 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-[var(--color-status-danger)] flex-shrink-0 mt-0.5" />
            <p className="text-sm text-[var(--color-status-danger)]">{error}</p>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-5">
          {/* STEP 1: Details */}
          {currentStep === 'details' && (
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1.5">
                  Scenario Name <span className="text-[var(--color-status-danger)]">*</span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => updateFormData({ name: e.target.value })}
                  placeholder="e.g., Play music while navigating home"
                  className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder-[var(--color-content-muted)] focus:outline-none focus:ring-2 focus:ring-[#2A6B6E]/30 focus:border-[#2A6B6E]"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1.5">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => updateFormData({ description: e.target.value })}
                  placeholder="Describe what this scenario tests..."
                  rows={3}
                  className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder-[var(--color-content-muted)] focus:outline-none focus:ring-2 focus:ring-[#2A6B6E]/30 focus:border-[#2A6B6E] resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1.5">
                    Category
                  </label>
                  <Select
                    value={formData.script_metadata.category}
                    onChange={(e) =>
                      updateFormData({
                        script_metadata: { ...formData.script_metadata, category: e.target.value },
                      })
                    }
                    className="w-full"
                  >
                    <option value="">Select category...</option>
                    {categories.map((cat) => (
                      <option key={cat.id} value={cat.name}>
                        {cat.display_name}
                      </option>
                    ))}
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1.5">
                    Validation Mode
                  </label>
                  <Select
                    value={formData.validation_mode}
                    onChange={(e) => updateFormData({ validation_mode: e.target.value as any })}
                    className="w-full"
                  >
                    {VALIDATION_MODES.map((mode) => (
                      <option key={mode.value} value={mode.value}>
                        {mode.label}
                      </option>
                    ))}
                  </Select>
                  <p className="mt-1 text-xs text-[var(--color-content-muted)]">
                    {VALIDATION_MODES.find((m) => m.value === formData.validation_mode)?.description}
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1.5">
                  Tags
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        addTag();
                      }
                    }}
                    placeholder="Add a tag..."
                    className="flex-1 px-4 py-2 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder-[var(--color-content-muted)] focus:outline-none focus:ring-2 focus:ring-[#2A6B6E]/30 focus:border-[#2A6B6E]"
                  />
                  <button
                    type="button"
                    onClick={addTag}
                    className="px-4 py-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] rounded-xl hover:bg-[var(--color-interactive-active)] font-medium"
                  >
                    Add
                  </button>
                </div>
                {formData.script_metadata.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {formData.script_metadata.tags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center gap-1 px-2.5 py-1 bg-[#2A6B6E]/10 text-[var(--color-brand-primary)] rounded-lg text-sm"
                      >
                        {tag}
                        <button type="button" onClick={() => removeTag(tag)} className="hover:text-[var(--color-status-danger)]">
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Audio Environment Simulation */}
              <div className="border border-[var(--color-border-default)] rounded-xl overflow-hidden">
                <button
                  type="button"
                  onClick={() => setNoiseConfigExpanded(!noiseConfigExpanded)}
                  className="w-full flex items-center justify-between p-3 text-left hover:bg-[var(--color-interactive-hover)]/50 transition-colors"
                >
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-400/20 to-cyan-500/20 flex items-center justify-center">
                      <Volume2 className="w-4 h-4 text-[var(--color-status-teal)]" />
                    </div>
                    <div>
                      <span className="font-medium text-[var(--color-content-primary)] text-sm">
                        Audio Environment
                      </span>
                      <p className="text-xs text-[var(--color-content-muted)]">
                        Simulate background noise for robustness testing
                      </p>
                    </div>
                    {formData.script_metadata.noise_config?.enabled && (
                      <span className="px-2 py-0.5 text-[10px] font-medium bg-[var(--color-status-teal-bg)] text-[var(--color-status-teal)] rounded-full">
                        Active
                      </span>
                    )}
                  </div>
                  <ChevronDown
                    className={`w-4 h-4 text-[var(--color-content-muted)] transition-transform ${noiseConfigExpanded ? 'rotate-180' : ''}`}
                  />
                </button>

                {noiseConfigExpanded && (
                  <div className="px-3 pb-3 space-y-3 border-t border-[var(--color-border-default)] pt-3">
                    {/* Enable Toggle */}
                    <div className="flex items-center justify-between p-2.5 bg-[var(--color-surface-inset)]/50 rounded-lg">
                      <span className="text-sm text-[var(--color-content-secondary)]">Enable noise injection</span>
                      <div
                        className={`w-10 h-5 rounded-full relative cursor-pointer transition-colors ${
                          formData.script_metadata.noise_config?.enabled
                            ? 'bg-gradient-to-r from-teal-400 to-cyan-500'
                            : 'bg-[var(--color-interactive-active)]'
                        }`}
                        onClick={() => updateNoiseConfig({ enabled: !formData.script_metadata.noise_config?.enabled })}
                      >
                        <div
                          className={`absolute top-0.5 w-4 h-4 bg-[var(--color-surface-overlay)] rounded-full shadow transition-all ${
                            formData.script_metadata.noise_config?.enabled ? 'left-5' : 'left-0.5'
                          }`}
                        />
                      </div>
                    </div>

                    {formData.script_metadata.noise_config?.enabled && (
                      <>
                        {/* Category Tabs */}
                        <div className="flex gap-1 p-1 bg-[var(--color-surface-inset)] rounded-lg">
                          {(['vehicle', 'environmental', 'industrial'] as const).map((cat) => {
                            const Icon = getCategoryIcon(cat);
                            return (
                              <button
                                key={cat}
                                type="button"
                                onClick={() => setSelectedNoiseCategory(cat)}
                                className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-md text-xs font-medium transition-colors ${
                                  selectedNoiseCategory === cat
                                    ? 'bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] shadow-sm'
                                    : 'text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)]'
                                }`}
                              >
                                <Icon className="w-3.5 h-3.5" />
                                {cat.charAt(0).toUpperCase() + cat.slice(1)}
                              </button>
                            );
                          })}
                        </div>

                        {/* Profile Grid */}
                        <div className="grid grid-cols-2 gap-2">
                          {NOISE_PROFILES.filter((p) => p.category === selectedNoiseCategory).map((profile) => {
                            const isSelected = formData.script_metadata.noise_config?.profile === profile.name;
                            const colors = DIFFICULTY_COLORS[profile.difficulty];

                            return (
                              <button
                                key={profile.name}
                                type="button"
                                onClick={() => updateNoiseConfig({ profile: profile.name, snr_db: undefined })}
                                className={`p-2.5 rounded-lg border text-left transition-all ${
                                  isSelected
                                    ? 'border-[var(--color-status-teal)] bg-[var(--color-status-teal-bg)]'
                                    : 'border-[var(--color-border-default)] hover:border-[var(--color-status-teal)]/50'
                                }`}
                              >
                                <div className="flex items-center justify-between mb-1">
                                  <span className="text-xs font-medium text-[var(--color-content-primary)]">
                                    {profile.name.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                                  </span>
                                  <span className={`px-1.5 py-0.5 text-[9px] font-medium rounded ${colors.bg} ${colors.text}`}>
                                    {profile.difficulty.replace('_', ' ')}
                                  </span>
                                </div>
                                <p className="text-[10px] text-[var(--color-content-muted)]">{profile.description}</p>
                                <div className="flex items-center gap-2 mt-1.5 text-[10px] text-[var(--color-content-muted)]">
                                  <span>{profile.default_snr_db} dB</span>
                                  <span>·</span>
                                  <span>+{profile.estimated_wer_increase}% WER</span>
                                </div>
                              </button>
                            );
                          })}
                        </div>

                        {/* SNR Slider */}
                        <div className="p-2.5 bg-[var(--color-surface-inset)]/50 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium text-[var(--color-content-secondary)] flex items-center gap-1">
                              <Gauge className="w-3.5 h-3.5" />
                              SNR Level
                            </span>
                            <span className="text-xs font-bold text-[var(--color-content-primary)]">
                              {getEffectiveSNR()} dB
                            </span>
                          </div>
                          <input
                            type="range"
                            min="-10"
                            max="50"
                            value={getEffectiveSNR()}
                            onChange={(e) => updateNoiseConfig({ snr_db: parseInt(e.target.value) })}
                            className="w-full h-1.5 bg-[var(--color-interactive-active)] rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3.5 [&::-webkit-slider-thumb]:h-3.5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gradient-to-r [&::-webkit-slider-thumb]:from-teal-400 [&::-webkit-slider-thumb]:to-cyan-500 [&::-webkit-slider-thumb]:cursor-pointer"
                          />
                          <div className="flex justify-between text-[9px] text-[var(--color-content-muted)] mt-1">
                            <span>Extreme (-10 dB)</span>
                            <span>Clean (50 dB)</span>
                          </div>
                        </div>

                        {/* Info */}
                        <div className="flex items-start gap-2 p-2 bg-[var(--color-status-info-bg)] rounded-lg">
                          <Info className="w-3.5 h-3.5 text-[var(--color-status-info)] mt-0.5 flex-shrink-0" />
                          <p className="text-[10px] text-[var(--color-status-info)]">
                            Noise will be applied to all audio during scenario execution. Lower SNR = more noise = harder for ASR.
                          </p>
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* STEP 2: Steps with Language Variants */}
          {currentStep === 'steps' && (
            <div className="space-y-4">
              <p className="text-sm text-[var(--color-content-secondary)]">
                Define conversation steps. Add multiple languages and use auto-translate.
              </p>

              {formData.steps.map((step, stepIndex) => (
                <div
                  key={stepIndex}
                  className="p-4 bg-[var(--color-surface-inset)]/50 rounded-xl border border-[var(--color-border-default)]"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#2A6B6E] to-[#11484D] flex items-center justify-center text-white text-xs font-bold">
                        {step.step_order}
                      </div>
                      <span className="font-medium text-[var(--color-content-primary)]">Step {step.step_order}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => openTranslateSelector(stepIndex)}
                        disabled={isTranslating !== null || getAvailableLanguages(stepIndex).length === 0}
                        className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-white bg-gradient-to-r from-[#2A6B6E] to-[#11484D] rounded-lg hover:opacity-90 disabled:opacity-50"
                      >
                        <Languages className="w-3.5 h-3.5" />
                        Auto-Translate
                      </button>
                      {formData.steps.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeStep(stepIndex)}
                          className="p-1.5 text-[var(--color-content-muted)] hover:text-[var(--color-status-danger)] hover:bg-[var(--color-status-danger-bg)] rounded-lg"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Auto-Translate Language Selector */}
                  {showTranslateSelector === stepIndex && (
                    <div className="mb-4 p-4 bg-gradient-to-br from-[var(--color-status-teal-bg)] to-[var(--color-status-teal-bg)] border-2 border-[#2A6B6E] rounded-lg">
                      <div className="flex justify-between items-center mb-3">
                        <h5 className="text-sm font-semibold text-[var(--color-content-primary)]">Select Languages to Translate</h5>
                        <button
                          type="button"
                          onClick={() => {
                            setShowTranslateSelector(null);
                            setSelectedTranslateLanguages([]);
                          }}
                          className="text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)]"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>

                      {/* Quick Select Buttons */}
                      <div className="flex gap-2 mb-3">
                        <button
                          type="button"
                          onClick={() => selectAllTranslateLanguages(stepIndex)}
                          className="px-3 py-1.5 text-xs font-medium text-[var(--color-brand-primary)] bg-[var(--color-surface-raised)] border border-[#2A6B6E] rounded-md hover:bg-[var(--color-status-teal-bg)]"
                        >
                          Select All
                        </button>
                        <button
                          type="button"
                          onClick={deselectAllTranslateLanguages}
                          className="px-3 py-1.5 text-xs font-medium text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] border border-[var(--color-border-strong)] rounded-md hover:bg-[var(--color-interactive-hover)]"
                        >
                          Deselect All
                        </button>
                        <span className="ml-auto text-xs text-[var(--color-content-secondary)] self-center">
                          {selectedTranslateLanguages.length} selected
                        </span>
                      </div>

                      {/* Language Checkboxes */}
                      <div className="grid grid-cols-2 gap-2 mb-4 max-h-48 overflow-y-auto">
                        {getAvailableLanguages(stepIndex).map((langCode) => {
                          const langInfo = getLanguageInfo(langCode);
                          const isSelected = selectedTranslateLanguages.includes(langCode);

                          return (
                            <label
                              key={langCode}
                              className={`flex items-center gap-2 p-2 rounded-md cursor-pointer transition-colors ${
                                isSelected
                                  ? 'bg-[var(--color-brand-muted)] border border-[#2A6B6E]'
                                  : 'bg-[var(--color-surface-raised)] border border-[var(--color-border-default)] hover:bg-[var(--color-interactive-hover)]'
                              }`}
                            >
                              <input
                                type="checkbox"
                                checked={isSelected}
                                onChange={() => toggleTranslateLanguage(langCode)}
                                className="w-4 h-4 text-[#2A6B6E] border-[var(--color-border-strong)] rounded focus:ring-[#2A6B6E]"
                              />
                              <span className="text-lg">{langInfo.flag}</span>
                              <span className="text-xs font-medium text-[var(--color-content-secondary)]">{langInfo.name}</span>
                            </label>
                          );
                        })}
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => performTranslation(stepIndex)}
                          disabled={isTranslating !== null || selectedTranslateLanguages.length === 0}
                          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-[#2A6B6E] to-[#11484D] rounded-md hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {isTranslating === stepIndex ? (
                            <>
                              <Loader2 className="w-4 h-4 animate-spin" />
                              Translating...
                            </>
                          ) : (
                            <>
                              <Languages className="w-4 h-4" />
                              Translate to {selectedTranslateLanguages.length} Language{selectedTranslateLanguages.length !== 1 ? 's' : ''}
                            </>
                          )}
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setShowTranslateSelector(null);
                            setSelectedTranslateLanguages([]);
                          }}
                          disabled={isTranslating !== null}
                          className="px-4 py-2 text-sm font-medium text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] border border-[var(--color-border-strong)] rounded-md hover:bg-[var(--color-interactive-hover)] disabled:opacity-50"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Language Variants */}
                  <div className="space-y-3">
                    {(step.step_metadata.language_variants || []).map((variant) => {
                      const langInfo = getLanguageInfo(variant.language_code);
                      const isPrimary = variant.language_code === step.step_metadata.primary_language;

                      return (
                        <div
                          key={variant.language_code}
                          className={`p-3 rounded-lg border ${
                            isPrimary
                              ? 'border-[var(--color-status-info-bg)] bg-[var(--color-status-info-bg)]'
                              : 'border-[var(--color-border-default)] bg-[var(--color-surface-raised)]'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="text-lg">{langInfo.flag}</span>
                              <span className="text-sm font-medium text-[var(--color-content-secondary)]">
                                {langInfo.name}
                              </span>
                              {isPrimary && (
                                <span className="px-1.5 py-0.5 text-[10px] font-bold bg-[var(--color-status-info)] text-white rounded">
                                  PRIMARY
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-1">
                              {!isPrimary && (
                                <button
                                  type="button"
                                  onClick={() => setPrimaryLanguage(stepIndex, variant.language_code)}
                                  className="px-2 py-1 text-[10px] font-medium text-[var(--color-status-info)] border border-[var(--color-status-info-bg)] rounded hover:bg-[var(--color-status-info-bg)]"
                                >
                                  Set Primary
                                </button>
                              )}
                              {!isPrimary && (
                                <button
                                  type="button"
                                  onClick={() => removeLanguageVariant(stepIndex, variant.language_code)}
                                  className="p-1 text-[var(--color-content-muted)] hover:text-[var(--color-status-danger)]"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              )}
                            </div>
                          </div>
                          <input
                            type="text"
                            value={variant.user_utterance}
                            onChange={(e) =>
                              updateLanguageVariant(stepIndex, variant.language_code, e.target.value)
                            }
                            placeholder={`User says in ${langInfo.name}...`}
                            className="w-full px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[#2A6B6E]/30 focus:border-[#2A6B6E]"
                          />
                        </div>
                      );
                    })}

                    {/* Add Language */}
                    <Select
                      className="select-sm w-full"
                      value=""
                      onChange={(e) => {
                        if (e.target.value) {
                          addLanguageVariant(stepIndex, e.target.value);
                        }
                      }}
                    >
                      <option value="">+ Add language...</option>
                      {SUPPORTED_LANGUAGES.filter(
                        (l) => !(step.step_metadata.language_variants || []).some((v) => v.language_code === l.code)
                      ).map((lang) => (
                        <option key={lang.code} value={lang.code}>
                          {lang.flag} {lang.name}
                        </option>
                      ))}
                    </Select>
                  </div>
                </div>
              ))}

              <button
                type="button"
                onClick={addStep}
                className="w-full py-3 border-2 border-dashed border-[var(--color-border-strong)] rounded-xl text-[var(--color-content-secondary)] hover:border-[#2A6B6E] hover:text-[#2A6B6E] flex items-center justify-center gap-2 font-medium"
              >
                <Plus className="w-4 h-4" />
                Add Step
              </button>
            </div>
          )}

          {/* STEP 3: Expected Outcomes (Optional) */}
          {currentStep === 'outcomes' && (
            <div className="space-y-4">
              <div className="p-4 bg-[var(--color-status-info-bg)] border border-[var(--color-status-info-bg)] rounded-xl">
                <h3 className="font-semibold text-[var(--color-status-info)] flex items-center gap-2 mb-1">
                  <Target className="w-4 h-4" />
                  Advanced Validation (Optional)
                </h3>
                <p className="text-sm text-[var(--color-status-info)]">
                  Configure expected outcomes for precise validation: CommandKind, confidence, patterns, entities.
                </p>
              </div>

              {/* Step Selector */}
              <div>
                <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1.5">
                  Configure outcomes for step:
                </label>
                <Select
                  value={selectedStepIndex}
                  onChange={(e) => setSelectedStepIndex(parseInt(e.target.value))}
                  className="w-full"
                >
                  {formData.steps.map((step, index) => {
                    const primaryVariant = step.step_metadata.language_variants?.find(
                      (v) => v.language_code === step.step_metadata.primary_language
                    );
                    return (
                      <option key={index} value={index}>
                        Step {step.step_order}: {primaryVariant?.user_utterance || '(No utterance)'}
                      </option>
                    );
                  })}
                </Select>
              </div>

              {/* Outcomes for Selected Step */}
              <div className="space-y-3">
                {formData.steps[selectedStepIndex]?.expected_outcomes.map((outcome, outcomeIndex) => {
                  const key = `${selectedStepIndex}-${outcomeIndex}`;
                  const isExpanded = expandedOutcomes.has(key);
                  const showAdvanced = showAdvancedOutcome.has(key);

                  return (
                    <div
                      key={outcomeIndex}
                      className="border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)]"
                    >
                      <div
                        className="flex items-center justify-between p-3 bg-[var(--color-status-emerald-bg)] cursor-pointer"
                        onClick={() => toggleOutcomeExpanded(key)}
                      >
                        <div className="flex items-center gap-2">
                          <Target className="w-4 h-4 text-[var(--color-status-emerald)]" />
                          <span className="font-medium text-[var(--color-content-primary)]">{outcome.name}</span>
                          <span className="text-xs text-[var(--color-content-muted)]">({outcome.outcome_code})</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              removeOutcome(selectedStepIndex, outcomeIndex);
                            }}
                            className="p-1 text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)]"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                          {isExpanded ? <ChevronUp className="w-4 h-4 text-[var(--color-content-muted)]" /> : <ChevronDown className="w-4 h-4 text-[var(--color-content-muted)]" />}
                        </div>
                      </div>

                      {isExpanded && (
                        <div className="p-4 space-y-4">
                          {/* Basic fields */}
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">Outcome Code</label>
                              <input
                                type="text"
                                value={outcome.outcome_code}
                                onChange={(e) => updateOutcome(selectedStepIndex, outcomeIndex, { outcome_code: e.target.value })}
                                className="w-full px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)]"
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">Name</label>
                              <input
                                type="text"
                                value={outcome.name}
                                onChange={(e) => updateOutcome(selectedStepIndex, outcomeIndex, { name: e.target.value })}
                                className="w-full px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)]"
                              />
                            </div>
                          </div>

                          <div>
                            <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">Description</label>
                            <textarea
                              value={outcome.description || ''}
                              onChange={(e) => updateOutcome(selectedStepIndex, outcomeIndex, { description: e.target.value })}
                              rows={2}
                              placeholder="Describe what this outcome validates..."
                              className="w-full px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)]"
                            />
                          </div>

                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">Expected Command Kind</label>
                              <Select
                                value={outcome.expected_command_kind || ''}
                                onChange={(e) => updateOutcome(selectedStepIndex, outcomeIndex, { expected_command_kind: e.target.value })}
                                className="select-sm w-full"
                              >
                                <option value="">Select...</option>
                                {COMMAND_KINDS.map((kind) => (
                                  <option key={kind} value={kind}>{kind}</option>
                                ))}
                              </Select>
                            </div>
                            <div>
                              <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">Min ASR Confidence (0-1)</label>
                              <input
                                type="number"
                                min="0"
                                max="1"
                                step="0.1"
                                value={outcome.expected_asr_confidence_min || 0.7}
                                onChange={(e) => updateOutcome(selectedStepIndex, outcomeIndex, { expected_asr_confidence_min: parseFloat(e.target.value) })}
                                className="w-full px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)]"
                              />
                            </div>
                          </div>

                          {/* Response Content Validation - Mode Toggle */}
                          <div className="border-t border-[var(--color-border-default)] pt-4 mt-4">
                            <div className="flex items-center justify-between mb-3">
                              <div>
                                <h5 className="text-xs font-semibold text-[var(--color-content-primary)]">
                                  Response Content Validation
                                </h5>
                                <p className="text-[10px] text-[var(--color-content-muted)]">
                                  Define patterns the AI response must match or avoid
                                </p>
                              </div>
                              <button
                                type="button"
                                onClick={() => toggleRawJsonMode(key)}
                                className="flex items-center gap-1.5 px-2 py-1 text-[10px] text-[var(--color-content-secondary)] bg-[var(--color-surface-inset)] rounded hover:bg-[var(--color-interactive-active)]"
                                title={rawJsonMode.has(key) ? 'Switch to structured form' : 'Switch to raw JSON'}
                              >
                                {rawJsonMode.has(key) ? (
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

                            {rawJsonMode.has(key) ? (
                              /* Raw JSON Mode */
                              <div>
                                <textarea
                                  value={formatResponseContentJson(outcome.expected_response_content)}
                                  onChange={(e) => updateOutcome(selectedStepIndex, outcomeIndex, {
                                    expected_response_content: parseResponseContentJson(e.target.value),
                                  })}
                                  rows={6}
                                  className="w-full px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] font-mono"
                                  placeholder='{"contains": ["sunny"], "not_contains": ["error"]}'
                                />
                              </div>
                            ) : (
                              /* Structured Mode - Interactive Lists */
                              <div className="space-y-4">
                                {/* Must Contain */}
                                <div>
                                  <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">Must Contain</label>
                                  <p className="text-[10px] text-[var(--color-content-muted)] mb-2">AI response MUST include these phrases (case-insensitive)</p>
                                  {(outcome.expected_response_content?.contains || []).length > 0 && (
                                    <div className="space-y-1 mb-2">
                                      {(outcome.expected_response_content?.contains || []).map((item, idx) => (
                                        <div key={idx} className="flex items-center gap-2 p-2 bg-[var(--color-surface-inset)]/50 rounded border border-[var(--color-border-default)] text-sm">
                                          <span className="text-[var(--color-content-secondary)]">{item}</span>
                                          <button type="button" onClick={() => removePattern(selectedStepIndex, outcomeIndex, 'contains', idx)} className="ml-auto text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)]">
                                            <Trash2 className="w-3 h-3" />
                                          </button>
                                        </div>
                                      ))}
                                    </div>
                                  )}
                                  <div className="flex gap-2">
                                    <input
                                      type="text"
                                      value={getPatternInput(key, 'contains')}
                                      onChange={(e) => setPatternInput(key, 'contains', e.target.value)}
                                      onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                          e.preventDefault();
                                          addPattern(selectedStepIndex, outcomeIndex, 'contains', getPatternInput(key, 'contains'));
                                        }
                                      }}
                                      className="flex-1 px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)]"
                                      placeholder="e.g., sunny, temperature"
                                    />
                                    <button
                                      type="button"
                                      onClick={() => addPattern(selectedStepIndex, outcomeIndex, 'contains', getPatternInput(key, 'contains'))}
                                      className="px-3 py-2 bg-[var(--color-interactive-active)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-active)] text-sm"
                                    >
                                      Add
                                    </button>
                                  </div>
                                </div>

                                {/* Must NOT Contain */}
                                <div>
                                  <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">Must NOT Contain</label>
                                  <p className="text-[10px] text-[var(--color-content-muted)] mb-2">AI response must NOT include these phrases (case-insensitive)</p>
                                  {(outcome.expected_response_content?.not_contains || []).length > 0 && (
                                    <div className="space-y-1 mb-2">
                                      {(outcome.expected_response_content?.not_contains || []).map((item, idx) => (
                                        <div key={idx} className="flex items-center gap-2 p-2 bg-[var(--color-surface-inset)]/50 rounded border border-[var(--color-border-default)] text-sm">
                                          <span className="text-[var(--color-content-secondary)]">{item}</span>
                                          <button type="button" onClick={() => removePattern(selectedStepIndex, outcomeIndex, 'not_contains', idx)} className="ml-auto text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)]">
                                            <Trash2 className="w-3 h-3" />
                                          </button>
                                        </div>
                                      ))}
                                    </div>
                                  )}
                                  <div className="flex gap-2">
                                    <input
                                      type="text"
                                      value={getPatternInput(key, 'not_contains')}
                                      onChange={(e) => setPatternInput(key, 'not_contains', e.target.value)}
                                      onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                          e.preventDefault();
                                          addPattern(selectedStepIndex, outcomeIndex, 'not_contains', getPatternInput(key, 'not_contains'));
                                        }
                                      }}
                                      className="flex-1 px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)]"
                                      placeholder="e.g., error, sorry, unknown"
                                    />
                                    <button
                                      type="button"
                                      onClick={() => addPattern(selectedStepIndex, outcomeIndex, 'not_contains', getPatternInput(key, 'not_contains'))}
                                      className="px-3 py-2 bg-[var(--color-interactive-active)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-active)] text-sm"
                                    >
                                      Add
                                    </button>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>

                          {/* Advanced Toggle */}
                          <button
                            type="button"
                            onClick={() => toggleAdvancedOutcome(key)}
                            className="flex items-center gap-2 text-xs font-medium text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)]"
                          >
                            <Code className="w-3.5 h-3.5" />
                            {showAdvanced ? 'Hide Advanced Options' : 'Show Advanced Options'}
                            {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                          </button>

                          {showAdvanced && (
                            <div className="space-y-4 pt-3 border-t border-[var(--color-border-default)]">
                              {/* Regex Patterns - Interactive */}
                              <div>
                                <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">Must Match Regex</label>
                                <p className="text-[10px] text-[var(--color-content-muted)] mb-2">AI response must match these regex patterns</p>
                                {(outcome.expected_response_content?.regex || []).length > 0 && (
                                  <div className="space-y-1 mb-2">
                                    {(outcome.expected_response_content?.regex || []).map((item, idx) => (
                                      <div key={idx} className="flex items-center gap-2 p-2 bg-[var(--color-surface-inset)]/50 rounded border border-[var(--color-border-default)] text-sm">
                                        <span className="font-mono text-[var(--color-status-purple)]">{item}</span>
                                        <button type="button" onClick={() => removePattern(selectedStepIndex, outcomeIndex, 'regex', idx)} className="ml-auto text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)]">
                                          <Trash2 className="w-3 h-3" />
                                        </button>
                                      </div>
                                    ))}
                                  </div>
                                )}
                                <div className="flex gap-2">
                                  <input
                                    type="text"
                                    value={getPatternInput(key, 'regex')}
                                    onChange={(e) => setPatternInput(key, 'regex', e.target.value)}
                                    onKeyDown={(e) => {
                                      if (e.key === 'Enter') {
                                        e.preventDefault();
                                        addPattern(selectedStepIndex, outcomeIndex, 'regex', getPatternInput(key, 'regex'));
                                      }
                                    }}
                                    className="flex-1 px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] font-mono"
                                    placeholder="e.g., \\d+ degrees"
                                  />
                                  <button
                                    type="button"
                                    onClick={() => addPattern(selectedStepIndex, outcomeIndex, 'regex', getPatternInput(key, 'regex'))}
                                    className="px-3 py-2 bg-[var(--color-interactive-active)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-active)] text-sm"
                                  >
                                    Add
                                  </button>
                                </div>
                              </div>

                              <div>
                                <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">Must NOT Match Regex</label>
                                <p className="text-[10px] text-[var(--color-content-muted)] mb-2">AI response must NOT match these regex patterns</p>
                                {(outcome.expected_response_content?.regex_not_match || []).length > 0 && (
                                  <div className="space-y-1 mb-2">
                                    {(outcome.expected_response_content?.regex_not_match || []).map((item, idx) => (
                                      <div key={idx} className="flex items-center gap-2 p-2 bg-[var(--color-surface-inset)]/50 rounded border border-[var(--color-border-default)] text-sm">
                                        <span className="font-mono text-[var(--color-status-purple)]">{item}</span>
                                        <button type="button" onClick={() => removePattern(selectedStepIndex, outcomeIndex, 'regex_not_match', idx)} className="ml-auto text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)]">
                                          <Trash2 className="w-3 h-3" />
                                        </button>
                                      </div>
                                    ))}
                                  </div>
                                )}
                                <div className="flex gap-2">
                                  <input
                                    type="text"
                                    value={getPatternInput(key, 'regex_not_match')}
                                    onChange={(e) => setPatternInput(key, 'regex_not_match', e.target.value)}
                                    onKeyDown={(e) => {
                                      if (e.key === 'Enter') {
                                        e.preventDefault();
                                        addPattern(selectedStepIndex, outcomeIndex, 'regex_not_match', getPatternInput(key, 'regex_not_match'));
                                      }
                                    }}
                                    className="flex-1 px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] font-mono"
                                    placeholder="e.g., error.*occurred"
                                  />
                                  <button
                                    type="button"
                                    onClick={() => addPattern(selectedStepIndex, outcomeIndex, 'regex_not_match', getPatternInput(key, 'regex_not_match'))}
                                    className="px-3 py-2 bg-[var(--color-interactive-active)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-active)] text-sm"
                                  >
                                    Add
                                  </button>
                                </div>
                              </div>

                              {/* Native Data Schema */}
                              <div>
                                <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">Expected Native Data Schema (JSON)</label>
                                <textarea
                                  value={formatJson(outcome.expected_native_data_schema)}
                                  onChange={(e) => updateOutcome(selectedStepIndex, outcomeIndex, { expected_native_data_schema: parseJson(e.target.value) })}
                                  rows={3}
                                  placeholder='{"required_fields": ["Artist"], "field_types": {"Artist": "string"}}'
                                  className="w-full px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] font-mono"
                                />
                              </div>

                              {/* Conversation Requirements */}
                              <div>
                                <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">Conversation Requirements (JSON)</label>
                                <textarea
                                  value={formatJson(outcome.conversation_requirements)}
                                  onChange={(e) => updateOutcome(selectedStepIndex, outcomeIndex, { conversation_requirements: parseJson(e.target.value) })}
                                  rows={3}
                                  placeholder='{"requires_context": true, "context_vars": ["location"]}'
                                  className="w-full px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] font-mono"
                                />
                              </div>

                              {/* Entities */}
                              <div>
                                <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">Expected Entities</label>
                                {outcome.entities && Object.keys(outcome.entities).length > 0 && (
                                  <div className="space-y-1 mb-2">
                                    {Object.entries(outcome.entities).map(([k, v]) => (
                                      <div key={k} className="flex items-center gap-2 p-2 bg-[var(--color-surface-inset)]/50 rounded border border-[var(--color-border-default)] text-sm">
                                        <span className="font-medium text-[var(--color-content-secondary)]">{k}:</span>
                                        <span className="text-[var(--color-content-secondary)]">{v}</span>
                                        <button type="button" onClick={() => removeEntity(selectedStepIndex, outcomeIndex, k)} className="ml-auto text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)]">
                                          <Trash2 className="w-3 h-3" />
                                        </button>
                                      </div>
                                    ))}
                                  </div>
                                )}
                                <div className="flex gap-2">
                                  <input
                                    type="text"
                                    value={entityInputs[key]?.key || ''}
                                    onChange={(e) => setEntityInputs({ ...entityInputs, [key]: { ...entityInputs[key], key: e.target.value } })}
                                    placeholder="Entity name"
                                    className="flex-1 px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)]"
                                  />
                                  <input
                                    type="text"
                                    value={entityInputs[key]?.value || ''}
                                    onChange={(e) => setEntityInputs({ ...entityInputs, [key]: { ...entityInputs[key], value: e.target.value } })}
                                    placeholder="Expected value"
                                    className="flex-1 px-3 py-2 text-sm border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)]"
                                  />
                                  <button
                                    type="button"
                                    onClick={() => addEntity(key, selectedStepIndex, outcomeIndex)}
                                    className="px-3 py-2 bg-[var(--color-interactive-active)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-active)] text-sm"
                                  >
                                    Add
                                  </button>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}

                <button
                  type="button"
                  onClick={() => addOutcome(selectedStepIndex)}
                  className="w-full py-2.5 border-2 border-dashed border-[var(--color-border-strong)] rounded-xl text-[var(--color-content-secondary)] hover:border-[var(--color-status-emerald)] hover:text-[var(--color-status-emerald)] flex items-center justify-center gap-2 text-sm font-medium"
                >
                  <Plus className="w-4 h-4" />
                  Add Expected Outcome
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: Review */}
          {currentStep === 'review' && (
            <div className="space-y-5">
              <div className="p-4 bg-[var(--color-status-emerald-bg)] border border-[var(--color-status-emerald-bg)] rounded-xl">
                <h3 className="font-semibold text-[var(--color-status-emerald)] flex items-center gap-2 mb-1">
                  <Sparkles className="w-4 h-4" />
                  Ready to Create
                </h3>
                <p className="text-sm text-[var(--color-status-emerald)]">
                  Review your scenario details below, then click "Create Scenario" to finish.
                </p>
              </div>

              <div className="space-y-4">
                <div className="p-4 bg-[var(--color-surface-inset)]/50 rounded-xl border border-[var(--color-border-default)]">
                  <h4 className="text-sm font-medium text-[var(--color-content-muted)] mb-2">Scenario Details</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-[var(--color-content-secondary)]">Name</span>
                      <span className="font-medium text-[var(--color-content-primary)]">{formData.name}</span>
                    </div>
                    {formData.description && (
                      <div className="flex justify-between">
                        <span className="text-[var(--color-content-secondary)]">Description</span>
                        <span className="text-[var(--color-content-primary)] text-right max-w-[60%] truncate">{formData.description}</span>
                      </div>
                    )}
                    {formData.script_metadata.category && (
                      <div className="flex justify-between">
                        <span className="text-[var(--color-content-secondary)]">Category</span>
                        <span className="font-medium text-[var(--color-content-primary)]">{formData.script_metadata.category}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-[var(--color-content-secondary)]">Validation</span>
                      <span className="font-medium text-[var(--color-content-primary)]">
                        {VALIDATION_MODES.find((m) => m.value === formData.validation_mode)?.label}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[var(--color-content-secondary)]">Audio Environment</span>
                      <span className="font-medium text-[var(--color-content-primary)]">
                        {formData.script_metadata.noise_config?.enabled ? (
                          <span className="flex items-center gap-1.5">
                            <Volume2 className="w-3.5 h-3.5 text-[var(--color-status-teal)]" />
                            {getSelectedProfile()?.name.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')} ({getEffectiveSNR()} dB)
                          </span>
                        ) : (
                          <span className="text-[var(--color-content-muted)]">Disabled</span>
                        )}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-[var(--color-surface-inset)]/50 rounded-xl border border-[var(--color-border-default)]">
                  <h4 className="text-sm font-medium text-[var(--color-content-muted)] mb-3">
                    Conversation Steps ({formData.steps.length})
                  </h4>
                  <div className="space-y-3">
                    {formData.steps.map((step, index) => {
                      const primaryVariant = step.step_metadata.language_variants?.find(
                        (v) => v.language_code === step.step_metadata.primary_language
                      );
                      const langCount = step.step_metadata.language_variants.length;
                      const outcomeCount = step.expected_outcomes.length;

                      return (
                        <div key={index} className="flex items-start gap-2 text-sm">
                          <span className="flex-shrink-0 w-5 h-5 rounded-full bg-[#2A6B6E]/20 text-[var(--color-brand-primary)] text-xs flex items-center justify-center font-medium">
                            {step.step_order}
                          </span>
                          <div className="flex-1">
                            <div className="text-[var(--color-content-primary)]">"{primaryVariant?.user_utterance}"</div>
                            <div className="flex items-center gap-2 mt-1 text-xs text-[var(--color-content-muted)]">
                              <span className="flex items-center gap-1">
                                <Globe className="w-3 h-3" />
                                {langCount} language{langCount !== 1 ? 's' : ''}
                              </span>
                              {outcomeCount > 0 && (
                                <span className="flex items-center gap-1">
                                  <Target className="w-3 h-3" />
                                  {outcomeCount} outcome{outcomeCount !== 1 ? 's' : ''}
                                </span>
                              )}
                              {step.follow_up_action && (
                                <span className="text-[var(--color-content-muted)]">| {step.follow_up_action}</span>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex-shrink-0 px-6 py-4 border-t border-[var(--color-border-default)] bg-[var(--color-surface-inset)]/50 flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={handleBack}
            disabled={currentStep === 'details' || isSubmitting}
            className="flex items-center gap-2 px-4 py-2.5 text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-active)] rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4" />
            Back
          </button>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2.5 text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-active)] rounded-xl font-medium disabled:opacity-50"
            >
              Cancel
            </button>

            {currentStep !== 'review' ? (
              <button
                type="button"
                onClick={handleNext}
                className="flex items-center gap-2 px-5 py-2.5 text-white rounded-xl font-medium hover:shadow-lg hover:-translate-y-0.5 transition-all"
                style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
              >
                {currentStep === 'outcomes' ? 'Review' : 'Continue'}
                <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="flex items-center gap-2 px-5 py-2.5 text-white rounded-xl font-medium hover:shadow-lg hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Check className="w-4 h-4" />
                    Create Scenario
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateScenarioModal;
