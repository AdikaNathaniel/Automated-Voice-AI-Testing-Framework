/**
 * Categories Management Page
 *
 * Admin page for managing scenario categories including
 * create, edit, delete, and viewing scenario counts.
 */

import React, { useEffect, useState, useCallback, useRef } from 'react';
import ReactDOM from 'react-dom';
import {
  Tag,
  Plus,
  Search,
  Edit2,
  Trash2,
  MoreVertical,
  X,
  Check,
  AlertCircle,
} from 'lucide-react';
import categoryService from '../../services/category.service';
import type { Category, CategoryCreate, CategoryUpdate } from '../../services/category.service';

interface FormData {
  name: string;
  display_name: string;
  description: string;
  color: string;
  icon: string;
  is_active: boolean;
}

const DEFAULT_FORM_DATA: FormData = {
  name: '',
  display_name: '',
  description: '',
  color: '#6B7280',
  icon: '',
  is_active: true,
};

const CategoriesPage: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [formData, setFormData] = useState<FormData>(DEFAULT_FORM_DATA);
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Delete confirmation state
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingCategory, setDeletingCategory] = useState<Category | null>(null);
  const [deleteForce, setDeleteForce] = useState(false);

  // Action menu state
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [dropdownPosition, setDropdownPosition] = useState<{ top: number; right: number } | null>(null);
  const buttonRefsMap = useRef<Map<string, HTMLButtonElement>>(new Map());

  const loadCategories = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await categoryService.getCategories({});
      setCategories(response.categories);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load categories');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  // Calculate dropdown position when menu opens
  useEffect(() => {
    if (openMenu) {
      const buttonEl = buttonRefsMap.current.get(openMenu);
      if (buttonEl) {
        const rect = buttonEl.getBoundingClientRect();
        setDropdownPosition({
          top: rect.bottom + 4,
          right: window.innerWidth - rect.right,
        });
      }
    } else {
      setDropdownPosition(null);
    }
  }, [openMenu]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (openMenu && !target.closest('.category-dropdown-menu') && !target.closest('button')) {
        setOpenMenu(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [openMenu]);

  const filteredCategories = categories.filter((cat) =>
    cat.name.toLowerCase().includes(search.toLowerCase()) ||
    cat.display_name.toLowerCase().includes(search.toLowerCase())
  );

  const handleCreate = () => {
    setEditingCategory(null);
    setFormData(DEFAULT_FORM_DATA);
    setFormError(null);
    setShowModal(true);
  };

  const handleEdit = (category: Category) => {
    setEditingCategory(category);
    setFormData({
      name: category.name,
      display_name: category.display_name,
      description: category.description || '',
      color: category.color || '#6B7280',
      icon: category.icon || '',
      is_active: category.is_active,
    });
    setFormError(null);
    setShowModal(true);
    setOpenMenu(null);
  };

  const handleDelete = (category: Category) => {
    setDeletingCategory(category);
    setDeleteForce(false);
    setShowDeleteConfirm(true);
    setOpenMenu(null);
  };

  const confirmDelete = async () => {
    if (!deletingCategory) return;

    try {
      await categoryService.deleteCategory(deletingCategory.id, deleteForce);
      await loadCategories();
      setShowDeleteConfirm(false);
      setDeletingCategory(null);
    } catch (err) {
      if (err instanceof Error && err.message.includes('associated scenario')) {
        // Show force option
        setFormError(err.message);
      } else {
        setError(err instanceof Error ? err.message : 'Failed to delete category');
        setShowDeleteConfirm(false);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    try {
      setSaving(true);

      if (editingCategory) {
        // Update existing category
        const updateData: CategoryUpdate = {};
        if (formData.name !== editingCategory.name) updateData.name = formData.name;
        if (formData.display_name !== editingCategory.display_name) updateData.display_name = formData.display_name;
        if (formData.description !== editingCategory.description) updateData.description = formData.description;
        if (formData.color !== editingCategory.color) updateData.color = formData.color;
        if (formData.icon !== editingCategory.icon) updateData.icon = formData.icon;
        if (formData.is_active !== editingCategory.is_active) updateData.is_active = formData.is_active;

        await categoryService.updateCategory(editingCategory.id, updateData);
      } else {
        // Create new category
        const createData: CategoryCreate = {
          name: formData.name,
          display_name: formData.display_name || formData.name,
          description: formData.description,
          color: formData.color,
          icon: formData.icon,
          is_active: formData.is_active,
        };

        await categoryService.createCategory(createData);
      }

      await loadCategories();
      setShowModal(false);
      setFormData(DEFAULT_FORM_DATA);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Failed to save category');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
              <Tag className="w-6 h-6" style={{ color: '#9333EA' }} />
              Categories
            </h1>
            <p className="mt-2 text-sm text-[var(--color-content-secondary)]">
              Manage scenario categories and organization
            </p>
          </div>
          <button
            onClick={handleCreate}
            className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--color-status-purple)] text-white rounded-lg hover:opacity-90 transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Category
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--color-content-muted)]" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search categories..."
            className="w-full pl-10 pr-4 py-2 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-purple)]/10 focus:border-[var(--color-status-purple)]"
          />
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 p-4 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg">
          <div className="flex items-center gap-2 text-[var(--color-status-danger)]">
            <AlertCircle className="w-5 h-5" />
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Categories Table */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm border border-[var(--color-border-default)] overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-[var(--color-content-muted)]">
            Loading categories...
          </div>
        ) : filteredCategories.length === 0 ? (
          <div className="p-12 text-center text-[var(--color-content-muted)]">
            {search ? 'No categories found matching your search.' : 'No categories yet. Create one to get started.'}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[var(--color-surface-inset)]/50 border-b border-[var(--color-border-default)]">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
                    Scenarios
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border-subtle)]">
                {filteredCategories.map((category) => (
                  <tr key={category.id} className="hover:bg-[var(--color-interactive-hover)]/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-4 h-4 rounded"
                          style={{ backgroundColor: category.color || '#6B7280' }}
                        />
                        <div>
                          <div className="font-medium text-[var(--color-content-primary)]">
                            {category.display_name}
                          </div>
                          <div className="text-sm text-[var(--color-content-muted)]">
                            {category.name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-[var(--color-content-muted)]">
                      {category.description || '—'}
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-[var(--color-status-info-bg)] text-[var(--color-status-info)]">
                        {category.scenario_count}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          category.is_active
                            ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]'
                            : 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]'
                        }`}
                      >
                        {category.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {category.is_system && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-[var(--color-status-purple-bg)] text-[var(--color-status-purple)]">
                          System
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="relative">
                        <button
                          ref={(el) => {
                            if (el) {
                              buttonRefsMap.current.set(category.id, el);
                            }
                          }}
                          onClick={() => setOpenMenu(openMenu === category.id ? null : category.id)}
                          className="p-2 hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
                        >
                          <MoreVertical className="w-4 h-4 text-[var(--color-content-muted)]" />
                        </button>

                        {openMenu === category.id && dropdownPosition && ReactDOM.createPortal(
                          <div
                            className="category-dropdown-menu fixed w-48 bg-[var(--color-surface-raised)] rounded-xl shadow-lg border border-[var(--color-border-default)] py-1 z-50"
                            style={{
                              top: `${dropdownPosition.top}px`,
                              right: `${dropdownPosition.right}px`,
                            }}
                          >
                            <button
                              onClick={() => handleEdit(category)}
                              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]"
                              disabled={category.is_system}
                            >
                              <Edit2 className="w-4 h-4" />
                              Edit
                            </button>
                            <button
                              onClick={() => handleDelete(category)}
                              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-status-danger)] hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 disabled:cursor-not-allowed"
                              disabled={category.is_system}
                            >
                              <Trash2 className="w-4 h-4" />
                              Delete
                            </button>
                          </div>,
                          document.body
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-[var(--color-border-default)]">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-[var(--color-content-primary)]">
                  {editingCategory ? 'Edit Category' : 'New Category'}
                </h2>
                <button
                  onClick={() => setShowModal(false)}
                  className="p-2 hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {formError && (
                <div className="p-3 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg text-sm text-[var(--color-status-danger)]">
                  {formError}
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                    Name (lowercase, no spaces) *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value.toLowerCase().replace(/\s+/g, '_') })}
                    className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-purple)]/10 focus:border-[var(--color-status-purple)]"
                    required
                    disabled={editingCategory?.is_system}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                    Display Name
                  </label>
                  <input
                    type="text"
                    value={formData.display_name}
                    onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                    className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-purple)]/10 focus:border-[var(--color-status-purple)]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-purple)]/10 focus:border-[var(--color-status-purple)]"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                    Color
                  </label>
                  <input
                    type="color"
                    value={formData.color}
                    onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                    className="w-full h-10 rounded-lg cursor-pointer"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                    Icon Name
                  </label>
                  <input
                    type="text"
                    value={formData.icon}
                    onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                    className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-purple)]/10 focus:border-[var(--color-status-purple)]"
                    placeholder="e.g., music, home, cloud"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="w-4 h-4 text-[var(--color-status-purple)] rounded focus:ring-[var(--color-status-purple)]"
                />
                <label htmlFor="is_active" className="text-sm text-[var(--color-content-secondary)]">
                  Active (category appears in dropdowns)
                </label>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 bg-[var(--color-status-purple)] text-white rounded-lg hover:opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Check className="w-4 h-4" />
                  {saving ? 'Saving...' : editingCategory ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && deletingCategory && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-xl max-w-md w-full">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">
                Delete Category
              </h3>
              <p className="text-[var(--color-content-secondary)] mb-4">
                Are you sure you want to delete "<strong>{deletingCategory.display_name}</strong>"?
                {deletingCategory.scenario_count > 0 && (
                  <span className="block mt-2 text-[var(--color-status-amber)]">
                    This category is used by {deletingCategory.scenario_count} scenario(s).
                  </span>
                )}
              </p>

              {formError && (
                <div className="mb-4 p-3 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg text-sm text-[var(--color-status-danger)]">
                  <p className="mb-2">{formError}</p>
                  <label className="flex items-center gap-2 mt-2">
                    <input
                      type="checkbox"
                      checked={deleteForce}
                      onChange={(e) => setDeleteForce(e.target.checked)}
                      className="w-4 h-4 text-[var(--color-status-danger)] rounded focus:ring-red-500"
                    />
                    <span className="text-sm">Force delete anyway</span>
                  </label>
                </div>
              )}

              <div className="flex justify-end gap-2">
                <button
                  onClick={() => {
                    setShowDeleteConfirm(false);
                    setFormError(null);
                    setDeleteForce(false);
                  }}
                  className="px-4 py-2 text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmDelete}
                  className="px-4 py-2 bg-[var(--color-status-danger)] text-white rounded-lg hover:opacity-90 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CategoriesPage;
