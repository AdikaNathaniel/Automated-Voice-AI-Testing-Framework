/**
 * User Profile Component
 *
 * Displays and manages user profile information with:
 * - Display mode: Shows user information (email, username, full name, role)
 * - Edit mode: Allows editing profile information with validation
 * - Change password: Secure password change functionality
 * - Redux integration: Gets user from auth state and dispatches updates
 * - API integration: Updates profile and password via API calls
 * - Error handling: Displays error and success messages
 * - Loading states: Shows loading indicators during API calls
 * - Form validation: Uses react-hook-form with yup schemas
 *
 * @example
 * ```tsx
 * import UserProfile from './components/UserProfile';
 *
 * function ProfilePage() {
 *   return <UserProfile />;
 * }
 * ```
 */

import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { RootState } from '../store';
import { updateUser } from '../store/slices/authSlice';
import apiClient from '../services/api';
import type { User } from '../types/auth';

/**
 * Profile Update Form Data
 */
interface ProfileFormData {
  email: string;
  username: string;
  full_name: string;
}

/**
 * Password Change Form Data
 */
interface PasswordFormData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

/**
 * Profile validation schema
 */
const profileSchema = yup.object().shape({
  email: yup
    .string()
    .required('Email is required')
    .email('Please enter a valid email address')
    .trim()
    .lowercase(),
  username: yup
    .string()
    .required('Username is required')
    .min(3, 'Username must be at least 3 characters')
    .max(50, 'Username must not exceed 50 characters')
    .trim(),
  full_name: yup
    .string()
    .required('Full name is required')
    .min(2, 'Full name must be at least 2 characters')
    .max(100, 'Full name must not exceed 100 characters')
    .trim(),
});

/**
 * Password validation schema
 */
const passwordSchema = yup.object().shape({
  currentPassword: yup.string().required('Current password is required'),
  newPassword: yup
    .string()
    .required('New password is required')
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    ),
  confirmPassword: yup
    .string()
    .required('Please confirm your new password')
    .oneOf([yup.ref('newPassword')], 'Passwords must match'),
});

/**
 * User Profile Component
 *
 * Manages user profile display and editing
 */
const UserProfile: React.FC = () => {
  // Get user from Redux store
  const { user } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch();

  // Component state
  const [isEditing, setIsEditing] = useState(false);
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);
  const [isLoadingPassword, setIsLoadingPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Profile form
  const {
    control: profileControl,
    handleSubmit: handleProfileSubmit,
    formState: { errors: profileErrors },
    reset: resetProfile,
  } = useForm<ProfileFormData>({
    resolver: yupResolver(profileSchema),
    defaultValues: {
      email: user?.email || '',
      username: user?.username || '',
      full_name: user?.full_name || '',
    },
  });

  // Password form
  const {
    control: passwordControl,
    handleSubmit: handlePasswordSubmit,
    formState: { errors: passwordErrors },
    reset: resetPassword,
  } = useForm<PasswordFormData>({
    resolver: yupResolver(passwordSchema),
    defaultValues: {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    },
  });

  /**
   * Handle profile update submission
   */
  const onProfileSubmit = async (data: ProfileFormData) => {
    setIsLoadingProfile(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      // Make API call to update profile
      const response = await apiClient.put<User>('/v1/users/me', {
        email: data.email,
        username: data.username,
        full_name: data.full_name,
      });

      // Update Redux store with new user data
      dispatch(updateUser(response.data));

      // Show success message and exit edit mode
      setSuccessMessage('Profile updated successfully');
      setIsEditing(false);
    } catch (error: unknown) {
      let message = 'Failed to update profile';
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string } } };
        message = axiosError.response?.data?.detail || message;
      }
      setErrorMessage(message);
    } finally {
      setIsLoadingProfile(false);
    }
  };

  /**
   * Handle password change submission
   */
  const onPasswordSubmit = async (data: PasswordFormData) => {
    setIsLoadingPassword(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      // Make API call to change password
      await apiClient.post('/v1/users/me/change-password', {
        current_password: data.currentPassword,
        new_password: data.newPassword,
      });

      // Show success message and reset form
      setSuccessMessage('Password changed successfully');
      resetPassword();
    } catch (error: unknown) {
      let message = 'Failed to change password';
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string } } };
        message = axiosError.response?.data?.detail || message;
      }
      setErrorMessage(message);
    } finally {
      setIsLoadingPassword(false);
    }
  };

  /**
   * Handle cancel edit
   */
  const handleCancelEdit = () => {
    // Reset form to original values
    resetProfile({
      email: user?.email || '',
      username: user?.username || '',
      full_name: user?.full_name || '',
    });
    setIsEditing(false);
    setErrorMessage(null);
  };

  /**
   * Handle edit button click
   */
  const handleEditClick = () => {
    setIsEditing(true);
    setErrorMessage(null);
    setSuccessMessage(null);
  };

  if (!user) {
    return (
      <div className="container max-w-3xl mx-auto px-4">
        <div className="mt-8 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-[var(--color-brand-primary)] mx-auto" />
          <p className="mt-4 text-[var(--color-content-secondary)]">Loading user profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container max-w-3xl mx-auto px-4">
      <div className="mt-8 mb-8 space-y-6">
        {/* Error Message */}
        {errorMessage && (
          <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-md p-4 flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-[var(--color-status-danger)] flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-[var(--color-status-danger)]">{errorMessage}</p>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-[var(--color-status-danger)] hover:opacity-80"
              aria-label="Close"
            >
              ×
            </button>
          </div>
        )}

        {/* Success Message */}
        {successMessage && (
          <div className="bg-[var(--color-status-success-bg)] border border-[var(--color-status-success)] rounded-md p-4 flex items-start gap-2">
            <CheckCircle className="w-5 h-5 text-[var(--color-status-success)] flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-[var(--color-status-success)]">{successMessage}</p>
            </div>
            <button
              onClick={() => setSuccessMessage(null)}
              className="text-[var(--color-status-success)] hover:opacity-80"
              aria-label="Close"
            >
              ×
            </button>
          </div>
        )}

        {/* Profile Information Card */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Profile Information</h2>

          {!isEditing ? (
            /* Display Mode */
            <div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                    Email
                  </label>
                  <p className="text-[var(--color-content-primary)]">{user.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                    Username
                  </label>
                  <p className="text-[var(--color-content-primary)]">{user.username}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                    Full Name
                  </label>
                  <p className="text-[var(--color-content-primary)]">{user.full_name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                    Role
                  </label>
                  <p className="text-[var(--color-content-primary)]">{user.role}</p>
                </div>
              </div>

              <div className="mt-6">
                <button type="button" onClick={handleEditClick} className="btn">
                  Edit Profile
                </button>
              </div>
            </div>
          ) : (
            /* Edit Mode */
            <form onSubmit={handleProfileSubmit(onProfileSubmit)}>
              <div className="space-y-4">
                {/* Email Field */}
                <Controller
                  name="email"
                  control={profileControl}
                  render={({ field }) => (
                    <div>
                      <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                        Email
                      </label>
                      <input
                        {...field}
                        type="email"
                        disabled={isLoadingProfile}
                        className={`w-full px-3 py-2 border rounded-md focus:ring-1 ${
                          profileErrors.email
                            ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-[var(--color-status-danger)]'
                            : 'border-[var(--color-border-default)] focus:border-[var(--color-brand-primary)] focus:ring-[var(--color-brand-primary)]'
                        } disabled:bg-[var(--color-surface-inset)] disabled:cursor-not-allowed`}
                      />
                      {profileErrors.email && (
                        <p className="mt-1 text-sm text-[var(--color-status-danger)]">{profileErrors.email.message}</p>
                      )}
                    </div>
                  )}
                />

                {/* Username Field */}
                <Controller
                  name="username"
                  control={profileControl}
                  render={({ field }) => (
                    <div>
                      <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                        Username
                      </label>
                      <input
                        {...field}
                        type="text"
                        disabled={isLoadingProfile}
                        className={`w-full px-3 py-2 border rounded-md focus:ring-1 ${
                          profileErrors.username
                            ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-[var(--color-status-danger)]'
                            : 'border-[var(--color-border-default)] focus:border-[var(--color-brand-primary)] focus:ring-[var(--color-brand-primary)]'
                        } disabled:bg-[var(--color-surface-inset)] disabled:cursor-not-allowed`}
                      />
                      {profileErrors.username && (
                        <p className="mt-1 text-sm text-[var(--color-status-danger)]">{profileErrors.username.message}</p>
                      )}
                    </div>
                  )}
                />

                {/* Full Name Field */}
                <Controller
                  name="full_name"
                  control={profileControl}
                  render={({ field }) => (
                    <div>
                      <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                        Full Name
                      </label>
                      <input
                        {...field}
                        type="text"
                        disabled={isLoadingProfile}
                        className={`w-full px-3 py-2 border rounded-md focus:ring-1 ${
                          profileErrors.full_name
                            ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-[var(--color-status-danger)]'
                            : 'border-[var(--color-border-default)] focus:border-[var(--color-brand-primary)] focus:ring-[var(--color-brand-primary)]'
                        } disabled:bg-[var(--color-surface-inset)] disabled:cursor-not-allowed`}
                      />
                      {profileErrors.full_name && (
                        <p className="mt-1 text-sm text-[var(--color-status-danger)]">{profileErrors.full_name.message}</p>
                      )}
                    </div>
                  )}
                />

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={isLoadingProfile}
                    className="btn flex items-center gap-2"
                  >
                    {isLoadingProfile && <Loader2 className="w-4 h-4 animate-spin" />}
                    {isLoadingProfile ? 'Saving...' : 'Save Changes'}
                  </button>
                  <button
                    type="button"
                    onClick={handleCancelEdit}
                    disabled={isLoadingProfile}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </form>
          )}
        </div>

        {/* Change Password Card */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Change Password</h2>

          <form onSubmit={handlePasswordSubmit(onPasswordSubmit)}>
            <div className="space-y-4">
              {/* Current Password Field */}
              <Controller
                name="currentPassword"
                control={passwordControl}
                render={({ field }) => (
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                      Current Password
                    </label>
                    <input
                      {...field}
                      type="password"
                      disabled={isLoadingPassword}
                      className={`w-full px-3 py-2 border rounded-md focus:ring-1 ${
                        passwordErrors.currentPassword
                          ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-[var(--color-status-danger)]'
                          : 'border-[var(--color-border-default)] focus:border-[var(--color-brand-primary)] focus:ring-[var(--color-brand-primary)]'
                      } disabled:bg-[var(--color-surface-inset)] disabled:cursor-not-allowed`}
                    />
                    {passwordErrors.currentPassword && (
                      <p className="mt-1 text-sm text-[var(--color-status-danger)]">{passwordErrors.currentPassword.message}</p>
                    )}
                  </div>
                )}
              />

              {/* New Password Field */}
              <Controller
                name="newPassword"
                control={passwordControl}
                render={({ field }) => (
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                      New Password
                    </label>
                    <input
                      {...field}
                      type="password"
                      disabled={isLoadingPassword}
                      className={`w-full px-3 py-2 border rounded-md focus:ring-1 ${
                        passwordErrors.newPassword
                          ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-[var(--color-status-danger)]'
                          : 'border-[var(--color-border-default)] focus:border-[var(--color-brand-primary)] focus:ring-[var(--color-brand-primary)]'
                      } disabled:bg-[var(--color-surface-inset)] disabled:cursor-not-allowed`}
                    />
                    {passwordErrors.newPassword && (
                      <p className="mt-1 text-sm text-[var(--color-status-danger)]">{passwordErrors.newPassword.message}</p>
                    )}
                  </div>
                )}
              />

              {/* Confirm Password Field */}
              <Controller
                name="confirmPassword"
                control={passwordControl}
                render={({ field }) => (
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                      Confirm New Password
                    </label>
                    <input
                      {...field}
                      type="password"
                      disabled={isLoadingPassword}
                      className={`w-full px-3 py-2 border rounded-md focus:ring-1 ${
                        passwordErrors.confirmPassword
                          ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-[var(--color-status-danger)]'
                          : 'border-[var(--color-border-default)] focus:border-[var(--color-brand-primary)] focus:ring-[var(--color-brand-primary)]'
                      } disabled:bg-[var(--color-surface-inset)] disabled:cursor-not-allowed`}
                    />
                    {passwordErrors.confirmPassword && (
                      <p className="mt-1 text-sm text-[var(--color-status-danger)]">{passwordErrors.confirmPassword.message}</p>
                    )}
                  </div>
                )}
              />

              {/* Submit Button */}
              <div>
                <button
                  type="submit"
                  disabled={isLoadingPassword}
                  className="btn flex items-center gap-2"
                >
                  {isLoadingPassword && <Loader2 className="w-4 h-4 animate-spin" />}
                  {isLoadingPassword ? 'Changing Password...' : 'Change Password'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
