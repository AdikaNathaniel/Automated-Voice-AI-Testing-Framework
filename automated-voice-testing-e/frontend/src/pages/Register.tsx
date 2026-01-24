/**
 * Registration Page Component
 *
 * Split-screen registration with visual branding panel and clean form.
 * Matches login page design with enhanced password strength meter.
 */

import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { Link, useNavigate } from 'react-router-dom';
import { Loader2, Mail, Lock, Eye, EyeOff, User, AtSign, Brain, GitBranch, Globe, ArrowRight, CheckCircle } from 'lucide-react';
import { registerSchema, type RegisterFormData } from '../validations/authSchemas';
import { OuterNav, PasswordStrengthMeter } from '../components/outer';
import vaiLogo from '../assets/vai-logo.png';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Feature highlights for the visual panel
const features = [
  { icon: Brain, text: 'AI + Human validation' },
  { icon: GitBranch, text: 'CI/CD integration' },
  { icon: Globe, text: '8+ languages supported' },
];

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const {
    control,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: yupResolver(registerSchema),
    defaultValues: {
      email: '',
      username: '',
      password: '',
      full_name: '',
    },
  });

  const password = watch('password');

  const onSubmit = async (data: RegisterFormData) => {
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await axios.post(`${API_BASE_URL}/auth/register`, data);
      setSuccessMessage('Registration successful! Redirecting to login...');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err: any) {
      const message =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Registration failed. Please try again.';
      setError(message);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex font-display">
      {/* Left Panel - Visual/Branding */}
      <div className="hidden lg:flex lg:w-[55%] relative bg-[var(--color-slate-900)] overflow-hidden">
        {/* Background Pattern */}
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `linear-gradient(rgba(42, 107, 110, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(42, 107, 110, 0.1) 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        />

        {/* Teal Glow */}
        <div className="absolute bottom-0 left-0 w-[80%] h-[80%] bg-gradient-to-tr from-[#2A6B6E]/30 via-[#2A6B6E]/10 to-transparent rounded-full blur-3xl" />

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3">
            <img src={vaiLogo} alt="VoxTest" className="h-10 w-10" />
            <span className="text-xl font-bold text-white">VoxTest</span>
          </Link>

          {/* Center Content - Waveform SVG */}
          <div className="flex-1 flex items-center justify-center">
            <div className="relative">
              {/* Animated Waveform */}
              <svg viewBox="0 0 200 100" className="w-80 h-40 animate-slide-in-left">
                <defs>
                  <linearGradient id="registerWaveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#2A6B6E" />
                    <stop offset="100%" stopColor="#3D8285" />
                  </linearGradient>
                </defs>
                {[20, 35, 55, 75, 90, 100, 90, 75, 55, 35, 20].map((height, i) => (
                  <rect
                    key={i}
                    x={10 + i * 18}
                    y={50 - height / 2}
                    width="8"
                    height={height}
                    rx="4"
                    fill="url(#registerWaveGradient)"
                    className="animate-wave-bar"
                    style={{ animationDelay: `${i * 100}ms`, transformOrigin: `${14 + i * 18}px 50px` }}
                  />
                ))}
              </svg>
            </div>
          </div>

          {/* Feature Highlights */}
          <div className="space-y-4">
            {features.map((feature, index) => (
              <div
                key={feature.text}
                className="flex items-center gap-4 animate-fade-up"
                style={{ animationDelay: `${index * 100 + 300}ms` }}
              >
                <div className="w-10 h-10 rounded-lg bg-[#2A6B6E]/20 flex items-center justify-center">
                  <feature.icon className="w-5 h-5 text-[#3D8285]" />
                </div>
                <span className="text-[var(--color-slate-300)]">{feature.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex flex-col bg-[var(--color-surface-base)]">
        {/* Mobile Nav */}
        <div className="lg:hidden">
          <OuterNav transparent={false} />
        </div>

        {/* Form Container */}
        <div className="flex-1 flex items-center justify-center p-6 lg:p-12 overflow-y-auto">
          <div className="w-full max-w-md animate-slide-in-right">
            {/* Header */}
            <div className="text-center lg:text-left mb-8">
              <h1 className="text-3xl font-bold text-[var(--color-content-primary)] mb-2">
                Create your account
              </h1>
              <p className="text-[var(--color-content-muted)]">
                Start testing your voice AI in minutes
              </p>
            </div>

            {/* Success Alert */}
            {successMessage && (
              <div className="bg-[var(--color-status-emerald-bg)] text-[var(--color-status-emerald)] p-4 rounded-xl mb-6 text-sm border border-[var(--color-status-emerald-bg)] flex items-center gap-3">
                <CheckCircle className="w-5 h-5 flex-shrink-0" />
                {successMessage}
              </div>
            )}

            {/* Error Alert */}
            {error && (
              <div className="bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] p-4 rounded-xl mb-6 text-sm border border-[var(--color-status-danger)]">
                {error}
              </div>
            )}

            {/* Registration Form */}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* Email Field */}
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-semibold text-[var(--color-content-secondary)] mb-2"
                >
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--color-content-muted)]" />
                  <Controller
                    name="email"
                    control={control}
                    render={({ field }) => (
                      <input
                        {...field}
                        type="email"
                        id="email"
                        placeholder="you@company.com"
                        autoComplete="email"
                        autoFocus
                        disabled={loading}
                        className={`
                          w-full pl-12 pr-4 py-3.5 rounded-xl text-sm
                          bg-[var(--color-surface-inset)]
                          border-2 transition-all duration-200
                          text-[var(--color-content-primary)]
                          placeholder:text-[var(--color-content-muted)]
                          focus:outline-none focus:bg-[var(--color-surface-raised)]
                          disabled:opacity-50 disabled:cursor-not-allowed
                          ${errors.email
                            ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-2 focus:ring-[var(--color-status-danger)]/20'
                            : 'border-[var(--color-border-default)] focus:border-[#2A6B6E] focus:ring-2 focus:ring-[#2A6B6E]/20'
                          }
                        `}
                      />
                    )}
                  />
                </div>
                {errors.email && (
                  <p className="text-[var(--color-status-danger)] text-xs mt-2">{errors.email.message}</p>
                )}
              </div>

              {/* Username Field */}
              <div>
                <label
                  htmlFor="username"
                  className="block text-sm font-semibold text-[var(--color-content-secondary)] mb-2"
                >
                  Username
                </label>
                <div className="relative">
                  <AtSign className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--color-content-muted)]" />
                  <Controller
                    name="username"
                    control={control}
                    render={({ field }) => (
                      <input
                        {...field}
                        type="text"
                        id="username"
                        placeholder="Choose a username"
                        autoComplete="username"
                        disabled={loading}
                        className={`
                          w-full pl-12 pr-4 py-3.5 rounded-xl text-sm
                          bg-[var(--color-surface-inset)]
                          border-2 transition-all duration-200
                          text-[var(--color-content-primary)]
                          placeholder:text-[var(--color-content-muted)]
                          focus:outline-none focus:bg-[var(--color-surface-raised)]
                          disabled:opacity-50 disabled:cursor-not-allowed
                          ${errors.username
                            ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-2 focus:ring-[var(--color-status-danger)]/20'
                            : 'border-[var(--color-border-default)] focus:border-[#2A6B6E] focus:ring-2 focus:ring-[#2A6B6E]/20'
                          }
                        `}
                      />
                    )}
                  />
                </div>
                {errors.username && (
                  <p className="text-[var(--color-status-danger)] text-xs mt-2">{errors.username.message}</p>
                )}
              </div>

              {/* Full Name Field */}
              <div>
                <label
                  htmlFor="full_name"
                  className="block text-sm font-semibold text-[var(--color-content-secondary)] mb-2"
                >
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--color-content-muted)]" />
                  <Controller
                    name="full_name"
                    control={control}
                    render={({ field }) => (
                      <input
                        {...field}
                        type="text"
                        id="full_name"
                        placeholder="Your full name"
                        autoComplete="name"
                        disabled={loading}
                        className={`
                          w-full pl-12 pr-4 py-3.5 rounded-xl text-sm
                          bg-[var(--color-surface-inset)]
                          border-2 transition-all duration-200
                          text-[var(--color-content-primary)]
                          placeholder:text-[var(--color-content-muted)]
                          focus:outline-none focus:bg-[var(--color-surface-raised)]
                          disabled:opacity-50 disabled:cursor-not-allowed
                          ${errors.full_name
                            ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-2 focus:ring-[var(--color-status-danger)]/20'
                            : 'border-[var(--color-border-default)] focus:border-[#2A6B6E] focus:ring-2 focus:ring-[#2A6B6E]/20'
                          }
                        `}
                      />
                    )}
                  />
                </div>
                {errors.full_name && (
                  <p className="text-[var(--color-status-danger)] text-xs mt-2">{errors.full_name.message}</p>
                )}
              </div>

              {/* Password Field */}
              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-semibold text-[var(--color-content-secondary)] mb-2"
                >
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--color-content-muted)]" />
                  <Controller
                    name="password"
                    control={control}
                    render={({ field }) => (
                      <input
                        {...field}
                        type={showPassword ? 'text' : 'password'}
                        id="password"
                        placeholder="Create a password"
                        autoComplete="new-password"
                        disabled={loading}
                        className={`
                          w-full pl-12 pr-12 py-3.5 rounded-xl text-sm
                          bg-[var(--color-surface-inset)]
                          border-2 transition-all duration-200
                          text-[var(--color-content-primary)]
                          placeholder:text-[var(--color-content-muted)]
                          focus:outline-none focus:bg-[var(--color-surface-raised)]
                          disabled:opacity-50 disabled:cursor-not-allowed
                          ${errors.password
                            ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-2 focus:ring-[var(--color-status-danger)]/20'
                            : 'border-[var(--color-border-default)] focus:border-[#2A6B6E] focus:ring-2 focus:ring-[#2A6B6E]/20'
                          }
                        `}
                      />
                    )}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)] transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-[var(--color-status-danger)] text-xs mt-2">{errors.password.message}</p>
                )}

                {/* Password Strength Meter */}
                <PasswordStrengthMeter password={password || ''} />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="btn-primary-glow w-full flex items-center justify-center gap-2 !py-4 mt-6"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Creating Account...
                  </>
                ) : (
                  <>
                    Create Account
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="relative my-8">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-[var(--color-border-default)]" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-[var(--color-surface-base)] text-[var(--color-slate-500)]">
                  or continue with
                </span>
              </div>
            </div>

            {/* Social Login */}
            <div className="grid grid-cols-2 gap-4">
              <button className="btn-social">
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="currentColor"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                Google
              </button>
              <button className="btn-social">
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M11.4 24H0V12.6h11.4V24zM24 24H12.6V12.6H24V24zM11.4 11.4H0V0h11.4v11.4zm12.6 0H12.6V0H24v11.4z" />
                </svg>
                Microsoft
              </button>
            </div>

            {/* Login Link */}
            <p className="text-center mt-8 text-[var(--color-content-secondary)]">
              Already have an account?{' '}
              <Link
                to="/login"
                className="font-semibold text-[var(--color-brand-primary)] hover:text-[var(--color-brand-hover)]"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
