/**
 * Scenario Form Component
 *
 * Reusable form component for scenario metadata including:
 * - Name, description, version
 * - Category and tags
 * - Active status
 * - Noise configuration with visual profile cards
 * - Form validation and error handling
 */

import React, { useState, useRef, useEffect } from 'react';
import { AlertCircle } from 'lucide-react';
import categoryService, { type Category } from '../../services/category.service';
import type { NoiseConfig } from '../../types/multiTurn';
import { NoiseConfigPanel } from '../../components/Audio';

export interface ScenarioFormData {
  name: string;
  description: string;
  version: string;
  is_active: boolean;
  validation_mode: 'houndify' | 'llm_ensemble' | 'hybrid';
  script_metadata: {
    category?: string;
    tags?: string[];
    [key: string]: any;
  };
  noise_config?: NoiseConfig;
}

interface ScenarioFormProps {
  initialData?: Partial<ScenarioFormData>;
  onSubmit: (data: ScenarioFormData) => void;
  onCancel?: () => void;
  isLoading?: boolean;
}

export const ScenarioForm: React.FC<ScenarioFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState<ScenarioFormData>({
    name: initialData?.name || '',
    description: initialData?.description || '',
    version: initialData?.version || '1.0.0',
    is_active: initialData?.is_active ?? true,
    validation_mode: initialData?.validation_mode || 'hybrid',
    script_metadata: {
      category: initialData?.script_metadata?.category || '',
      tags: initialData?.script_metadata?.tags || [],
      ...initialData?.script_metadata,
    },
    noise_config: initialData?.noise_config || {
      enabled: false,
      profile: 'car_cabin_city',
      snr_db: undefined,
      randomize_snr: false,
      snr_variance: 3.0,
    },
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [tagInput, setTagInput] = useState('');
  const [categories, setCategories] = useState<Category[]>([]);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const isInitialMount = useRef(true);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Scenario name is required';
    } else if (formData.name.length < 3) {
      newErrors.name = 'Scenario name must be at least 3 characters';
    }

    if (!formData.version.trim()) {
      newErrors.version = 'Version is required';
    } else if (!/^\d+\.\d+\.\d+$/.test(formData.version)) {
      newErrors.version = 'Version must be in format X.Y.Z (e.g., 1.0.0)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  // Fetch categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoadingCategories(true);
        const response = await categoryService.getCategories({ is_active: true });
        setCategories(response.categories);
      } catch (error) {
        console.error('Failed to fetch categories:', error);
        setCategories([]);
      } finally {
        setLoadingCategories(false);
      }
    };

    fetchCategories();
  }, []);

  // Update parent component whenever form data changes (skip initial render)
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    onSubmit(formData);
  }, [formData, onSubmit]);

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.script_metadata.tags?.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        script_metadata: {
          ...formData.script_metadata,
          tags: [...(formData.script_metadata.tags || []), tagInput.trim()],
        },
      });
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData({
      ...formData,
      script_metadata: {
        ...formData.script_metadata,
        tags: formData.script_metadata.tags?.filter((tag) => tag !== tagToRemove) || [],
      },
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  // Handle noise config changes
  const handleNoiseConfigChange = (newConfig: NoiseConfig) => {
    setFormData({
      ...formData,
      noise_config: newConfig,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Name Field */}
      <div>
        <label
          htmlFor="name"
          className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1"
        >
          Scenario Name <span className="text-[var(--color-status-danger)]">*</span>
        </label>
        <input
          type="text"
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className={`w-full px-3 py-2 border rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-border-focus)] ${
            errors.name ? 'border-[var(--color-status-danger)]' : 'border-[var(--color-border-strong)]'
          }`}
          placeholder="e.g., Restaurant Reservation Flow"
          disabled={isLoading}
        />
        {errors.name && (
          <div className="mt-1 flex items-center text-sm text-[var(--color-status-danger)]">
            <AlertCircle className="w-4 h-4 mr-1" />
            {errors.name}
          </div>
        )}
      </div>

      {/* Description Field */}
      <div>
        <label
          htmlFor="description"
          className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1"
        >
          Description
        </label>
        <textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          rows={3}
          className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-border-focus)]"
          placeholder="Describe what this scenario tests..."
          disabled={isLoading}
        />
      </div>

      {/* Version and Category Row */}
      <div className="grid grid-cols-2 gap-4">
        {/* Version Field */}
        <div>
          <label
            htmlFor="version"
            className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1"
          >
            Version <span className="text-[var(--color-status-danger)]">*</span>
          </label>
          <input
            type="text"
            id="version"
            value={formData.version}
            onChange={(e) => setFormData({ ...formData, version: e.target.value })}
            className={`w-full px-3 py-2 border rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-border-focus)] ${
              errors.version ? 'border-[var(--color-status-danger)]' : 'border-[var(--color-border-strong)]'
            }`}
            placeholder="1.0.0"
            disabled={isLoading}
          />
          {errors.version && (
            <div className="mt-1 flex items-center text-sm text-[var(--color-status-danger)]">
              <AlertCircle className="w-4 h-4 mr-1" />
              {errors.version}
            </div>
          )}
        </div>

        {/* Category Field */}
        <div>
          <label
            htmlFor="category"
            className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1"
          >
            Category
          </label>
          <select
            id="category"
            value={formData.script_metadata.category || ''}
            onChange={(e) =>
              setFormData({
                ...formData,
                script_metadata: { ...formData.script_metadata, category: e.target.value },
              })
            }
            className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-border-focus)]"
            disabled={isLoading || loadingCategories}
          >
            <option value="">{loadingCategories ? 'Loading categories...' : 'Select category...'}</option>
            {categories.map((category) => (
              <option key={category.id} value={category.name}>
                {category.display_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Validation Mode Field */}
      <div>
        <label
          htmlFor="validation_mode"
          className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1"
        >
          Validation Mode
        </label>
        <select
          id="validation_mode"
          value={formData.validation_mode}
          onChange={(e) =>
            setFormData({
              ...formData,
              validation_mode: e.target.value as 'houndify' | 'llm_ensemble' | 'hybrid',
            })
          }
          className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-border-focus)]"
          disabled={isLoading}
        >
          <option value="hybrid">Hybrid (Houndify + LLM) - Recommended</option>
          <option value="houndify">Houndify Only (ASR/NLU-based validation)</option>
          <option value="llm_ensemble">LLM Ensemble Only (3-judge AI evaluation)</option>
        </select>
        <p className="mt-1 text-sm text-[var(--color-content-muted)]">
          {formData.validation_mode === 'houndify' &&
            'Uses Houndify ASR and NLU for CommandKind-based validation'}
          {formData.validation_mode === 'llm_ensemble' &&
            'Uses 3 LLM judges (GPT-4o, Claude, Gemini) for response evaluation'}
          {formData.validation_mode === 'hybrid' &&
            'Combines Houndify validation with LLM ensemble evaluation'}
        </p>
      </div>

      {/* Audio Settings Section - Noise Configuration */}
      {formData.noise_config && (
        <NoiseConfigPanel
          config={formData.noise_config}
          onChange={handleNoiseConfigChange}
          disabled={isLoading}
          defaultExpanded={initialData?.noise_config?.enabled}
        />
      )}

      {/* Tags Field */}
      <div>
        <label
          htmlFor="tags"
          className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1"
        >
          Tags
        </label>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            id="tags"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1 px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-border-focus)]"
            placeholder="Add a tag and press Enter..."
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={handleAddTag}
            className="px-4 py-2 bg-[var(--color-interactive-active)] text-[var(--color-content-secondary)] rounded-md hover:bg-[var(--color-interactive-active)] disabled:opacity-50"
            disabled={isLoading || !tagInput.trim()}
          >
            Add
          </button>
        </div>
        {formData.script_metadata.tags && formData.script_metadata.tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {formData.script_metadata.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-3 py-1 bg-[var(--color-status-info-bg)] text-[var(--color-status-info)] rounded-full text-sm"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="ml-2 text-[var(--color-status-info)] hover:text-[var(--color-status-info)]"
                  disabled={isLoading}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Active Status */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="is_active"
          checked={formData.is_active}
          onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
          className="w-4 h-4 text-[var(--color-status-info)] border-[var(--color-border-strong)] rounded focus:ring-[var(--color-status-info)]"
          disabled={isLoading}
        />
        <label htmlFor="is_active" className="ml-2 text-sm font-medium text-[var(--color-content-secondary)]">
          Active (scenario can be executed)
        </label>
      </div>

      {/* Form Actions */}
    </form>
  );
};

export default ScenarioForm;
