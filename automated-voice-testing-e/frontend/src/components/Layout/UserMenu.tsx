/**
 * UserMenu Component (TASK-130)
 *
 * User menu dropdown with options:
 * - Profile
 * - Settings
 * - Logout
 *
 * Features:
 * - Custom dropdown using Tailwind CSS
 * - Icons for each menu item
 * - Click handlers for navigation
 * - Divider to separate logout option
 */

import React from 'react';
import { User, Settings as SettingsIcon, LogOut } from 'lucide-react';

/**
 * Props interface for UserMenu component
 */
interface UserMenuProps {
  /**
   * Whether the menu is open
   */
  open: boolean;

  /**
   * Handler for closing the menu
   */
  onClose: () => void;
}

/**
 * UserMenu component
 *
 * Displays a dropdown menu with user-related options.
 * Positioned relative to a button element (typically user icon in header).
 *
 * @param props - Component props
 * @returns User menu dropdown with options
 *
 * @example
 * ```tsx
 * const [menuOpen, setMenuOpen] = useState(false);
 *
 * <button onClick={() => setMenuOpen(true)}>
 *   <User />
 * </button>
 * <UserMenu
 *   open={menuOpen}
 *   onClose={() => setMenuOpen(false)}
 * />
 * ```
 */
const UserMenu: React.FC<UserMenuProps> = ({ open, onClose }) => {
  /**
   * Handle profile menu item click
   */
  const handleProfileClick = () => {
    onClose();
    // TODO: Navigate to profile page
    console.log('Navigate to profile');
  };

  /**
   * Handle settings menu item click
   */
  const handleSettingsClick = () => {
    onClose();
    // TODO: Navigate to settings page
    console.log('Navigate to settings');
  };

  /**
   * Handle logout menu item click
   */
  const handleLogoutClick = () => {
    onClose();
    // TODO: Implement logout logic
    console.log('Logout');
  };

  if (!open) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 z-40"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Menu Dropdown */}
      <div className="absolute right-0 mt-2 w-48 bg-[var(--color-surface-overlay)] rounded-lg shadow-lg border border-[var(--color-border-default)] py-1 z-50">
        <button
          onClick={handleProfileClick}
          className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] transition-colors"
        >
          <User className="w-4 h-4" />
          <span>Profile</span>
        </button>

        <button
          onClick={handleSettingsClick}
          className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] transition-colors"
        >
          <SettingsIcon className="w-4 h-4" />
          <span>Settings</span>
        </button>

        <hr className="my-1 border-[var(--color-border-default)]" />

        <button
          onClick={handleLogoutClick}
          className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Logout</span>
        </button>
      </div>
    </>
  );
};

export default UserMenu;
