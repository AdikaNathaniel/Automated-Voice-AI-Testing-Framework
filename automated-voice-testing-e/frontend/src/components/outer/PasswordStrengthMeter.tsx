/**
 * PasswordStrengthMeter Component
 *
 * Enhanced password strength visualization with checklist.
 * Shows strength bar, label, and animated requirement checklist.
 */

import React, { useMemo } from 'react';
import { Check, X } from 'lucide-react';

interface PasswordCheck {
  label: string;
  passed: boolean;
}

interface StrengthResult {
  score: number;
  label: string;
  color: string;
  bgColor: string;
  checks: PasswordCheck[];
}

const calculateStrength = (password: string): StrengthResult => {
  const checks: PasswordCheck[] = [
    { label: '8+ characters', passed: password.length >= 8 },
    { label: 'Uppercase letter', passed: /[A-Z]/.test(password) },
    { label: 'Lowercase letter', passed: /[a-z]/.test(password) },
    { label: 'Number', passed: /[0-9]/.test(password) },
    { label: 'Special character', passed: /[^a-zA-Z0-9]/.test(password) },
  ];

  const passedCount = checks.filter((c) => c.passed).length;

  if (passedCount <= 1) {
    return {
      score: 20,
      label: 'Weak',
      color: 'text-[var(--color-status-danger)]',
      bgColor: 'bg-[var(--color-status-danger)]',
      checks,
    };
  } else if (passedCount === 2) {
    return {
      score: 40,
      label: 'Fair',
      color: 'text-[var(--color-status-amber)]',
      bgColor: 'bg-[var(--color-status-amber)]',
      checks,
    };
  } else if (passedCount === 3) {
    return {
      score: 60,
      label: 'Good',
      color: 'text-[var(--color-status-info)]',
      bgColor: 'bg-[var(--color-status-info)]',
      checks,
    };
  } else if (passedCount === 4) {
    return {
      score: 80,
      label: 'Strong',
      color: 'text-[var(--color-status-emerald)]',
      bgColor: 'bg-[var(--color-status-emerald)]',
      checks,
    };
  } else {
    return {
      score: 100,
      label: 'Very Strong',
      color: 'text-[var(--color-status-emerald)]',
      bgColor: 'bg-[var(--color-status-emerald)]',
      checks,
    };
  }
};

interface PasswordStrengthMeterProps {
  password: string;
  showChecklist?: boolean;
  className?: string;
}

const PasswordStrengthMeter: React.FC<PasswordStrengthMeterProps> = ({
  password,
  showChecklist = true,
  className = '',
}) => {
  const strength = useMemo(() => calculateStrength(password), [password]);

  if (!password) {
    return null;
  }

  return (
    <div className={`mt-3 ${className}`}>
      {/* Strength Bar */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-[var(--color-content-muted)]">
          Password Strength
        </span>
        <span className={`text-xs font-semibold ${strength.color}`}>
          {strength.label}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="h-1.5 bg-[var(--color-surface-inset)] rounded-full overflow-hidden">
        <div
          className={`h-full ${strength.bgColor} transition-all duration-500 ease-out rounded-full`}
          style={{ width: `${strength.score}%` }}
        />
      </div>

      {/* Checklist */}
      {showChecklist && (
        <div className="mt-4 grid grid-cols-2 gap-2">
          {strength.checks.map((check, index) => (
            <div
              key={check.label}
              className={`
                flex items-center gap-2 text-xs transition-all duration-300
                ${check.passed
                  ? 'text-[var(--color-status-emerald)]'
                  : 'text-[var(--color-content-muted)]'
                }
              `}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div
                className={`
                  w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0
                  transition-all duration-300
                  ${check.passed
                    ? 'bg-[var(--color-status-emerald)] text-white scale-100'
                    : 'bg-[var(--color-surface-inset)] scale-90'
                  }
                `}
              >
                {check.passed ? (
                  <Check className="w-2.5 h-2.5" strokeWidth={3} />
                ) : (
                  <X className="w-2.5 h-2.5 text-[var(--color-content-muted)]" strokeWidth={2} />
                )}
              </div>
              <span className="leading-none">{check.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PasswordStrengthMeter;
