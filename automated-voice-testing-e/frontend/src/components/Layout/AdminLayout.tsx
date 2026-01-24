/**
 * AdminLayout Component - Super Admin Console Layout
 *
 * A separate layout for the super admin console with its own navigation.
 * Maintains the same design language as AppLayout but with admin-specific features.
 */

import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import { useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Menu as MenuIcon,
  LayoutDashboard,
  Building2,
  Users,
  Tag,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  LogOut,
  X,
  PanelLeftClose,
  PanelLeft,
  Sun,
  Moon,
  Shield,
  Cpu,
  Settings,
} from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import type { AppDispatch, RootState } from '../../store';
import { logout } from '../../store/slices/authSlice';

const SIDEBAR_WIDTH = 260;
const SIDEBAR_COLLAPSED_WIDTH = 72;

interface NavigationItem {
  title: string;
  path: string;
  icon: React.ReactNode;
  badge?: string | number;
}

const navigationItems: NavigationItem[] = [
  {
    title: 'Dashboard',
    path: '/admin',
    icon: <LayoutDashboard className="w-5 h-5" />,
  },
  {
    title: 'Organizations',
    path: '/admin/organizations',
    icon: <Building2 className="w-5 h-5" />,
  },
  {
    title: 'Users',
    path: '/admin/users',
    icon: <Users className="w-5 h-5" />,
  },
  {
    title: 'Categories',
    path: '/admin/categories',
    icon: <Tag className="w-5 h-5" />,
  },
  {
    title: 'Configurations',
    path: '/admin/configurations',
    icon: <Settings className="w-5 h-5" />,
  },
  // LLM Providers - Hidden for now
  // {
  //   title: 'LLM Providers',
  //   path: '/admin/llm-providers',
  //   icon: <Cpu className="w-5 h-5" />,
  // },
];

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  visible: boolean;
}

const Tooltip: React.FC<TooltipProps> = ({ content, children, visible }) => {
  const [show, setShow] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ top: 0, left: 0 });

  useEffect(() => {
    if (show && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setPosition({
        top: rect.top + rect.height / 2,
        left: rect.right + 12,
      });
    }
  }, [show]);

  if (!visible) return <>{children}</>;

  const tooltipContent = show ? (
    <div
      className="fixed px-3 py-1.5 bg-[var(--color-surface-overlay)] text-[var(--color-content-primary)] text-sm rounded-lg shadow-lg pointer-events-none whitespace-nowrap border border-[var(--color-border-default)]"
      style={{
        top: `${position.top}px`,
        left: `${position.left}px`,
        transform: 'translateY(-50%)',
        zIndex: 999999,
      }}
    >
      {content}
      <div
        className="absolute bg-[var(--color-surface-overlay)]"
        style={{
          right: '100%',
          top: '50%',
          transform: 'translateY(-50%) rotate(45deg)',
          width: '8px',
          height: '8px',
          marginRight: '-4px',
        }}
      />
    </div>
  ) : null;

  return (
    <>
      <div
        ref={containerRef}
        className="relative"
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
      >
        {children}
      </div>
      {tooltipContent && ReactDOM.createPortal(tooltipContent, document.body)}
    </>
  );
};

interface AdminLayoutProps {
  children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch<AppDispatch>();
  const { isDark, toggleTheme } = useTheme();

  const user = useSelector((state: RootState) => state.auth.user);

  const [isMobile, setIsMobile] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 1024;
      setIsMobile(mobile);
      if (mobile) {
        setIsCollapsed(false);
      }
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleDrawerToggle = () => {
    if (isMobile) {
      setMobileOpen(!mobileOpen);
    } else {
      setIsCollapsed(!isCollapsed);
    }
  };

  const handleLogout = () => {
    dispatch(logout());
    setUserMenuOpen(false);
    navigate('/login');
  };

  const handleNavigate = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const isActiveRoute = (path: string) => {
    if (path === '/admin') {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  const sidebarWidth = isCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH;

  const renderNavItem = (item: NavigationItem) => {
    const isActive = isActiveRoute(item.path);

    return (
      <Tooltip key={item.title} content={item.title} visible={isCollapsed && !isMobile}>
        <button
          onClick={() => handleNavigate(item.path)}
          className={`
            group flex items-center w-full rounded-xl transition-all duration-200
            ${isCollapsed && !isMobile ? 'justify-center px-3 py-3' : 'px-3 py-2.5'}
            ${isActive
              ? 'bg-gradient-to-r from-[var(--color-status-purple-bg)] to-[var(--color-status-purple-bg)] text-[var(--color-status-purple)]'
              : 'text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] hover:text-[var(--color-content-primary)]'
            }
          `}
          aria-current={isActive ? 'page' : undefined}
        >
          <span className={`
            flex items-center justify-center flex-shrink-0 transition-colors
            ${isActive ? 'text-[var(--color-status-purple)]' : 'text-[var(--color-content-muted)] group-hover:text-[var(--color-content-secondary)]'}
          `}>
            {item.icon}
          </span>
          {(!isCollapsed || isMobile) && (
            <span className={`ml-3 text-sm font-medium truncate ${isActive ? 'text-[var(--color-status-purple)]' : ''}`}>
              {item.title}
            </span>
          )}
          {item.badge && (!isCollapsed || isMobile) && (
            <span className="ml-auto px-2 py-0.5 text-xs font-semibold rounded-full bg-[var(--color-status-purple-bg)] text-[var(--color-status-purple)]">
              {item.badge}
            </span>
          )}
        </button>
      </Tooltip>
    );
  };

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Logo Section */}
      <div className={`
        flex items-center h-16 border-b border-[var(--color-border-subtle)]
        ${isCollapsed && !isMobile ? 'justify-center px-3' : 'px-5'}
      `}>
        {isCollapsed && !isMobile ? (
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-purple-800 flex items-center justify-center shadow-lg shadow-purple-500/20">
            <Shield className="w-5 h-5 text-white" />
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-purple-800 flex items-center justify-center shadow-lg shadow-purple-500/20">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-[var(--color-content-primary)]">Admin Console</h1>
              <p className="text-[10px] text-[var(--color-content-muted)] font-medium">Super Admin</p>
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3">
        <div className="space-y-1">
          {navigationItems.map(renderNavItem)}
        </div>
      </nav>

      {/* Collapse Toggle (Desktop only) */}
      {!isMobile && (
        <div className="p-3 border-t border-[var(--color-border-subtle)]">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className={`
              flex items-center w-full rounded-xl py-2.5 text-[var(--color-content-muted)] hover:bg-[var(--color-interactive-hover)] hover:text-[var(--color-content-primary)] transition-all
              ${isCollapsed ? 'justify-center px-3' : 'px-3'}
            `}
          >
            {isCollapsed ? (
              <ChevronRight className="w-5 h-5" />
            ) : (
              <>
                <ChevronLeft className="w-5 h-5" />
                <span className="ml-3 text-sm font-medium">Collapse</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );

  return (
    <div className="flex min-h-screen bg-[var(--color-surface-inset)] text-[var(--color-content-primary)]">
      {/* Mobile Overlay */}
      {isMobile && mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 backdrop-blur-sm"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-full bg-[var(--color-surface-raised)] border-r border-[var(--color-border-subtle)] z-50
          transition-all duration-300 ease-in-out
          ${isMobile
            ? mobileOpen ? 'translate-x-0' : '-translate-x-full'
            : 'translate-x-0'
          }
        `}
        style={{ width: isMobile ? SIDEBAR_WIDTH : sidebarWidth }}
      >
        {/* Mobile Close Button */}
        {isMobile && (
          <button
            onClick={() => setMobileOpen(false)}
            className="absolute top-4 right-4 p-2 text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] rounded-lg z-10"
          >
            <X className="w-5 h-5" />
          </button>
        )}
        {sidebarContent}
      </aside>

      {/* Main Content Area */}
      <div
        className="flex-1 flex flex-col transition-all duration-300"
        style={{ marginLeft: isMobile ? 0 : sidebarWidth }}
      >
        {/* Top Navigation Bar */}
        <header className="sticky top-0 z-30 bg-[var(--color-surface-raised)]/80 backdrop-blur-md border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center justify-between h-16 px-4 lg:px-6">
            {/* Left Section */}
            <div className="flex items-center gap-3">
              {/* Sidebar Toggle - Desktop */}
              {!isMobile && (
                <button
                  onClick={() => setIsCollapsed(!isCollapsed)}
                  className="p-2 text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)] hover:bg-[var(--color-interactive-hover)] rounded-xl transition-colors"
                  title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                >
                  {isCollapsed ? <PanelLeft className="w-5 h-5" /> : <PanelLeftClose className="w-5 h-5" />}
                </button>
              )}

              {/* Mobile Menu Toggle */}
              {isMobile && (
                <button
                  onClick={handleDrawerToggle}
                  className="p-2 text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)] hover:bg-[var(--color-interactive-hover)] rounded-xl transition-colors"
                >
                  <MenuIcon className="w-5 h-5" />
                </button>
              )}

              {/* Admin Badge */}
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-[var(--color-status-purple-bg)] text-[var(--color-status-purple)]">
                  Super Admin
                </span>
                <span className="hidden md:block text-sm font-medium text-[var(--color-content-primary)]">
                  {navigationItems.find(item => isActiveRoute(item.path))?.title || 'Dashboard'}
                </span>
              </div>
            </div>

            {/* Right Section */}
            <div className="flex items-center gap-2">
              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2.5 text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)] hover:bg-[var(--color-interactive-hover)] rounded-xl transition-colors"
                title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>

              {/* User Menu */}
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 p-1.5 hover:bg-[var(--color-interactive-hover)] rounded-xl transition-colors"
                >
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-600 to-purple-800 flex items-center justify-center text-white font-semibold text-sm">
                    {user?.email?.[0]?.toUpperCase() || 'A'}
                  </div>
                  <ChevronDown className={`w-4 h-4 text-[var(--color-content-muted)] transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
                </button>

                {/* Dropdown */}
                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-[var(--color-surface-raised)] rounded-xl shadow-xl border border-[var(--color-border-subtle)] py-2 z-50">
                    <div className="px-4 py-3 border-b border-[var(--color-border-subtle)]">
                      <p className="text-sm font-semibold text-[var(--color-content-primary)]">
                        {user?.email?.split('@')[0] || 'Admin'}
                      </p>
                      <p className="text-xs text-[var(--color-content-muted)] mt-0.5">
                        {user?.email || 'admin@example.com'}
                      </p>
                    </div>
                    <div className="py-1">
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-[var(--color-status-danger)] hover:bg-[var(--color-status-danger-bg)] transition-colors"
                      >
                        <LogOut className="w-4 h-4" />
                        Sign out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-4 lg:p-6">
          {children}
        </main>

        {/* Footer */}
        <footer className="py-4 px-6 border-t border-[var(--color-border-subtle)] bg-[var(--color-surface-raised)]">
          <div className="flex items-center justify-between text-xs text-[var(--color-content-muted)]">
            <span>Admin Console v1.0.0</span>
            <span>Super Admin Access</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
