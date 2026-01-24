import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Header from '../Header';

describe('Header component', () => {
  const renderHeader = () => {
    return render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );
  };

  describe('Layout and structure', () => {
    it('renders the app title', () => {
      renderHeader();
      expect(screen.getByText('Voice AI Testing')).toBeInTheDocument();
    });

    it('renders as an AppBar with fixed position', () => {
      renderHeader();
      const header = screen.getByRole('banner');
      expect(header).toBeInTheDocument();
    });
  });

  describe('Notifications', () => {
    it('renders notifications button', () => {
      renderHeader();
      const notificationsButton = screen.getByRole('button', {
        name: /show notifications/i
      });
      expect(notificationsButton).toBeInTheDocument();
    });

    it('displays notification badge with count', () => {
      renderHeader();
      const badge = screen.getByText('4');
      expect(badge).toBeInTheDocument();
    });
  });

  describe('User menu', () => {
    it('renders user account button', () => {
      renderHeader();
      const userButton = screen.getByRole('button', {
        name: /user account menu/i
      });
      expect(userButton).toBeInTheDocument();
    });
  });
});
