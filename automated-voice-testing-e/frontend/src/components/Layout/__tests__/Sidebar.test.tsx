import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Sidebar from '../Sidebar';

describe('Sidebar navigation', () => {
  it('includes integrations link and highlights it when active', () => {
    render(
      <MemoryRouter initialEntries={['/integrations']}>
        <Sidebar />
      </MemoryRouter>
    );

    const link = screen.getByRole('link', { name: /Integrations/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveClass('Mui-selected');
  });
});
