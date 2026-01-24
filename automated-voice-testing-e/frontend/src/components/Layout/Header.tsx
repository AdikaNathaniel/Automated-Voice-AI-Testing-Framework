/**
 * Header Component (TASK-129)
 *
 * Application header with:
 * - Logo/app title
 * - User menu button
 * - Notifications icon with badge
 *
 * Features:
 * - Custom nav-container class with Tailwind
 * - Account icon for user menu
 * - Notifications badge for unread count
 * - Responsive design
 */

import React from 'react';
import { Bell, User } from 'lucide-react';

/**
 * Header component
 *
 * Displays the application header with logo, notifications, and user menu.
 * Uses Tailwind CSS for styling and responsive behavior.
 *
 * @returns Application header with logo and menu items
 *
 * @example
 * ```tsx
 * <Header />
 * ```
 */
const Header: React.FC = () => {
  return (
    <header className="nav-container fixed top-0 left-0 right-0 z-50 bg-[var(--color-surface-raised)] shadow-sm">
      <div className="flex items-center justify-between h-16 px-4">
        {/* App Logo/Title */}
        <h1 className="nav-brand text-xl font-semibold text-[var(--color-content-primary)]">
          Voice AI Testing
        </h1>

        <div className="flex items-center gap-4">
          {/* Notifications Icon with Badge */}
          <button
            className="relative p-2 rounded-lg hover:bg-[var(--color-interactive-hover)] transition-colors"
            aria-label="Show notifications"
          >
            <div className="badge absolute -top-1 -right-1 bg-[var(--color-status-danger)] text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              4
            </div>
            <Bell className="w-6 h-6 text-[var(--color-content-secondary)]" />
          </button>

          {/* User Menu Icon */}
          <button
            className="p-2 rounded-lg hover:bg-[var(--color-interactive-hover)] transition-colors"
            aria-label="User account menu"
          >
            <User className="w-6 h-6 text-[var(--color-content-secondary)]" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
