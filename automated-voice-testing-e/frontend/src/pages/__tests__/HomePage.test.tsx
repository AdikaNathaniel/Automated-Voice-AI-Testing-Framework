/**
 * HomePage asset optimization tests (TASK-282).
 */

import { screen, within } from '@testing-library/react'
import { renderWithProviders } from '../../test/utils'
import HomePage from '../HomePage'

describe('HomePage hero image', () => {
  it('renders WebP source with lazy-loaded fallback image', () => {
    renderWithProviders(<HomePage />)

    const picture = screen.getByTestId('hero-image')
    const sources = picture.querySelectorAll('source')
    expect(sources.length).toBeGreaterThan(0)
    expect(Array.from(sources)).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          type: 'image/webp',
        }),
      ]),
    )

    const heroImg = within(picture).getByRole('img', { name: /automated testing platform/i })
    expect(heroImg).toHaveAttribute('loading', 'lazy')
    expect(heroImg.getAttribute('src') ?? '').toMatch(/hero-background\.jpg$/)
    expect(heroImg.getAttribute('decoding')).toBe('async')
  })
})
