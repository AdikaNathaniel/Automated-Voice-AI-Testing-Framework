/**
 * ProtectedRoute Component
 *
 * Wrapper component for routes that require authentication and/or specific roles.
 * Features:
 * - Authentication check via Redux state
 * - Automatic redirect to login if not authenticated
 * - Optional role-based access control
 * - TypeScript typed with proper interfaces
 *
 * Usage:
 *   // Basic authentication required
 *   <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
 *
 *   // Require specific role
 *   <Route path="/admin" element={<ProtectedRoute requiredRole="admin"><AdminPanel /></ProtectedRoute>} />
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import type { RootState } from '../store';

/**
 * Props interface for ProtectedRoute component
 */
interface ProtectedRouteProps {
  /** Child components to render when authorized */
  children: React.ReactNode;
  /** Optional role required to access this route (single role) */
  requiredRole?: string;
  /** Optional list of roles that can access this route (any of these) */
  allowedRoles?: string[];
}

/**
 * ProtectedRoute Component
 *
 * Protects routes by checking authentication status and optionally user role.
 * If user is not authenticated, redirects to /login.
 * If user is authenticated but lacks required role, redirects to /login.
 * If authorized, renders children.
 *
 * @param children - Components to render when authorized
 * @param requiredRole - Optional role requirement (e.g., "admin", "moderator")
 * @returns Navigate to login or children components
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  allowedRoles,
}) => {
  // Get authentication state from Redux
  const { isAuthenticated, user, accessToken } = useSelector(
    (state: RootState) => state.auth
  );

  const hasSession = isAuthenticated || Boolean(accessToken);

  // Check if user is authenticated
  if (!hasSession) {
    // Redirect to login page with return URL
    return <Navigate to="/login" replace />;
  }

  // Check role-based access if requiredRole or allowedRoles is specified
  if (requiredRole || allowedRoles) {
    // Check if user exists and has a role
    if (!user) {
      // User authenticated but user object not loaded yet
      return <Navigate to="/login" replace />;
    }

    // Check if user has one of the allowed roles
    if (allowedRoles && allowedRoles.length > 0) {
      if (!user.role || !allowedRoles.includes(user.role)) {
        // User doesn't have any of the allowed roles
        return <Navigate to="/dashboard" replace />;
      }
    }
    // Check if user has the required role (legacy single role check)
    else if (requiredRole && user.role !== requiredRole) {
      // User doesn't have required role - redirect to dashboard
      return <Navigate to="/dashboard" replace />;
    }
  }

  // User is authenticated and has required role (if specified)
  // Render the protected content
  return <>{children}</>;
};

export default ProtectedRoute;
