/**
 * KPICard Component
 *
 * Displays a KPI (Key Performance Indicator) card with:
 * - Title/label
 * - Large metric value
 * - Trend indicator (optional)
 * - Icon with tinted background
 *
 * Features:
 * - Semantic token-based styling
 * - Theme-aware (light/dark/oled)
 * - Hover lift effect matching outer pages
 * - Responsive layout
 */

import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

type TrendDirection = 'up' | 'down';

interface Trend {
  direction: TrendDirection;
  value: string | number;
}

interface KPICardProps {
  title: string;
  value: string | number;
  trend?: Trend;
  icon: React.ReactElement;
  iconColor?: string;
}

const KPICard: React.FC<KPICardProps> = ({ title, value, trend, icon, iconColor }) => {
  const getTrendColor = (direction: TrendDirection): string => {
    return direction === 'up'
      ? 'text-[var(--color-status-success)]'
      : 'text-[var(--color-status-danger)]';
  };

  const getTrendIcon = (direction: TrendDirection): React.ReactElement => {
    return direction === 'up' ? (
      <TrendingUp className="w-4 h-4" />
    ) : (
      <TrendingDown className="w-4 h-4" />
    );
  };

  return (
    <div className="card group h-full">
      <div className="flex flex-col gap-4">
        {/* Icon and Title Row */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-[var(--color-content-secondary)]">{title}</span>
          <div
            className={`
              w-12 h-12 rounded-xl flex items-center justify-center
              bg-[var(--color-brand-muted)]
              transition-transform duration-300 group-hover:scale-110
              ${iconColor || 'text-[var(--color-brand-primary)]'}
            `}
          >
            {React.cloneElement(icon, { className: 'w-6 h-6' })}
          </div>
        </div>

        {/* Value */}
        <div className="text-4xl font-bold text-[var(--color-content-primary)]">{value}</div>

        {/* Trend Indicator (Optional) */}
        {trend && (
          <div className="flex items-center gap-2">
            <div className={`flex items-center gap-1 ${getTrendColor(trend.direction)}`}>
              {getTrendIcon(trend.direction)}
              <span className="text-sm font-medium">{trend.value}</span>
            </div>
            <span className="text-sm text-[var(--color-content-muted)]">vs last period</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default KPICard;
