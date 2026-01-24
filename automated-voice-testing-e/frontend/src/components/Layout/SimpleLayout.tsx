import React from 'react';
import Navigation from '../Navigation';

interface SimpleLayoutProps {
  children: React.ReactNode;
}

const SimpleLayout: React.FC<SimpleLayoutProps> = ({ children }) => {
  return (
    <div className="app-layout">
      <div className="app-nav-wrapper">
        <Navigation />
      </div>
      <main className="app-content">
        {children}
      </main>
    </div>
  );
};

export default SimpleLayout;
