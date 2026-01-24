/**
 * Theme Context Provider
 * Manages theme state across the application (light, dark, oled)
 * Persists preference to localStorage and detects system preference
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

type Theme = 'light' | 'dark' | 'oled';

interface ThemeContextType {
  theme: Theme;
  isDark: boolean;
  isOled: boolean;
  toggleTheme: () => void;
  cycleTheme: () => void;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_STORAGE_KEY = 'voiceai-theme';

/**
 * Valid themes for validation
 */
const VALID_THEMES: Theme[] = ['light', 'dark', 'oled'];

/**
 * Get initial theme from localStorage or system preference
 */
function getInitialTheme(): Theme {
  // Check localStorage first
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored && VALID_THEMES.includes(stored as Theme)) {
      return stored as Theme;
    }
    // Fall back to system preference (check if matchMedia exists for test environments)
    if (typeof window.matchMedia === 'function') {
      try {
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
          return 'dark';
        }
      } catch {
        // matchMedia may throw in some environments
      }
    }
  }
  return 'light';
}

interface ThemeProviderProps {
  children: React.ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(getInitialTheme);

  const isDark = theme === 'dark' || theme === 'oled';
  const isOled = theme === 'oled';

  // Apply theme class to document element
  useEffect(() => {
    const root = document.documentElement;
    // Remove all theme classes
    root.classList.remove('light', 'dark', 'oled');
    // Add current theme class (light doesn't need a class, but we add it for consistency)
    if (theme !== 'light') {
      root.classList.add(theme);
    }
    // Persist to localStorage
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  // Listen for system preference changes
  useEffect(() => {
    // Skip if matchMedia is not available (e.g., in test environments)
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
      return;
    }

    let mediaQuery: MediaQueryList | null = null;
    try {
      mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    } catch {
      return;
    }

    // Ensure mediaQuery is valid and has addEventListener
    if (!mediaQuery || typeof mediaQuery.addEventListener !== 'function') {
      return;
    }

    const handleChange = (e: MediaQueryListEvent) => {
      // Only update if user hasn't set a preference
      const stored = localStorage.getItem(THEME_STORAGE_KEY);
      if (!stored) {
        setThemeState(e.matches ? 'dark' : 'light');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery?.removeEventListener('change', handleChange);
  }, []);

  // Toggle between light and dark (simple toggle, ignores oled)
  const toggleTheme = useCallback(() => {
    setThemeState(prev => prev === 'light' ? 'dark' : 'light');
  }, []);

  // Cycle through all themes: light -> dark -> oled -> light
  const cycleTheme = useCallback(() => {
    setThemeState(prev => {
      switch (prev) {
        case 'light': return 'dark';
        case 'dark': return 'oled';
        case 'oled': return 'light';
        default: return 'light';
      }
    });
  }, []);

  const setTheme = useCallback((newTheme: Theme) => {
    if (VALID_THEMES.includes(newTheme)) {
      setThemeState(newTheme);
    }
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, isDark, isOled, toggleTheme, cycleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * Hook to access theme context
 */
export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

export default ThemeContext;
