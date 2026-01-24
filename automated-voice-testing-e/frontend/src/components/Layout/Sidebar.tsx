/**
 * Sidebar Component
 *
 * Navigation sidebar with menu items:
 * - Dashboard
 * - Scenarios
 * - Executions
 * - Test Suites
 * - Suite Runs
 * - Integrations (org_admin only)
 * - CI/CD (org_admin only)
 * - Configurations (org_admin only)
 *
 * Note: LLM Providers is currently hidden
 *
 * Features:
 * - Tailwind CSS styling
 * - React Router navigation
 * - Active state highlighting
 * - Icons for each menu item
 * - Role-based menu item visibility
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store';
import {
  LayoutDashboard,
  FileText,
  Play,
  Blocks,
  Settings as SettingsIcon,
  Layers,
  Bot,
  PlayCircle,
  GitBranch,
} from 'lucide-react';

/**
 * Menu item interface
 */
interface MenuItem {
  /**
   * Display label for menu item
   */
  label: string;

  /**
   * Navigation path
   */
  path: string;

  /**
   * Icon component
   */
  icon: React.ReactElement;

  /**
   * Optional role required to see this menu item
   */
  requiredRole?: string;
}

/**
 * Menu items configuration
 */
const menuItems: MenuItem[] = [
  {
    label: 'Dashboard',
    path: '/',
    icon: <LayoutDashboard className="w-5 h-5" />,
  },
  {
    label: 'Scenarios',
    path: '/scenarios',
    icon: <FileText className="w-5 h-5" />,
  },
  {
    label: 'Executions',
    path: '/executions',
    icon: <Play className="w-5 h-5" />,
  },
  {
    label: 'Test Suites',
    path: '/test-suites',
    icon: <Layers className="w-5 h-5" />,
  },
  {
    label: 'Suite Runs',
    path: '/suite-runs',
    icon: <PlayCircle className="w-5 h-5" />,
  },
  {
    label: 'Integrations',
    path: '/integrations',
    icon: <Blocks className="w-5 h-5" />,
    requiredRole: 'org_admin',
  },
  {
    label: 'CI/CD',
    path: '/cicd-config',
    icon: <GitBranch className="w-5 h-5" />,
    requiredRole: 'org_admin',
  },
  // LLM Providers - Hidden for now
  // {
  //   label: 'LLM Providers',
  //   path: '/admin/llm-providers',
  //   icon: <Bot className="w-5 h-5" />,
  //   requiredRole: 'admin',
  // },
  {
    label: 'Configurations',
    path: '/configurations',
    icon: <SettingsIcon className="w-5 h-5" />,
    requiredRole: 'org_admin',
  },
];

/**
 * Sidebar component
 *
 * Provides navigation menu with active state highlighting.
 * Uses React Router for navigation and Tailwind CSS for styling.
 *
 * @returns Navigation sidebar with menu items
 *
 * @example
 * ```tsx
 * <Sidebar />
 * ```
 */
const Sidebar: React.FC = () => {
  // Get current location for active state
  const location = useLocation();

  // Get user role from Redux store
  const { user } = useSelector((state: RootState) => state.auth);
  const userRole = user?.role;

  // Filter menu items based on user role
  const visibleMenuItems = menuItems.filter((item) => {
    if (!item.requiredRole) return true;
    return userRole === item.requiredRole;
  });

  /**
   * Check if menu item is active based on current path
   *
   * @param path - Menu item path
   * @returns True if menu item matches current path
   */
  const isActive = (path: string): boolean => {
    // Exact match for root path
    if (path === '/') {
      return location.pathname === '/';
    }
    // Starts with for other paths
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="flex flex-col p-3 gap-1">
      {visibleMenuItems.map((item) => (
        <Link
          key={item.path}
          to={item.path}
          className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors text-sm ${
            isActive(item.path)
              ? 'bg-[var(--color-brand-muted)] text-[var(--color-brand-primary)] font-medium'
              : 'text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]'
          }`}
          aria-current={isActive(item.path) ? 'page' : undefined}
        >
          <span className={isActive(item.path) ? 'text-[var(--color-brand-primary)]' : 'text-[var(--color-content-muted)]'}>
            {item.icon}
          </span>
          <span>{item.label}</span>
        </Link>
      ))}
    </nav>
  );
};

export default Sidebar;
