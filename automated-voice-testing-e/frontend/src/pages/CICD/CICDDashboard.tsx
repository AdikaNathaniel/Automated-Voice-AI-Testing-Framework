/**
 * CI/CD Dashboard
 *
 * Unified page for CI/CD integration with tabs for:
 * - Runs: View history of automated test runs triggered by CI/CD
 * - Configuration: Set up webhooks and test suite mappings
 */

import React, { useState } from 'react';
import { GitBranch, Settings, List } from 'lucide-react';
import CICDRuns from './CICDRuns';
import CICDConfig from './CICDConfig';

type Tab = 'runs' | 'config';

const CICDDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('config');

  const tabs = [
    { id: 'config' as Tab, label: 'Configuration', icon: Settings },
    { id: 'runs' as Tab, label: 'Triggered Runs', icon: List },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md">
        <div className="flex items-center gap-3">
          <GitBranch className="w-6 h-6" style={{ color: '#2A6B6E' }} />
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)]">
              CI/CD Integration
            </h1>
            <p className="text-sm text-[var(--color-content-muted)] mt-1">
              Automate voice testing in your continuous integration pipeline
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-md overflow-hidden">
        <div className="border-b border-[var(--color-border-default)]">
          <nav className="flex">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary text-primary'
                      : 'border-transparent text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)] hover:border-[var(--color-border-default)]'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'runs' && <CICDRuns />}
          {activeTab === 'config' && <CICDConfig />}
        </div>
      </div>
    </div>
  );
};

export default CICDDashboard;
