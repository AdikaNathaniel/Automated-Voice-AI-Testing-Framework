/**
 * StatCard Component
 *
 * Standardized stat/metric card with icon, value, trend indicator.
 * Uses semantic tokens for consistent theming across light/dark/oled.
 * Supports both horizontal (compact) and vertical layouts.
 */

import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

type TrendDirection = 'up' | 'down' | 'flat';

interface StatCardTrend {
  value: string;
  direction: TrendDirection;
  isPositive: boolean;
}

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  iconColor?: string;
  iconBg?: string;
  trend?: StatCardTrend;
  onClick?: () => void;
  className?: string;
  variant?: 'horizontal' | 'vertical';
  valueColor?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  iconColor,
  iconBg,
  trend,
  onClick,
  className = '',
  variant = 'horizontal',
  valueColor,
}) => {
  const getTrendIcon = () => {
    if (!trend) return null;
    if (trend.direction === 'up') return <TrendingUp className="w-4 h-4" />;
    if (trend.direction === 'down') return <TrendingDown className="w-4 h-4" />;
    return <Minus className="w-4 h-4" />;
  };

  const getTrendColor = () => {
    if (!trend || trend.direction === 'flat') {
      return 'text-[var(--color-content-muted)]';
    }
    return trend.isPositive
      ? 'text-[var(--color-status-success)]'
      : 'text-[var(--color-status-danger)]';
  };

  const CardWrapper = onClick ? 'button' : 'div';

  // Horizontal layout (compact, icon + content side by side)
  if (variant === 'horizontal') {
    return (
      <CardWrapper
        className={`card-compact flex items-center gap-4 text-left w-full ${onClick ? 'cursor-pointer' : ''} ${className}`}
        onClick={onClick}
        {...(onClick ? { type: 'button' as const } : {})}
      >
        <div
          className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${iconBg || 'bg-[var(--color-brand-muted)]'}`}
        >
          <div className={iconColor || 'text-[var(--color-brand-primary)]'}>{icon}</div>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <p className={`text-2xl font-bold ${valueColor || 'text-[var(--color-content-primary)]'}`}>
              {value}
            </p>
            {trend && (
              <div className={`flex items-center gap-0.5 text-xs ${getTrendColor()}`}>
                {getTrendIcon()}
                <span>{trend.value}</span>
              </div>
            )}
          </div>
          <p className="text-sm text-[var(--color-content-secondary)]">{title}</p>
          {subtitle && (
            <p className="text-xs text-[var(--color-content-muted)] mt-0.5">{subtitle}</p>
          )}
        </div>
      </CardWrapper>
    );
  }

  // Vertical layout (stacked, icon on top)
  return (
    <CardWrapper
      className={`card-compact ${onClick ? 'cursor-pointer' : ''} ${className}`}
      onClick={onClick}
      {...(onClick ? { type: 'button' as const } : {})}
    >
      <div className="flex items-center justify-between mb-3">
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center ${iconBg || 'bg-[var(--color-brand-muted)]'}`}
        >
          <div className={iconColor || 'text-[var(--color-brand-primary)]'}>{icon}</div>
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-sm ${getTrendColor()}`}>
            {getTrendIcon()}
            <span>{trend.value}</span>
          </div>
        )}
      </div>
      <p className="text-sm text-[var(--color-content-secondary)] mb-1">{title}</p>
      <h3 className={`text-3xl font-bold ${valueColor || 'text-[var(--color-content-primary)]'}`}>
        {value}
      </h3>
      {subtitle && (
        <p className="text-xs text-[var(--color-content-muted)] mt-1">{subtitle}</p>
      )}
    </CardWrapper>
  );
};

export default StatCard;
