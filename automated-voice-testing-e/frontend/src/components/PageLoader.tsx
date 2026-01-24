/**
 * Shared page loading indicator displayed while lazy routes resolve.
 */

import React from 'react';
import { Loader2 } from 'lucide-react';

const PageLoader: React.FC = () => (
  <div
    data-testid="app-loading-indicator"
    className="flex items-center justify-center min-h-[60vh] w-full gap-3 flex-col"
  >
    <Loader2 className="w-10 h-10 animate-spin text-[var(--color-brand-primary)]" />
    <span className="text-[var(--color-content-secondary)] text-sm">Loading...</span>
  </div>
);

export default PageLoader;
