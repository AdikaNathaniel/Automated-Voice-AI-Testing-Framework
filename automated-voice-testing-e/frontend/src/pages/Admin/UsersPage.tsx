/**
 * Users Management Page
 *
 * Super admin page for managing users including
 * create, edit, delete, activate/deactivate, and password reset.
 */

import React, { useEffect, useState, useCallback, useRef } from 'react';
import ReactDOM from 'react-dom';
import {
  Users,
  Plus,
  Search,
  Edit2,
  Trash2,
  MoreVertical,
  ChevronLeft,
  ChevronRight,
  X,
  UserCheck,
  UserX,
  Key,
  Filter,
  Building2,
} from 'lucide-react';
import {
  listUsers,
  createUser,
  updateUser,
  deleteUser,
  activateUser,
  deactivateUser,
  resetUserPassword,
  listOrganizations,
} from '../../services/admin.service';
import type { UserDetail, UserCreate, UserUpdate, UserRole, Organization } from '../../types/admin';
import { ROLE_LABELS, ROLE_COLORS } from '../../types/admin';

interface FormData {
  email: string;
  username: string;
  password: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  tenant_id: string;
}

const DEFAULT_FORM_DATA: FormData = {
  email: '',
  username: '',
  password: '',
  full_name: '',
  role: 'viewer',
  is_active: true,
  tenant_id: '',
};

const ROLES: UserRole[] = ['super_admin', 'org_admin', 'admin', 'qa_lead', 'validator', 'viewer'];

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<UserDetail[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [orgFilter, setOrgFilter] = useState<string>('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 10;

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<UserDetail | null>(null);
  const [formData, setFormData] = useState<FormData>(DEFAULT_FORM_DATA);
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Password reset modal
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordUser, setPasswordUser] = useState<UserDetail | null>(null);
  const [newPassword, setNewPassword] = useState('');

  // Action menu state
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [dropdownPosition, setDropdownPosition] = useState<{ top: number; right: number } | null>(null);
  const buttonRefsMap = useRef<Map<string, HTMLButtonElement>>(new Map());

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params: Record<string, unknown> = {
        page,
        page_size: pageSize,
        include_org_owners: true,  // Show organization owners in user list
      };
      if (search) params.search = search;
      if (roleFilter) params.role = roleFilter;
      if (statusFilter) params.is_active = statusFilter === 'active';
      if (orgFilter) params.organization_id = orgFilter;

      const [usersResponse, orgsResponse] = await Promise.all([
        listUsers(params as Parameters<typeof listUsers>[0]),
        listOrganizations({ page: 1, page_size: 100 }),
      ]);

      setUsers(usersResponse.items);
      setTotal(usersResponse.total);
      setOrganizations(orgsResponse.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load users');
    } finally {
      setLoading(false);
    }
  }, [page, search, roleFilter, statusFilter, orgFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

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
        const isDropdown = target.closest('.user-dropdown-menu');
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
    setEditingUser(null);
    setFormError(null);
    setShowModal(true);
  };

  const handleEdit = (user: UserDetail) => {
    setFormData({
      email: user.email,
      username: user.username,
      password: '',
      full_name: user.full_name,
      role: user.role || 'viewer',
      is_active: user.is_active,
      tenant_id: user.tenant_id || '',
    });
    setEditingUser(user);
    setFormError(null);
    setShowModal(true);
    setOpenMenu(null);
  };

  const handleDelete = async (user: UserDetail) => {
    if (!window.confirm(`Are you sure you want to delete "${user.username}"?`)) {
      return;
    }
    setOpenMenu(null);
    try {
      await deleteUser(user.id);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete user');
    }
  };

  const handleToggleActive = async (user: UserDetail) => {
    setOpenMenu(null);
    try {
      if (user.is_active) {
        await deactivateUser(user.id);
      } else {
        await activateUser(user.id);
      }
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user');
    }
  };

  const handleResetPassword = (user: UserDetail) => {
    setPasswordUser(user);
    setNewPassword('');
    setShowPasswordModal(true);
    setOpenMenu(null);
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!passwordUser || !newPassword) return;

    try {
      setSaving(true);
      await resetUserPassword(passwordUser.id, { new_password: newPassword });
      setShowPasswordModal(false);
      setPasswordUser(null);
      setNewPassword('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset password');
    } finally {
      setSaving(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!formData.email.trim()) {
      setFormError('Email is required');
      return;
    }
    if (!formData.username.trim()) {
      setFormError('Username is required');
      return;
    }
    if (!formData.full_name.trim()) {
      setFormError('Full name is required');
      return;
    }
    if (!editingUser && !formData.password.trim()) {
      setFormError('Password is required for new users');
      return;
    }

    try {
      setSaving(true);

      if (editingUser) {
        const updateData: UserUpdate = {
          email: formData.email,
          username: formData.username,
          full_name: formData.full_name,
          role: formData.role,
          is_active: formData.is_active,
          tenant_id: formData.tenant_id || null,
        };
        await updateUser(editingUser.id, updateData);
      } else {
        const createData: UserCreate = {
          email: formData.email,
          username: formData.username,
          password: formData.password,
          full_name: formData.full_name,
          role: formData.role,
          is_active: formData.is_active,
          tenant_id: formData.tenant_id || undefined,
        };
        await createUser(createData);
      }

      setShowModal(false);
      await loadData();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Failed to save user');
    } finally {
      setSaving(false);
    }
  };

  const getOrgName = (tenantId: string | null) => {
    if (!tenantId) return null;
    const org = organizations.find(o => o.id === tenantId);
    return org?.name || 'Unknown';
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
              <Users className="w-6 h-6" style={{ color: '#9333EA' }} />
              Users
            </h1>
            <p className="text-sm text-[var(--color-content-muted)] mt-1">
              Manage users across the platform
            </p>
          </div>
          <button
            onClick={handleCreate}
            className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 text-white hover:shadow-lg hover:-translate-y-0.5"
            style={{ background: 'linear-gradient(135deg, #9333EA 0%, #7E22CE 100%)' }}
          >
            <Plus size={14} />
            New User
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg text-[var(--color-status-danger)]">
          {error}
          <button onClick={() => setError(null)} className="ml-2 underline">Dismiss</button>
        </div>
      )}

      {/* Search and Filters */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--color-content-muted)]" />
          <input
            type="text"
            placeholder="Search users..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="w-full pl-10 pr-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
          />
        </div>

        <select
          value={roleFilter}
          onChange={(e) => { setRoleFilter(e.target.value); setPage(1); }}
          className="px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
        >
          <option value="">All Roles</option>
          {ROLES.map(role => (
            <option key={role} value={role}>{ROLE_LABELS[role]}</option>
          ))}
        </select>

        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
        >
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>

        <select
          value={orgFilter}
          onChange={(e) => { setOrgFilter(e.target.value); setPage(1); }}
          className="px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
        >
          <option value="">All Organizations</option>
          {organizations.map(org => (
            <option key={org.id} value={org.id}>{org.name}</option>
          ))}
        </select>

        <div className="text-sm text-[var(--color-content-muted)]">
          {total} user{total !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)] shadow-md overflow-hidden">
        {loading ? (
          <div className="flex flex-col items-center justify-center p-20">
            <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#9333EA' }}></div>
            <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Users...</div>
          </div>
        ) : users.length === 0 ? (
          <div className="p-8 text-center text-[var(--color-content-muted)]">
            {search || roleFilter || statusFilter || orgFilter ? 'No users match your filters' : 'No users yet'}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[var(--color-surface-inset)]/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">
                    Organization
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">
                    Last Login
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border-subtle)]">
                {users.map((user) => {
                  const roleColors = user.role ? ROLE_COLORS[user.role] : ROLE_COLORS.viewer;
                  const roleLabel = user.role ? ROLE_LABELS[user.role] : 'None';
                  const orgName = getOrgName(user.tenant_id);

                  return (
                    <tr key={user.id} className="hover:bg-[var(--color-interactive-hover)]/50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center text-white font-semibold">
                            {user.full_name[0]?.toUpperCase()}
                          </div>
                          <div>
                            <div className="font-medium text-[var(--color-content-primary)]">{user.full_name}</div>
                            <div className="text-xs text-[var(--color-content-muted)]">{user.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2.5 py-1 text-xs font-medium rounded-lg ${roleColors.bg} ${roleColors.text}`}>
                          {roleLabel}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {orgName ? (
                          <div className="flex items-center gap-1.5 text-[var(--color-content-secondary)]">
                            <Building2 className="w-4 h-4" />
                            <span className="text-sm">{orgName}</span>
                          </div>
                        ) : (
                          <span className="text-sm text-[var(--color-content-muted)]">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex px-2.5 py-1 text-xs font-medium rounded-lg ${
                            user.is_active
                              ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]'
                              : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)]'
                          }`}
                        >
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-[var(--color-content-muted)]">
                        {user.last_login_at
                          ? new Date(user.last_login_at).toLocaleDateString()
                          : 'Never'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="relative">
                          <button
                            ref={(el) => {
                              if (el) {
                                buttonRefsMap.current.set(user.id, el);
                              }
                            }}
                            onClick={() => setOpenMenu(openMenu === user.id ? null : user.id)}
                            className="p-2 hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
                          >
                            <MoreVertical className="w-4 h-4 text-[var(--color-content-muted)]" />
                          </button>

                          {openMenu === user.id && dropdownPosition && ReactDOM.createPortal(
                            <div
                              className="user-dropdown-menu fixed w-48 bg-[var(--color-surface-raised)] rounded-xl shadow-lg border border-[var(--color-border-default)] py-1 z-50"
                              style={{
                                top: `${dropdownPosition.top}px`,
                                right: `${dropdownPosition.right}px`,
                              }}
                            >
                              <button
                                onClick={() => handleEdit(user)}
                                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]"
                              >
                                <Edit2 className="w-4 h-4" />
                                Edit
                              </button>
                              <button
                                onClick={() => handleResetPassword(user)}
                                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]"
                              >
                                <Key className="w-4 h-4" />
                                Reset Password
                              </button>
                              <button
                                onClick={() => handleToggleActive(user)}
                                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]"
                              >
                                {user.is_active ? (
                                  <>
                                    <UserX className="w-4 h-4" />
                                    Deactivate
                                  </>
                                ) : (
                                  <>
                                    <UserCheck className="w-4 h-4" />
                                    Activate
                                  </>
                                )}
                              </button>
                              <div className="border-t border-[var(--color-border-subtle)] my-1" />
                              <button
                                onClick={() => handleDelete(user)}
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
                  );
                })}
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

      {/* Create/Edit User Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--color-border-subtle)] sticky top-0 bg-[var(--color-surface-raised)]">
              <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">
                {editingUser ? 'Edit User' : 'New User'}
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

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
                    placeholder="user@example.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                    Username
                  </label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
                    placeholder="username"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
                  placeholder="John Doe"
                />
              </div>

              {!editingUser && (
                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                    Password
                  </label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
                    placeholder="Min 12 characters"
                  />
                  <p className="text-xs text-[var(--color-content-muted)] mt-1">
                    Must be 12+ characters with uppercase, lowercase, number, and special character
                  </p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                    Role
                  </label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value as UserRole })}
                    className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
                  >
                    {ROLES.map(role => (
                      <option key={role} value={role}>{ROLE_LABELS[role]}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                    Organization
                  </label>
                  <select
                    value={formData.tenant_id}
                    onChange={(e) => setFormData({ ...formData, tenant_id: e.target.value })}
                    className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
                  >
                    <option value="">None (Individual)</option>
                    {organizations.map(org => (
                      <option key={org.id} value={org.id}>{org.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="w-4 h-4 text-[var(--color-status-purple)] border-[var(--color-border-default)] rounded focus:ring-[var(--color-border-focus)]"
                />
                <label htmlFor="is_active" className="text-sm text-[var(--color-content-secondary)]">
                  Active user
                </label>
              </div>

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
                  {saving ? 'Saving...' : editingUser ? 'Save Changes' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Password Reset Modal */}
      {showPasswordModal && passwordUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-xl w-full max-w-md">
            <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--color-border-subtle)]">
              <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">
                Reset Password
              </h2>
              <button
                onClick={() => setShowPasswordModal(false)}
                className="p-2 hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-[var(--color-content-muted)]" />
              </button>
            </div>

            <form onSubmit={handlePasswordSubmit} className="p-6 space-y-4">
              <p className="text-sm text-[var(--color-content-secondary)]">
                Reset password for <span className="font-medium">{passwordUser.username}</span>
              </p>

              <div>
                <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                  New Password
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
                  placeholder="Min 12 characters"
                />
                <p className="text-xs text-[var(--color-content-muted)] mt-1">
                  Must be 12+ characters with uppercase, lowercase, number, and special character
                </p>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowPasswordModal(false)}
                  className="px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving || !newPassword}
                  className="px-4 py-2.5 bg-[var(--color-status-purple)] text-white rounded-xl hover:opacity-90 disabled:opacity-50 transition-colors"
                >
                  {saving ? 'Resetting...' : 'Reset Password'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersPage;
