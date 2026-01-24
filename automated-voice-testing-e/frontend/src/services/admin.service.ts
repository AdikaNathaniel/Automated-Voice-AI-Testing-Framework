/**
 * Admin Service
 *
 * API service for super admin console - organization and user management.
 */

import apiClient from './api';
import type {
  Organization,
  OrganizationCreate,
  OrganizationUpdate,
  OrganizationListResponse,
  OrganizationMember,
  OrganizationMemberAdd,
  OrganizationMemberListResponse,
  UserDetail,
  UserCreate,
  UserUpdate,
  UserPasswordReset,
  UserListResponse,
  UserStats,
} from '../types/admin';

// =============================================================================
// Organization Endpoints
// =============================================================================

/**
 * List all organizations with pagination.
 */
export const listOrganizations = async (params?: {
  page?: number;
  page_size?: number;
}): Promise<OrganizationListResponse> => {
  const response = await apiClient.get<OrganizationListResponse>('/organizations', {
    params,
  });
  return response.data;
};

/**
 * Get organization by ID.
 */
export const getOrganization = async (orgId: string): Promise<Organization> => {
  const response = await apiClient.get<Organization>(`/organizations/${orgId}`);
  return response.data;
};

/**
 * Create a new organization.
 */
export const createOrganization = async (
  data: OrganizationCreate
): Promise<Organization> => {
  const response = await apiClient.post<Organization>('/organizations', data);
  return response.data;
};

/**
 * Update an organization.
 */
export const updateOrganization = async (
  orgId: string,
  data: OrganizationUpdate
): Promise<Organization> => {
  const response = await apiClient.put<Organization>(`/organizations/${orgId}`, data);
  return response.data;
};

/**
 * Delete an organization.
 */
export const deleteOrganization = async (orgId: string): Promise<void> => {
  await apiClient.delete(`/organizations/${orgId}`);
};

/**
 * List organization members.
 */
export const listOrganizationMembers = async (
  orgId: string,
  params?: {
    page?: number;
    page_size?: number;
  }
): Promise<OrganizationMemberListResponse> => {
  const response = await apiClient.get<OrganizationMemberListResponse>(
    `/organizations/${orgId}/members`,
    { params }
  );
  return response.data;
};

/**
 * Add member to organization.
 */
export const addOrganizationMember = async (
  orgId: string,
  data: OrganizationMemberAdd
): Promise<OrganizationMember> => {
  const response = await apiClient.post<OrganizationMember>(
    `/organizations/${orgId}/members`,
    data
  );
  return response.data;
};

/**
 * Remove member from organization.
 */
export const removeOrganizationMember = async (
  orgId: string,
  userId: string
): Promise<void> => {
  await apiClient.delete(`/organizations/${orgId}/members/${userId}`);
};

// =============================================================================
// User Endpoints
// =============================================================================

/**
 * Get user statistics.
 */
export const getUserStats = async (): Promise<UserStats> => {
  const response = await apiClient.get<UserStats>('/users/stats');
  return response.data;
};

/**
 * List all users with filtering and pagination.
 */
export const listUsers = async (params?: {
  page?: number;
  page_size?: number;
  search?: string;
  role?: string;
  is_active?: boolean;
  organization_id?: string;
  include_org_owners?: boolean;
}): Promise<UserListResponse> => {
  const response = await apiClient.get<UserListResponse>('/users', { params });
  return response.data;
};

/**
 * Get user by ID.
 */
export const getUser = async (userId: string): Promise<UserDetail> => {
  const response = await apiClient.get<UserDetail>(`/users/${userId}`);
  return response.data;
};

/**
 * Create a new user.
 */
export const createUser = async (data: UserCreate): Promise<UserDetail> => {
  const response = await apiClient.post<UserDetail>('/users', data);
  return response.data;
};

/**
 * Update a user.
 */
export const updateUser = async (
  userId: string,
  data: UserUpdate
): Promise<UserDetail> => {
  const response = await apiClient.put<UserDetail>(`/users/${userId}`, data);
  return response.data;
};

/**
 * Delete a user.
 */
export const deleteUser = async (userId: string): Promise<void> => {
  await apiClient.delete(`/users/${userId}`);
};

/**
 * Reset user password.
 */
export const resetUserPassword = async (
  userId: string,
  data: UserPasswordReset
): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>(
    `/users/${userId}/reset-password`,
    data
  );
  return response.data;
};

/**
 * Deactivate a user.
 */
export const deactivateUser = async (userId: string): Promise<UserDetail> => {
  const response = await apiClient.post<UserDetail>(`/users/${userId}/deactivate`);
  return response.data;
};

/**
 * Activate a user.
 */
export const activateUser = async (userId: string): Promise<UserDetail> => {
  const response = await apiClient.post<UserDetail>(`/users/${userId}/activate`);
  return response.data;
};
