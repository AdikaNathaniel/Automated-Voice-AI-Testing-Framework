/**
 * LanguageSelector Component Tests
 *
 * Validates that the selector renders language options with native names,
 * exposes an "All languages" choice, and notifies consumers when the
 * selection changes.
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import LanguageSelector, {
  type LanguageOption,
} from '../LanguageSelector'

const LANGUAGES: LanguageOption[] = [
  {
    code: 'en-US',
    name: 'English (United States)',
    nativeName: 'English',
  },
  {
    code: 'ja-JP',
    name: 'Japanese (Japan)',
    nativeName: '日本語',
  },
  {
    code: 'pt-BR',
    name: 'Portuguese (Brazil)',
    nativeName: 'Português',
  },
]

describe('LanguageSelector', () => {
  it('renders language options with native names', () => {
    render(
      <LanguageSelector
        languages={LANGUAGES}
        value="en-US"
        onChange={vi.fn()}
        includeAllOption
      />
    )

    const select = screen.getByRole('combobox', { name: 'Language' })
    expect(select).toBeInTheDocument()
    expect(select).toHaveValue('en-US')

    // Check options are rendered
    const options = screen.getAllByRole('option')
    expect(options).toHaveLength(4) // All languages + 3 languages

    // Check "All languages" option exists
    expect(screen.getByRole('option', { name: 'All languages' })).toBeInTheDocument()

    // Check language options with native names
    expect(screen.getByRole('option', { name: 'English (United States) (English)' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Japanese (Japan) (日本語)' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Portuguese (Brazil) (Português)' })).toBeInTheDocument()
  })

  it('invokes onChange when a new language is selected', async () => {
    const user = userEvent.setup()
    const handleChange = vi.fn()

    render(
      <LanguageSelector
        languages={LANGUAGES}
        value="en-US"
        onChange={handleChange}
      />
    )

    const select = screen.getByRole('combobox', { name: 'Language' })
    await user.selectOptions(select, 'ja-JP')

    expect(handleChange).toHaveBeenCalledWith('ja-JP')
  })

  it('supports selecting the all-languages option when enabled', async () => {
    const user = userEvent.setup()
    const handleChange = vi.fn()

    render(
      <LanguageSelector
        languages={LANGUAGES}
        value="en-US"
        onChange={handleChange}
        includeAllOption
      />
    )

    const select = screen.getByRole('combobox', { name: 'Language' })
    await user.selectOptions(select, '__ALL_LANGUAGES__')

    expect(handleChange).toHaveBeenCalledWith(null)
  })

  it('displays helper text when provided', () => {
    render(
      <LanguageSelector
        languages={LANGUAGES}
        value="en-US"
        onChange={vi.fn()}
        helperText="Select a language to filter results"
      />
    )

    expect(screen.getByText('Select a language to filter results')).toBeInTheDocument()
  })

  it('disables the select when disabled prop is true', () => {
    render(
      <LanguageSelector
        languages={LANGUAGES}
        value="en-US"
        onChange={vi.fn()}
        disabled
      />
    )

    expect(screen.getByRole('combobox')).toBeDisabled()
  })

  it('renders with custom label', () => {
    render(
      <LanguageSelector
        languages={LANGUAGES}
        value="en-US"
        onChange={vi.fn()}
        label="Select Language"
      />
    )

    expect(screen.getByRole('combobox', { name: 'Select Language' })).toBeInTheDocument()
  })

  it('shows All languages as selected when value is null', () => {
    render(
      <LanguageSelector
        languages={LANGUAGES}
        value={null}
        onChange={vi.fn()}
        includeAllOption
      />
    )

    const select = screen.getByRole('combobox')
    expect(select).toHaveValue('__ALL_LANGUAGES__')
  })
})
