/**
 * Admin Dashboard Page
 *
 * Overview page for super admin console showing key metrics
 * for organizations and users across the platform.
 */

import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Building2,
  Users,
  UserCheck,
  UserX,
  TrendingUp,
  ArrowRight,
  Shield,
  Activity,
} from 'lucide-react';
import { listOrganizations, getUserStats } from '../../services/admin.service';
import type { Organization, UserStats } from '../../types/admin';
import { ROLE_LABELS, ROLE_COLORS, type UserRole } from '../../types/admin';

interface StatCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon: React.ReactNode;
  color: 'purple' | 'blue' | 'green' | 'red' | 'yellow';
  onClick?: () => void;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, subtitle, icon, color, onClick }) => {
  const colorClasses = {
    purple: 'bg-[var(--color-status-purple-bg)] border-[var(--color-status-purple-bg)]',
    blue: 'bg-[var(--color-status-info-bg)] border-[var(--color-status-info-bg)]',
    green: 'bg-[var(--color-status-success-bg)] border-[var(--color-status-success-bg)]',
    red: 'bg-[var(--color-status-danger-bg)] border-[var(--color-status-danger-bg)]',
    yellow: 'bg-[var(--color-status-warning-bg)] border-[var(--color-status-warning-bg)]',
  };

  const iconColorClasses = {
    purple: 'text-[var(--color-status-purple)]',
    blue: 'text-[var(--color-status-info)]',
    green: 'text-[var(--color-status-success)]',
    red: 'text-[var(--color-status-danger)]',
    yellow: 'text-[var(--color-status-warning)]',
  };

  return (
    <div
      className={`p-6 rounded-xl border ${colorClasses[color]} ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-xl ${colorClasses[color]}`}>
          <span className={iconColorClasses[color]}>{icon}</span>
        </div>
        {onClick && (
          <ArrowRight className="w-5 h-5 text-[var(--color-content-muted)]" />
        )}
      </div>
      <div className="text-3xl font-bold text-[var(--color-content-primary)] mb-1">
        {value}
      </div>
      <div className="text-sm font-medium text-[var(--color-content-secondary)]">
        {title}
      </div>
      {subtitle && (
        <div className="text-xs text-[var(--color-content-muted)] mt-1">
          {subtitle}
        </div>
      )}
    </div>
  );
};

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [orgTotal, setOrgTotal] = useState(0);
  const [userStats, setUserStats] = useState<UserStats | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [orgsResponse, stats] = await Promise.all([
        listOrganizations({ page: 1, page_size: 5 }),
        getUserStats(),
      ]);
      setOrganizations(orgsResponse.items);
      setOrgTotal(orgsResponse.total);
      setUserStats(stats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md">
          <h1 className="text-3xl font-bold text-[var(--color-content-primary)]">Admin Dashboard</h1>
          <p className="text-sm text-[var(--color-content-muted)] mt-1">Platform overview and management</p>
        </div>
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md">
          <div className="flex flex-col items-center justify-center p-20">
            <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#9333EA' }}></div>
            <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Dashboard...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md">
          <h1 className="text-3xl font-bold text-[var(--color-content-primary)]">Admin Dashboard</h1>
          <p className="text-sm text-[var(--color-content-muted)] mt-1">Platform overview and management</p>
        </div>
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md">
          <div className="p-10 text-center text-[var(--color-status-danger)]">{error}</div>
        </div>
      </div>
    );
  }

  const activeOrgs = organizations.filter(org => org.is_active).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md">
        <h1 className="text-3xl font-bold text-[var(--color-content-primary)]">Admin Dashboard</h1>
        <p className="text-sm text-[var(--color-content-muted)] mt-1">
          Platform overview and management
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Organizations"
          value={orgTotal}
          subtitle={`${activeOrgs} active`}
          icon={<Building2 className="w-6 h-6" />}
          color="purple"
          onClick={() => navigate('/admin/organizations')}
        />
        <StatCard
          title="Total Users"
          value={userStats?.total_users || 0}
          subtitle={`${userStats?.active_users || 0} active`}
          icon={<Users className="w-6 h-6" />}
          color="blue"
          onClick={() => navigate('/admin/users')}
        />
        <StatCard
          title="Active Users"
          value={userStats?.active_users || 0}
          subtitle={`${Math.round(((userStats?.active_users || 0) / (userStats?.total_users || 1)) * 100)}% of total`}
          icon={<UserCheck className="w-6 h-6" />}
          color="green"
        />
        <StatCard
          title="Inactive Users"
          value={userStats?.inactive_users || 0}
          subtitle="Require attention"
          icon={<UserX className="w-6 h-6" />}
          color="red"
        />
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Users by Role */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)] p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">Users by Role</h2>
            <Shield className="w-5 h-5 text-[var(--color-content-muted)]" />
          </div>
          <div className="space-y-4">
            {userStats?.users_by_role && Object.entries(userStats.users_by_role).length > 0 ? (
              Object.entries(userStats.users_by_role)
                .sort(([, a], [, b]) => b - a)
                .map(([role, count]) => {
                  const roleKey = role as UserRole;
                  const roleColors = ROLE_COLORS[roleKey] || ROLE_COLORS.viewer;
                  const roleLabel = ROLE_LABELS[roleKey] || role;
                  const percentage = Math.round((count / (userStats?.total_users || 1)) * 100);

                  return (
                    <div key={role} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className={`px-2.5 py-1 text-xs font-medium rounded-lg ${roleColors.bg} ${roleColors.text}`}>
                          {roleLabel}
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-24 h-2 bg-[var(--color-surface-inset)] rounded-full overflow-hidden">
                          <div
                            className="h-full bg-[var(--color-status-purple)] rounded-full"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-[var(--color-content-primary)] w-12 text-right">
                          {count}
                        </span>
                      </div>
                    </div>
                  );
                })
            ) : (
              <p className="text-[var(--color-content-muted)] text-sm">No users found</p>
            )}
          </div>
        </div>

        {/* Recent Organizations */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)] p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">Recent Organizations</h2>
            <button
              onClick={() => navigate('/admin/organizations')}
              className="text-sm text-[var(--color-status-purple)] hover:underline flex items-center gap-1"
            >
              View all
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          <div className="space-y-3">
            {organizations.length > 0 ? (
              organizations.map((org) => (
                <div
                  key={org.id}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-[var(--color-interactive-hover)] transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center text-white font-semibold">
                      {org.name[0]?.toUpperCase()}
                    </div>
                    <div>
                      <div className="font-medium text-[var(--color-content-primary)]">{org.name}</div>
                      <div className="text-xs text-[var(--color-content-muted)]">
                        {org.member_count} member{org.member_count !== 1 ? 's' : ''}
                      </div>
                    </div>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-lg ${
                      org.is_active
                        ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]'
                        : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)]'
                    }`}
                  >
                    {org.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-[var(--color-content-muted)] text-sm text-center py-4">
                No organizations yet
              </p>
            )}
          </div>
        </div>
      </div>

      {/* User Distribution */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)] p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">User Distribution</h2>
          <Activity className="w-5 h-5 text-[var(--color-content-muted)]" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-[var(--color-status-purple-bg)] rounded-xl">
            <div className="text-3xl font-bold text-[var(--color-status-purple)] mb-1">
              {userStats?.users_by_organization || 0}
            </div>
            <div className="text-sm text-[var(--color-content-secondary)]">In Organizations</div>
          </div>
          <div className="text-center p-4 bg-[var(--color-status-info-bg)] rounded-xl">
            <div className="text-3xl font-bold text-[var(--color-status-info)] mb-1">
              {userStats?.individual_users || 0}
            </div>
            <div className="text-sm text-[var(--color-content-secondary)]">Individual Users</div>
          </div>
          <div className="text-center p-4 bg-[var(--color-status-success-bg)] rounded-xl">
            <div className="text-3xl font-bold text-[var(--color-status-success)] mb-1">
              {orgTotal}
            </div>
            <div className="text-sm text-[var(--color-content-secondary)]">Total Organizations</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
