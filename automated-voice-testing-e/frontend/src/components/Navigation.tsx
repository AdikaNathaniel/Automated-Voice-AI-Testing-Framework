import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FlaskConical,
  TrendingUp,
  CheckCircle,
  FileText,
} from 'lucide-react';

const Navigation: React.FC = () => {
  const location = useLocation();

  const navLinks = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/scenarios', label: 'Scenarios', icon: FlaskConical },
    { path: '/analytics', label: 'Analytics', icon: TrendingUp },
    { path: '/validation', label: 'Validation', icon: CheckCircle },
    { path: '/reports', label: 'Reports', icon: FileText },
  ];

  return (
    <nav className="nav-container">
      <div className="nav-brand">Productive Playhouse</div>
      <div className="flex gap-2">
        {navLinks.map((link) => {
          const Icon = link.icon;
          const isActive = location.pathname === link.path;

          return (
            <Link
              key={link.path}
              to={link.path}
              className={`nav-link ${isActive ? 'active' : ''}`}
            >
              <Icon size={16} />
              {link.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
};

export default Navigation;
