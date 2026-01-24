/**
 * SkipLink Component
 *
 * Accessibility component that allows keyboard users to skip navigation
 * and jump directly to main content.
 *
 * Features:
 * - Visually hidden by default
 * - Becomes visible on focus
 * - Links to main content area
 */

import React from 'react';

interface SkipLinkProps {
  /** The ID of the main content element to skip to */
  targetId?: string;
  /** The text to display in the skip link */
  children?: React.ReactNode;
}

const SkipLink: React.FC<SkipLinkProps> = ({
  targetId = 'main-content',
  children = 'Skip to main content',
}) => {
  return (
    <a
      href={`#${targetId}`}
      className="absolute -left-[10000px] top-auto w-px h-px overflow-hidden focus:fixed focus:top-2.5 focus:left-2.5 focus:w-auto focus:h-auto focus:px-6 focus:py-4 focus:text-white focus:z-[9999] focus:rounded-lg focus:no-underline focus:font-bold focus:shadow-2xl"
      style={{
        background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)',
      }}
    >
      {children}
    </a>
  );
};

export default SkipLink;
