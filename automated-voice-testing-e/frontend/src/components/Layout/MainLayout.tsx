/**
 * MainLayout Component (TASK-127)
 *
 * Main application layout with:
 * - Header (nav bar)
 * - Sidebar (navigation)
 * - Main content area for children
 * - Responsive design for mobile/desktop
 *
 * Features:
 * - Mobile-first responsive design
 * - Collapsible sidebar on mobile
 * - Fixed header
 * - Proper spacing and padding
 */

import React, { useState, useEffect, ReactNode } from 'react';
import { Menu, X } from 'lucide-react';

// Drawer width constant
const drawerWidth = 240;

/**
 * Props interface for MainLayout component
 */
interface MainLayoutProps {
  /**
   * Child components to render in main content area
   */
  children: ReactNode;
}

/**
 * MainLayout component
 *
 * Provides the main application layout structure with header, sidebar, and content area.
 * Responsive design adapts drawer behavior based on screen size.
 *
 * @param props - Component props
 * @returns Main layout with header, sidebar, and content
 *
 * @example
 * ```tsx
 * <MainLayout>
 *   <YourPageContent />
 * </MainLayout>
 * ```
 */
const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  // State for mobile drawer open/close
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Handle responsive breakpoint
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  /**
   * Handle drawer toggle for mobile view
   */
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  /**
   * Drawer content (same for mobile and desktop)
   */
  const drawer = (
    <div className="overflow-auto h-full bg-[var(--color-surface-raised)]">
      {/* Spacer to push content below header */}
      <div className="h-16" />
      <div className="p-4">
        {/* Sidebar content will be added by child components */}
        <p className="text-sm text-[var(--color-content-muted)]">Sidebar Content</p>
      </div>
    </div>
  );

  return (
    <div className="flex min-h-screen bg-[var(--color-surface-base)]">
      {/* Header (AppBar) */}
      <header className="nav-container fixed top-0 left-0 right-0 z-50 bg-[var(--color-surface-raised)] shadow-sm">
        <div className="flex items-center h-16 px-4">
          {/* Menu icon button for mobile */}
          <button
            onClick={handleDrawerToggle}
            className="p-2 mr-2 md:hidden rounded-lg hover:bg-[var(--color-interactive-hover)] transition-colors"
            aria-label="Open drawer"
          >
            <Menu className="w-6 h-6" />
          </button>

          {/* App title */}
          <h1 className="nav-brand text-xl font-semibold text-[var(--color-content-primary)] truncate">
            Voice AI Testing
          </h1>
        </div>
      </header>

      {/* Sidebar Navigation */}
      <nav
        className="w-0 md:w-60 flex-shrink-0"
        aria-label="navigation"
      >
        {/* Mobile drawer - temporary, overlays content */}
        {isMobile && (
          <>
            {/* Overlay */}
            {mobileOpen && (
              <div
                className="fixed inset-0 bg-black bg-opacity-50 z-40"
                onClick={handleDrawerToggle}
                aria-hidden="true"
              />
            )}
            {/* Mobile Drawer */}
            <aside
              className={`fixed top-0 left-0 h-full z-50 transform transition-transform duration-300 ${
                mobileOpen ? 'translate-x-0' : '-translate-x-full'
              }`}
              style={{ width: `${drawerWidth}px` }}
            >
              <div className="absolute top-4 right-4">
                <button
                  onClick={handleDrawerToggle}
                  className="p-2 rounded-lg hover:bg-[var(--color-interactive-hover)] transition-colors"
                  aria-label="Close drawer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              {drawer}
            </aside>
          </>
        )}

        {/* Desktop drawer - permanent, pushes content */}
        {!isMobile && (
          <aside
            className="fixed top-0 left-0 h-full bg-[var(--color-surface-raised)] border-r border-[var(--color-border-default)]"
            style={{ width: `${drawerWidth}px` }}
          >
            {drawer}
          </aside>
        )}
      </nav>

      {/* Main content area */}
      <main
        className="flex-1 p-6 mt-16"
        style={{
          marginLeft: !isMobile ? `${drawerWidth}px` : 0,
        }}
      >
        {/* Render children components */}
        {children}
      </main>
    </div>
  );
};

export default MainLayout;
