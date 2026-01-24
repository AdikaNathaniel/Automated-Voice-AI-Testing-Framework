/**
 * FeatureCard Component
 *
 * Card component for the bento grid features section.
 * Supports different sizes and accent colors.
 */

import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  accent?: 'teal' | 'amber' | 'emerald' | 'purple' | 'rose';
  size?: 'normal' | 'large';
  className?: string;
  delay?: number;
}

const accentColors = {
  teal: {
    bg: 'bg-[var(--color-brand-muted)]',
    text: 'text-[var(--color-brand-primary)]',
    border: 'group-hover:border-[var(--color-brand-primary)]/30',
  },
  amber: {
    bg: 'bg-[var(--color-status-amber-bg)]',
    text: 'text-[var(--color-status-amber)]',
    border: 'group-hover:border-[var(--color-status-amber)]/30',
  },
  emerald: {
    bg: 'bg-[var(--color-status-emerald-bg)]',
    text: 'text-[var(--color-status-emerald)]',
    border: 'group-hover:border-[var(--color-status-emerald)]/30',
  },
  purple: {
    bg: 'bg-[var(--color-status-purple-bg)]',
    text: 'text-[var(--color-status-purple)]',
    border: 'group-hover:border-[var(--color-status-purple)]/30',
  },
  rose: {
    bg: 'bg-[var(--color-status-rose-bg)]',
    text: 'text-[var(--color-status-rose)]',
    border: 'group-hover:border-[var(--color-status-rose)]/30',
  },
};

const FeatureCard: React.FC<FeatureCardProps> = ({
  icon: Icon,
  title,
  description,
  accent = 'teal',
  size = 'normal',
  className = '',
  delay = 0,
}) => {
  const colors = accentColors[accent];

  return (
    <div
      className={`
        group relative bg-[var(--color-surface-raised)]/50
        rounded-2xl border border-[var(--color-border-default)]/50
        p-6 lg:p-8 transition-all duration-300
        hover:shadow-lg hover:shadow-[var(--color-shadow)]/5
        hover:-translate-y-1 ${colors.border}
        animate-fade-up
        ${size === 'large' ? 'md:col-span-2' : ''}
        ${className}
      `}
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Icon */}
      <div
        className={`
          w-12 h-12 rounded-xl ${colors.bg}
          flex items-center justify-center mb-5
          transition-transform duration-300 group-hover:scale-110
        `}
      >
        <Icon className={`w-6 h-6 ${colors.text}`} />
      </div>

      {/* Content */}
      <h3 className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">
        {title}
      </h3>
      <p className="text-sm text-[var(--color-content-secondary)] leading-relaxed">
        {description}
      </p>

      {/* Hover gradient overlay */}
      <div
        className={`
          absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100
          transition-opacity duration-300 pointer-events-none
          bg-gradient-to-br from-white/50 via-transparent to-transparent
          
        `}
      />
    </div>
  );
};

export default FeatureCard;
