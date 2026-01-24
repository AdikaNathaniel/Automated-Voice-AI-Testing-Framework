/**
 * Admin Types
 *
 * Type definitions for super admin console including
 * organizations and user management.
 */

// =============================================================================
// Organization Types
// =============================================================================

export interface Organization {
  id: string;
  name: string;
  admin_email: string;
  admin_username: string;
  is_active: boolean;
  member_count: number;
  settings: Record<string, unknown>;
  created_at: string;
  updated_at?: string;
}

export interface OrganizationCreate {
  name: string;
  admin_email: string;
  admin_username: string;
  admin_password: string;
  admin_full_name?: string;
  settings?: Record<string, unknown>;
}

export interface OrganizationUpdate {
  name?: string;
  settings?: Record<string, unknown>;
  is_active?: boolean;
}

export interface OrganizationListResponse {
  items: Organization[];
  total: number;
  page: number;
  page_size: number;
}

export interface OrganizationMember {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: string;
  is_active: boolean;
  joined_at: string;
}

export interface OrganizationMemberAdd {
  user_id: string;
  role?: string;
}

export interface OrganizationMemberListResponse {
  items: OrganizationMember[];
  total: number;
  organization_id: string;
  organization_name: string;
}

// =============================================================================
// User Types
// =============================================================================

export type UserRole =
  | 'super_admin'
  | 'org_admin'
  | 'admin'
  | 'qa_lead'
  | 'validator'
  | 'viewer';

export interface UserDetail {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: UserRole | null;
  is_active: boolean;
  tenant_id: string | null;
  is_organization_owner: boolean;
  organization_name: string | null;
  language_proficiencies: string[] | null;
  last_login_at: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
  full_name: string;
  role?: UserRole;
  is_active?: boolean;
  tenant_id?: string;
  language_proficiencies?: string[];
}

export interface UserUpdate {
  email?: string;
  username?: string;
  full_name?: string;
  role?: UserRole;
  is_active?: boolean;
  tenant_id?: string | null;
  language_proficiencies?: string[];
}

export interface UserPasswordReset {
  new_password: string;
}

export interface UserListResponse {
  items: UserDetail[];
  total: number;
  page: number;
  page_size: number;
}

export interface UserStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  users_by_role: Record<string, number>;
  users_by_organization: number;
  individual_users: number;
}

// =============================================================================
// Admin Dashboard Types
// =============================================================================

export interface AdminDashboardStats {
  organizations: {
    total: number;
    active: number;
  };
  users: UserStats;
}

// =============================================================================
// Role Display Helpers
// =============================================================================

export const ROLE_LABELS: Record<UserRole, string> = {
  super_admin: 'Super Admin',
  org_admin: 'Org Admin',
  admin: 'Admin',
  qa_lead: 'QA Lead',
  validator: 'Validator',
  viewer: 'Viewer',
};

export const ROLE_COLORS: Record<UserRole, { bg: string; text: string }> = {
  super_admin: { bg: 'bg-[var(--color-status-purple-bg)]', text: 'text-[var(--color-status-purple)]' },
  org_admin: { bg: 'bg-[var(--color-status-indigo-bg)]', text: 'text-[var(--color-status-indigo)]' },
  admin: { bg: 'bg-[var(--color-status-info-bg)]', text: 'text-[var(--color-status-info)]' },
  qa_lead: { bg: 'bg-[var(--color-status-teal-bg)]', text: 'text-[var(--color-status-teal)]' },
  validator: { bg: 'bg-[var(--color-status-success-bg)]', text: 'text-[var(--color-status-success)]' },
  viewer: { bg: 'bg-[var(--color-surface-inset)]', text: 'text-[var(--color-content-secondary)]' },
};
