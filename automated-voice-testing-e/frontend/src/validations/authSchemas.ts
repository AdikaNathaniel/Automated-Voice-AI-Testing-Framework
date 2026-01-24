/**
 * Authentication Form Validation Schemas
 *
 * Yup validation schemas for authentication forms including:
 * - Login form validation
 * - Registration form validation
 *
 * These schemas are used with react-hook-form for client-side validation.
 */

import * as yup from 'yup';

/**
 * Login Form Validation Schema
 *
 * Validates:
 * - email: Required, must be valid email format
 * - password: Required, minimum length 1 character
 */
export const loginSchema = yup.object().shape({
  email: yup
    .string()
    .required('Email is required')
    .email('Please enter a valid email address')
    .trim()
    .lowercase(),
  password: yup
    .string()
    .required('Password is required')
    .min(1, 'Password is required'),
});

/**
 * Registration Form Validation Schema
 *
 * Validates:
 * - email: Required, valid email format
 * - username: Required, 3-50 characters, alphanumeric with hyphens/underscores
 * - password: Required, minimum 8 characters
 * - full_name: Required, 1-100 characters
 */
export const registerSchema = yup.object().shape({
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
    .matches(
      /^[a-zA-Z0-9_-]+$/,
      'Username can only contain letters, numbers, hyphens, and underscores'
    )
    .trim(),
  password: yup
    .string()
    .required('Password is required')
    .min(8, 'Password must be at least 8 characters'),
  full_name: yup
    .string()
    .required('Full name is required')
    .min(1, 'Full name is required')
    .max(100, 'Full name must not exceed 100 characters')
    .trim(),
});

/**
 * Type inference from schemas for TypeScript
 */
export type LoginFormData = yup.InferType<typeof loginSchema>;
export type RegisterFormData = yup.InferType<typeof registerSchema>;
