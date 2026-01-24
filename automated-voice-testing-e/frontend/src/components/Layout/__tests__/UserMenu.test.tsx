import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import UserMenu from '../UserMenu';

describe('UserMenu component', () => {
  const mockOnClose = vi.fn();

  const renderUserMenu = (props = {}) => {
    const defaultProps = {
      anchorEl: document.createElement('button'),
      open: true,
      onClose: mockOnClose,
    };

    return render(
      <MemoryRouter>
        <UserMenu {...defaultProps} {...props} />
      </MemoryRouter>
    );
  };

  beforeEach(() => {
    mockOnClose.mockClear();
  });

  describe('Menu items', () => {
    it('renders Profile menu item', () => {
      renderUserMenu();
      expect(screen.getByText('Profile')).toBeInTheDocument();
    });

    it('renders Settings menu item', () => {
      renderUserMenu();
      expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    it('renders Logout menu item', () => {
      renderUserMenu();
      expect(screen.getByText('Logout')).toBeInTheDocument();
    });

    it('renders all menu items in correct order', () => {
      renderUserMenu();
      const menuItems = screen.getAllByRole('menuitem');
      expect(menuItems).toHaveLength(3);
      expect(menuItems[0]).toHaveTextContent('Profile');
      expect(menuItems[1]).toHaveTextContent('Settings');
      expect(menuItems[2]).toHaveTextContent('Logout');
    });
  });

  describe('Menu visibility', () => {
    it('renders menu when open is true', () => {
      renderUserMenu({ open: true });
      expect(screen.getByRole('menu')).toBeInTheDocument();
    });

    it('does not render menu when open is false', () => {
      renderUserMenu({ open: false });
      expect(screen.queryByRole('menu')).not.toBeInTheDocument();
    });
  });

  describe('Click handlers', () => {
    it('calls onClose when Profile is clicked', () => {
      renderUserMenu();
      fireEvent.click(screen.getByText('Profile'));
      expect(mockOnClose).toHaveBeenCalled();
    });

    it('calls onClose when Settings is clicked', () => {
      renderUserMenu();
      fireEvent.click(screen.getByText('Settings'));
      expect(mockOnClose).toHaveBeenCalled();
    });

    it('calls onClose when Logout is clicked', () => {
      renderUserMenu();
      fireEvent.click(screen.getByText('Logout'));
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe('Icons', () => {
    it('renders icons for each menu item', () => {
      renderUserMenu();
      // Check that SVG icons are present (MUI icons render as SVGs)
      const menuItems = screen.getAllByRole('menuitem');
      menuItems.forEach(item => {
        const icon = item.querySelector('svg');
        expect(icon).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('menu items are focusable', () => {
      renderUserMenu();
      const menuItems = screen.getAllByRole('menuitem');
      menuItems.forEach(item => {
        expect(item).not.toHaveAttribute('disabled');
      });
    });
  });
});
