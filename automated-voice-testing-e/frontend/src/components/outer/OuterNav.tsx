/**
 * OuterNav Component
 *
 * Sticky navigation bar for outer pages (landing, login, register).
 * Features glassmorphism effect on scroll and responsive mobile menu.
 */

import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, ArrowRight } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import vaiLogo from '../../assets/vai-logo.png';

interface OuterNavProps {
  transparent?: boolean;
}

const OuterNav: React.FC<OuterNavProps> = ({ transparent = true }) => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isDark } = useTheme();
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const navLinks = [
    { label: 'Features', href: '#features' },
    { label: 'How It Works', href: '#how-it-works' },
    { label: 'Pricing', href: '#pricing' },
  ];

  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  return (
    <>
      <nav
        className={`
          fixed top-0 left-0 right-0 z-50 transition-all duration-300
          ${scrolled || !transparent || isAuthPage
            ? 'py-3 glass glass-border shadow-sm'
            : 'py-5 bg-transparent'
          }
        `}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <img
                src={vaiLogo}
                alt="VoxTest"
                className="h-9 w-9 transition-transform duration-300 group-hover:scale-105"
              />
              <span className="text-xl font-bold text-gradient">
                VoxTest
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-8">
              {/* Nav Links - Only show on landing page */}
              {!isAuthPage && (
                <div className="flex items-center gap-1">
                  {navLinks.map((link) => (
                    <a
                      key={link.label}
                      href={link.href}
                      className={`
                        px-4 py-2 text-sm font-medium rounded-lg transition-colors duration-200
                        ${scrolled || !transparent
                          ? 'text-[var(--color-slate-600)] hover:text-[#2A6B6E] hover:bg-[#2A6B6E]/5  '
                          : 'text-[var(--color-slate-700)] hover:text-[#2A6B6E]  '
                        }
                      `}
                    >
                      {link.label}
                    </a>
                  ))}
                </div>
              )}

              {/* Auth Buttons */}
              <div className="flex items-center gap-3">
                {location.pathname !== '/login' && (
                  <Link to="/login" className="btn-ghost">
                    Sign In
                  </Link>
                )}
                {location.pathname !== '/register' && (
                  <Link
                    to="/register"
                    className="btn-primary-glow flex items-center gap-2 !py-2.5 !px-5"
                  >
                    Get Started
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                )}
              </div>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-[var(--color-content-secondary)] hover:bg-[var(--color-slate-100)] hover:bg-[var(--color-interactive-hover)] transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="absolute top-0 right-0 w-full max-w-sm h-full bg-[var(--color-surface-base)] shadow-xl animate-slide-in-right">
            <div className="p-6 pt-20">
              {/* Mobile Nav Links */}
              {!isAuthPage && (
                <div className="space-y-1 mb-8">
                  {navLinks.map((link) => (
                    <a
                      key={link.label}
                      href={link.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className="block px-4 py-3 text-base font-medium text-[var(--color-content-secondary)] hover:text-[#2A6B6E]  hover:bg-[var(--color-slate-50)] hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
                    >
                      {link.label}
                    </a>
                  ))}
                </div>
              )}

              {/* Mobile Auth Buttons */}
              <div className="space-y-3">
                {location.pathname !== '/login' && (
                  <Link
                    to="/login"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block w-full px-4 py-3 text-center text-base font-medium text-[var(--color-content-secondary)] border border-[var(--color-border-default)] rounded-xl hover:bg-[var(--color-slate-50)] hover:bg-[var(--color-interactive-hover)] transition-colors"
                  >
                    Sign In
                  </Link>
                )}
                {location.pathname !== '/register' && (
                  <Link
                    to="/register"
                    onClick={() => setMobileMenuOpen(false)}
                    className="btn-primary-glow block w-full text-center"
                  >
                    Get Started
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Spacer for fixed nav */}
      <div className={`h-16 ${scrolled ? 'h-14' : 'h-20'}`} />
    </>
  );
};

export default OuterNav;
