/**
 * Organizations Management Page
 *
 * Super admin page for managing organizations including
 * create, edit, delete, and viewing members.
 */

import React, { useEffect, useState, useCallback, useRef } from 'react';
import ReactDOM from 'react-dom';
import {
  Building2,
  Plus,
  Search,
  Edit2,
  Trash2,
  Users,
  MoreVertical,
  ChevronLeft,
  ChevronRight,
  X,
  Check,
} from 'lucide-react';
import {
  listOrganizations,
  createOrganization,
  updateOrganization,
  deleteOrganization,
} from '../../services/admin.service';
import type { Organization, OrganizationCreate, OrganizationUpdate } from '../../types/admin';

interface FormData {
  name: string;
  admin_email: string;
  admin_username: string;
  admin_password: string;
  admin_full_name: string;
}

const DEFAULT_FORM_DATA: FormData = {
  name: '',
  admin_email: '',
  admin_username: '',
  admin_password: '',
  admin_full_name: '',
};

const OrganizationsPage: React.FC = () => {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 10;

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingOrg, setEditingOrg] = useState<Organization | null>(null);
  const [formData, setFormData] = useState<FormData>(DEFAULT_FORM_DATA);
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Action menu state
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [dropdownPosition, setDropdownPosition] = useState<{ top: number; right: number } | null>(null);
  const buttonRefsMap = useRef<Map<string, HTMLButtonElement>>(new Map());

  const loadOrganizations = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await listOrganizations({ page, page_size: pageSize });
      setOrganizations(response.items);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load organizations');
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    loadOrganizations();
  }, [loadOrganizations]);

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
      if (openMenu) {
        const target = event.target as HTMLElement;
        const isButton = buttonRefsMap.current.get(openMenu)?.contains(target);
        const isDropdown = target.closest('.org-dropdown-menu');
        if (!isButton && !isDropdown) {
          setOpenMenu(null);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [openMenu]);

  const handleCreate = () => {
    setFormData(DEFAULT_FORM_DATA);
    setEditingOrg(null);
    setFormError(null);
    setShowModal(true);
  };

  const handleEdit = (org: Organization) => {
    setFormData({
      name: org.name,
      admin_email: org.admin_email,
      admin_username: org.admin_username,
      admin_full_name: '',
    });
    setEditingOrg(org);
    setFormError(null);
    setShowModal(true);
    setOpenMenu(null);
  };

  const handleDelete = async (org: Organization) => {
    if (!window.confirm(`Are you sure you want to delete "${org.name}"? This will remove all members from the organization.`)) {
      return;
    }
    setOpenMenu(null);
    try {
      await deleteOrganization(org.id);
      await loadOrganizations();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete organization');
    }
  };

  const handleToggleActive = async (org: Organization) => {
    setOpenMenu(null);
    try {
      await updateOrganization(org.id, { is_active: !org.is_active });
      await loadOrganizations();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update organization');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!formData.name.trim()) {
      setFormError('Organization name is required');
      return;
    }

    if (!editingOrg) {
      if (!formData.admin_email.trim()) {
        setFormError('Admin email is required');
        return;
      }
      if (!formData.admin_username.trim()) {
        setFormError('Admin username is required');
        return;
      }
      if (!formData.admin_password.trim()) {
        setFormError('Admin password is required');
        return;
      }
      if (formData.admin_password.length < 12) {
        setFormError('Password must be at least 12 characters');
        return;
      }
    }

    try {
      setSaving(true);

      if (editingOrg) {
        const updateData: OrganizationUpdate = {
          name: formData.name,
        };
        await updateOrganization(editingOrg.id, updateData);
      } else {
        const createData: OrganizationCreate = {
          name: formData.name,
          admin_email: formData.admin_email,
          admin_username: formData.admin_username,
          admin_password: formData.admin_password,
          admin_full_name: formData.admin_full_name || undefined,
        };
        await createOrganization(createData);
      }

      setShowModal(false);
      await loadOrganizations();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Failed to save organization');
    } finally {
      setSaving(false);
    }
  };

  const filteredOrgs = organizations.filter(org =>
    org.name.toLowerCase().includes(search.toLowerCase()) ||
    org.admin_email.toLowerCase().includes(search.toLowerCase())
  );

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
              <Building2 className="w-6 h-6" style={{ color: '#9333EA' }} />
              Organizations
            </h1>
            <p className="text-sm text-[var(--color-content-muted)] mt-1">
              Manage organizations and their settings
            </p>
          </div>
          <button
            onClick={handleCreate}
            className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 text-white hover:shadow-lg hover:-translate-y-0.5"
            style={{ background: 'linear-gradient(135deg, #9333EA 0%, #7E22CE 100%)' }}
          >
            <Plus size={14} />
            New Organization
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg text-[var(--color-status-danger)]">
          {error}
        </div>
      )}

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--color-content-muted)]" />
          <input
            type="text"
            placeholder="Search organizations..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
          />
        </div>
        <div className="text-sm text-[var(--color-content-muted)]">
          {total} organization{total !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Organizations Table */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)] shadow-md overflow-hidden">
        {loading ? (
          <div className="flex flex-col items-center justify-center p-20">
            <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#9333EA' }}></div>
            <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Organizations...</div>
          </div>
        ) : filteredOrgs.length === 0 ? (
          <div className="p-8 text-center text-[var(--color-content-muted)]">
            {search ? 'No organizations match your search' : 'No organizations yet'}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[var(--color-surface-inset)]/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">
                    Organization
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">
                    Admin
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">
                    Members
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border-subtle)]">
                {filteredOrgs.map((org) => (
                  <tr key={org.id} className="hover:bg-[var(--color-interactive-hover)]/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center text-white font-semibold">
                          {org.name[0]?.toUpperCase()}
                        </div>
                        <div className="font-medium text-[var(--color-content-primary)]">
                          {org.name}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-[var(--color-content-primary)]">{org.admin_username}</div>
                      <div className="text-xs text-[var(--color-content-muted)]">{org.admin_email}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5 text-[var(--color-content-secondary)]">
                        <Users className="w-4 h-4" />
                        <span>{org.member_count}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex px-2.5 py-1 text-xs font-medium rounded-lg ${
                          org.is_active
                            ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]'
                            : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)]'
                        }`}
                      >
                        {org.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-[var(--color-content-muted)]">
                      {new Date(org.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="relative">
                        <button
                          ref={(el) => {
                            if (el) {
                              buttonRefsMap.current.set(org.id, el);
                            }
                          }}
                          onClick={() => setOpenMenu(openMenu === org.id ? null : org.id)}
                          className="p-2 hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
                        >
                          <MoreVertical className="w-4 h-4 text-[var(--color-content-muted)]" />
                        </button>

                        {openMenu === org.id && dropdownPosition && ReactDOM.createPortal(
                          <div
                            className="org-dropdown-menu fixed w-48 bg-[var(--color-surface-raised)] rounded-xl shadow-lg border border-[var(--color-border-default)] py-1 z-50"
                            style={{
                              top: `${dropdownPosition.top}px`,
                              right: `${dropdownPosition.right}px`,
                            }}
                          >
                            <button
                              onClick={() => handleEdit(org)}
                              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]"
                            >
                              <Edit2 className="w-4 h-4" />
                              Edit
                            </button>
                            <button
                              onClick={() => handleToggleActive(org)}
                              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]"
                            >
                              {org.is_active ? (
                                <>
                                  <X className="w-4 h-4" />
                                  Deactivate
                                </>
                              ) : (
                                <>
                                  <Check className="w-4 h-4" />
                                  Activate
                                </>
                              )}
                            </button>
                            <div className="border-t border-[var(--color-border-subtle)] my-1" />
                            <button
                              onClick={() => handleDelete(org)}
                              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-status-danger)] hover:bg-[var(--color-status-danger-bg)]"
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

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-[var(--color-border-subtle)]">
            <div className="text-sm text-[var(--color-content-muted)]">
              Page {page} of {totalPages}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 hover:bg-[var(--color-interactive-hover)] rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-2 hover:bg-[var(--color-interactive-hover)] rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-xl w-full max-w-md">
            <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--color-border-subtle)]">
              <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">
                {editingOrg ? 'Edit Organization' : 'New Organization'}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="p-2 hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-[var(--color-content-muted)]" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {formError && (
                <div className="p-3 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg text-[var(--color-status-danger)] text-sm">
                  {formError}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                  Organization Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
                  placeholder="Acme Corporation"
                />
              </div>

              {!editingOrg && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                      Admin Email
                    </label>
                    <input
                      type="email"
                      value={formData.admin_email}
                      onChange={(e) => setFormData({ ...formData, admin_email: e.target.value })}
                      className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
                      placeholder="admin@acme.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                      Admin Username
                    </label>
                    <input
                      type="text"
                      value={formData.admin_username}
                      onChange={(e) => setFormData({ ...formData, admin_username: e.target.value })}
                      className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
                      placeholder="acme_admin"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                      Admin Password
                    </label>
                    <input
                      type="password"
                      value={formData.admin_password}
                      onChange={(e) => setFormData({ ...formData, admin_password: e.target.value })}
                      className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
                      placeholder="Min 12 characters"
                    />
                    <p className="text-xs text-[var(--color-content-muted)] mt-1">
                      Must be 12+ characters with uppercase, lowercase, number, and special character
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                      Admin Full Name (Optional)
                    </label>
                    <input
                      type="text"
                      value={formData.admin_full_name}
                      onChange={(e) => setFormData({ ...formData, admin_full_name: e.target.value })}
                      className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
                      placeholder="John Doe"
                    />
                  </div>
                </>
              )}

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2.5 bg-[var(--color-status-purple)] text-white rounded-xl hover:opacity-90 disabled:opacity-50 transition-colors"
                >
                  {saving ? 'Saving...' : editingOrg ? 'Save Changes' : 'Create Organization'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrganizationsPage;
