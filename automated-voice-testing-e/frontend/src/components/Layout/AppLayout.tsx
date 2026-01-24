/**
 * AppLayout Component - Modern Navigation System
 *
 * Features:
 * - Collapsible sidebar with mini mode (icons only)
 * - Tooltips on hover when collapsed
 * - Dark sidebar (slate-900) with teal accents
 * - Slate neutral backgrounds matching external pages
 * - Responsive design with mobile drawer
 * - Smooth animations
 * - Organized navigation groups
 * - Light/dark mode support
 */

import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import { useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Menu as MenuIcon,
  LayoutDashboard,
  Play,
  Bug,
  User,
  ChevronDown,
  Settings,
  Blocks,
  BookOpen,
  TrendingUp,
  CheckCircle,
  GitCompare,
  GitBranch,
  FileBarChart,
  AlertTriangle,
  MessageSquare,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Bell,
  Search,
  X,
  Layers,
  PlayCircle,
  PanelLeftClose,
  PanelLeft,
  Sun,
  Moon,
} from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import type { AppDispatch, RootState } from '../../store';
import { logout } from '../../store/slices/authSlice';
import vaiLogo from '../../assets/vai-logo.png';

const SIDEBAR_WIDTH = 260;
const SIDEBAR_COLLAPSED_WIDTH = 72;

interface NavigationItem {
  title: string;
  path?: string;
  icon: React.ReactNode;
  children?: NavigationItem[];
  badge?: string | number;
  requiredRole?: string;
}

interface NavigationGroup {
  title: string;
  items: NavigationItem[];
}

const navigationGroups: NavigationGroup[] = [
  {
    title: 'Overview',
    items: [
      {
        title: 'Dashboard',
        path: '/dashboard',
        icon: <LayoutDashboard className="w-5 h-5" />,
      },
      {
        title: 'Analytics',
        path: '/analytics',
        icon: <TrendingUp className="w-5 h-5" />,
      },
    ],
  },
  {
    title: 'Testing',
    items: [
      {
        title: 'Scenarios',
        path: '/scenarios',
        icon: <MessageSquare className="w-5 h-5" />,
      },
      {
        title: 'Test Suites',
        path: '/test-suites',
        icon: <Layers className="w-5 h-5" />,
      },
      {
        title: 'Suite Runs',
        path: '/suite-runs',
        icon: <PlayCircle className="w-5 h-5" />,
      },
      {
        title: 'Executions',
        path: '/executions',
        icon: <Play className="w-5 h-5" />,
      },
    ],
  },
  {
    title: 'Validation',
    items: [
      {
        title: 'Validation Queue',
        path: '/validation',
        icon: <CheckCircle className="w-5 h-5" />,
      },
    ],
  },
  {
    title: 'Quality',
    items: [
      {
        title: 'Defects',
        path: '/defects',
        icon: <Bug className="w-5 h-5" />,
      },
      {
        title: 'Edge Cases',
        path: '/edge-cases',
        icon: <AlertTriangle className="w-5 h-5" />,
      },
      {
        title: 'Regressions',
        path: '/regressions',
        icon: <GitCompare className="w-5 h-5" />,
      },
    ],
  },
  {
    title: 'Tools',
    items: [
      {
        title: 'Reports',
        path: '/reports',
        icon: <FileBarChart className="w-5 h-5" />,
      },
      {
        title: 'Knowledge Base',
        path: '/knowledge-base',
        icon: <BookOpen className="w-5 h-5" />,
      },
    ],
  },
  {
    title: 'Settings',
    items: [
      {
        title: 'Integrations',
        path: '/integrations',
        icon: <Blocks className="w-5 h-5" />,
      },
      {
        title: 'CI/CD',
        path: '/cicd',
        icon: <GitBranch className="w-5 h-5" />,
        requiredRole: 'org_admin',
      },
    ],
  },
];

// Configurations nav item - Only visible to ORG_ADMIN users
const configurationsNavGroup: NavigationGroup = {
  title: 'Admin',
  items: [
    {
      title: 'Configurations',
      path: '/configurations',
      icon: <Settings className="w-5 h-5" />,
    },
  ],
};

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
        left: rect.right + 12, // 12px to the right
      });
    }
  }, [show]);

  if (!visible) return <>{children}</>;

  const tooltipContent = show ? (
    <div
      className="fixed px-3 py-1.5 bg-[var(--color-slate-900)] text-white text-sm rounded-lg shadow-lg pointer-events-none whitespace-nowrap"
      style={{
        top: `${position.top}px`,
        left: `${position.left}px`,
        transform: 'translateY(-50%)',
        zIndex: 999999,
      }}
    >
      {content}
      <div
        className="absolute bg-[var(--color-slate-900)]"
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

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch<AppDispatch>();
  const { isDark, toggleTheme } = useTheme();

  const user = useSelector((state: RootState) => state.auth.user);
  const isOrgAdmin = user?.role === 'org_admin';

  // Conditionally add Configurations nav for ORG_ADMIN users
  const allNavigationGroups = isOrgAdmin
    ? [...navigationGroups, configurationsNavGroup]
    : navigationGroups;

  const [isMobile, setIsMobile] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Handle responsive breakpoint
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

  // Close user menu on click outside
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

  const isActiveRoute = (path?: string) => {
    if (!path) return false;
    if (path === '/dashboard') {
      return location.pathname === path || location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const sidebarWidth = isCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH;

  const renderNavItem = (item: NavigationItem) => {
    const isActive = isActiveRoute(item.path);

    return (
      <Tooltip key={item.title} content={item.title} visible={isCollapsed && !isMobile}>
        <button
          onClick={() => item.path && handleNavigate(item.path)}
          className={`
            group flex items-center w-full rounded-xl transition-all duration-200
            ${isCollapsed && !isMobile ? 'justify-center px-3 py-3' : 'px-3 py-2.5'}
            ${isActive
              ? 'bg-[#2A6B6E]/20 text-[#3D8285]'
              : 'text-[var(--color-content-muted)] hover:bg-[var(--color-slate-800)] hover:text-white'
            }
          `}
          aria-current={isActive ? 'page' : undefined}
        >
          <span className={`
            flex items-center justify-center flex-shrink-0 transition-colors
            ${isActive ? 'text-[#3D8285]' : 'text-[var(--color-slate-500)] group-hover:text-[var(--color-slate-300)]'}
          `}>
            {item.icon}
          </span>
          {(!isCollapsed || isMobile) && (
            <span className={`ml-3 text-sm font-medium truncate ${isActive ? 'text-[#3D8285]' : ''}`}>
              {item.title}
            </span>
          )}
          {item.badge && (!isCollapsed || isMobile) && (
            <span className="ml-auto px-2 py-0.5 text-xs font-semibold rounded-full bg-[#2A6B6E]/20 text-[#3D8285]">
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
        flex items-center h-16 border-b border-[var(--color-slate-800)]
        ${isCollapsed && !isMobile ? 'justify-center px-3' : 'px-5'}
      `}>
        {isCollapsed && !isMobile ? (
          <div className="w-10 h-10 flex items-center justify-center">
            <img src={vaiLogo} alt="VAI Logo" className="w-10 h-10 object-contain" />
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 flex items-center justify-center">
              <img src={vaiLogo} alt="VAI Logo" className="w-10 h-10 object-contain" />
            </div>
            <div className="flex flex-col">
              <h1 className="text-sm font-bold text-white tracking-tight">
                VoxTest
              </h1>
              <p className="text-[10px] text-[var(--color-content-muted)] font-medium tracking-wide">
                Voice AI Testing
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3">
        {allNavigationGroups.map((group, groupIndex) => (
          <div key={group.title} className={groupIndex > 0 ? 'mt-6' : ''}>
            {(!isCollapsed || isMobile) && (
              <h3 className="px-3 mb-2 text-[10px] font-semibold text-[var(--color-slate-500)] uppercase tracking-wider">
                {group.title}
              </h3>
            )}
            {isCollapsed && !isMobile && groupIndex > 0 && (
              <div className="mx-3 mb-3 border-t border-[var(--color-slate-800)]" />
            )}
            <div className="space-y-1">
              {group.items.map(renderNavItem)}
            </div>
          </div>
        ))}
      </nav>

      {/* Collapse Toggle (Desktop only) */}
      {!isMobile && (
        <div className="p-3 border-t border-[var(--color-slate-800)]">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className={`
              flex items-center w-full rounded-xl py-2.5 text-[var(--color-content-muted)] hover:bg-[var(--color-slate-800)] hover:text-white transition-all
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
    <div className="flex min-h-screen bg-[var(--color-surface-base)] text-[var(--color-content-primary)]">
      {/* Mobile Overlay */}
      {isMobile && mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 backdrop-blur-sm"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar - Always dark theme */}
      <aside
        className={`
          fixed top-0 left-0 h-full bg-[var(--color-slate-900)] border-r border-[var(--color-slate-800)] z-50
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
            className="absolute top-4 right-4 p-2 text-[var(--color-content-muted)] hover:text-white hover:bg-[var(--color-slate-800)] rounded-lg z-10"
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
        <header className="sticky top-0 z-30 bg-[var(--color-surface-raised)]/80 backdrop-blur-md border-b border-[var(--color-border-default)]">
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

              {/* Breadcrumb / Page Title */}
              <div className="hidden md:flex items-center gap-2 text-sm">
                <span className="text-[var(--color-content-muted)]">Home</span>
                <ChevronRight className="w-4 h-4 text-[var(--color-border-default)]" />
                <span className="font-medium text-[var(--color-content-primary)]">
                  {allNavigationGroups
                    .flatMap(g => g.items)
                    .find(item => isActiveRoute(item.path))?.title || 'Dashboard'}
                </span>
              </div>
            </div>

            {/* Right Section */}
            <div className="flex items-center gap-2">
              {/* Search */}
              <button className="hidden sm:flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-content-muted)] bg-[var(--color-surface-inset)] hover:bg-[var(--color-interactive-hover)] rounded-xl transition-colors">
                <Search className="w-4 h-4" />
                <span className="hidden lg:block">Search...</span>
                <kbd className="hidden lg:block ml-2 px-1.5 py-0.5 text-[10px] font-medium bg-[var(--color-surface-raised)] border border-[var(--color-border-default)] rounded">
                  ⌘K
                </kbd>
              </button>

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2.5 text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)] hover:bg-[var(--color-interactive-hover)] rounded-xl transition-colors"
                title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>

              {/* Notifications */}
              <button className="relative p-2.5 text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)] hover:bg-[var(--color-interactive-hover)] rounded-xl transition-colors">
                <Bell className="w-5 h-5" />
                <span className="absolute top-2 right-2 w-2 h-2 bg-[var(--color-status-danger)] rounded-full" />
              </button>

              {/* User Menu */}
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 p-1.5 hover:bg-[var(--color-interactive-hover)] rounded-xl transition-colors"
                >
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#2A6B6E] to-[#11484D] flex items-center justify-center text-white font-semibold text-sm">
                    {user?.email?.[0]?.toUpperCase() || 'U'}
                  </div>
                  <ChevronDown className={`w-4 h-4 text-[var(--color-content-muted)] transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
                </button>

                {/* Dropdown */}
                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-[var(--color-surface-raised)] rounded-xl shadow-xl border border-[var(--color-border-default)] py-2 z-50">
                    <div className="px-4 py-3 border-b border-[var(--color-border-default)]">
                      <p className="text-sm font-semibold text-[var(--color-content-primary)]">
                        {user?.email?.split('@')[0] || 'User'}
                      </p>
                      <p className="text-xs text-[var(--color-content-muted)] mt-0.5">
                        {user?.email || 'user@example.com'}
                      </p>
                    </div>
                    <div className="py-1">
                      <button
                        onClick={() => {
                          navigate('/profile');
                          setUserMenuOpen(false);
                        }}
                        className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] transition-colors"
                      >
                        <User className="w-4 h-4 text-[var(--color-content-muted)]" />
                        Your Profile
                      </button>
                      <button
                        onClick={() => {
                          navigate('/settings');
                          setUserMenuOpen(false);
                        }}
                        className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] transition-colors"
                      >
                        <Settings className="w-4 h-4 text-[var(--color-content-muted)]" />
                        Settings
                      </button>
                    </div>
                    <div className="border-t border-[var(--color-border-default)] pt-1">
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
        <main className="flex-1 p-4 lg:p-6 overflow-x-hidden min-w-0">
          {children}
        </main>

        {/* Footer */}
        <footer className="py-4 px-6 border-t border-[var(--color-border-default)] bg-[var(--color-surface-raised)]">
          <div className="flex items-center justify-between text-xs text-[var(--color-content-muted)]">
            <span>VoxTest v1.0.0</span>
            <span>Voice AI Testing Platform</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
