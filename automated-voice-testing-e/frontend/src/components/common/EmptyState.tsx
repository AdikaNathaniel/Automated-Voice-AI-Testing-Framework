/**
 * EmptyState Component
 *
 * Standardized empty state display with icon, title, description, and optional action.
 * Uses semantic tokens for consistent theming across light/dark/oled.
 */

import React from 'react';
import {
  Inbox,
  FileText,
  Search,
  Folder,
  Users,
  AlertCircle,
  Database,
  Calendar,
  type LucideIcon,
} from 'lucide-react';

type EmptyStateVariant = 'card' | 'inline';
type EmptyStateIcon =
  | 'inbox'
  | 'file'
  | 'search'
  | 'folder'
  | 'users'
  | 'alert'
  | 'database'
  | 'calendar';

const iconMap: Record<EmptyStateIcon, LucideIcon> = {
  inbox: Inbox,
  file: FileText,
  search: Search,
  folder: Folder,
  users: Users,
  alert: AlertCircle,
  database: Database,
  calendar: Calendar,
};

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: EmptyStateIcon | React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
  variant?: EmptyStateVariant;
  className?: string;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon = 'inbox',
  action,
  variant = 'card',
  className = '',
}) => {
  const renderIcon = () => {
    if (React.isValidElement(icon)) {
      return icon;
    }

    const IconComponent = iconMap[icon as EmptyStateIcon] || Inbox;
    return (
      <div
        className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6"
        style={{ background: 'var(--color-surface-inset)' }}
      >
        <IconComponent
          className="w-8 h-8 text-[var(--color-content-muted)]"
          aria-hidden="true"
        />
      </div>
    );
  };

  const content = (
    <div className="flex flex-col items-center text-center">
      {renderIcon()}
      <h3 className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">
        {title}
      </h3>
      {description && (
        <p className="text-sm text-[var(--color-content-secondary)] max-w-sm mb-6">
          {description}
        </p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          className="btn-primary"
        >
          {action.label}
        </button>
      )}
    </div>
  );

  if (variant === 'inline') {
    return <div className={`py-8 ${className}`}>{content}</div>;
  }

  // variant === 'card'
  return (
    <div className={`card-static ${className}`}>
      <div className="flex flex-col items-center justify-center py-12">
        {content}
      </div>
    </div>
  );
};

export default EmptyState;
