# Frontend Testing Guide

This document explains how to write and run tests for the Voice AI Testing Framework frontend.

## Testing Stack

- **Test Runner**: [Vitest](https://vitest.dev/) - Fast, Vite-native test runner
- **Test Library**: [@testing-library/react](https://testing-library.com/react) - React component testing utilities
- **Assertions**: [@testing-library/jest-dom](https://github.com/testing-library/jest-dom) - Custom DOM matchers
- **User Events**: [@testing-library/user-event](https://testing-library.com/docs/user-event/intro) - User interaction simulation
- **DOM Environment**: [happy-dom](https://github.com/capricorn86/happy-dom) - Lightweight DOM implementation

## Quick Start

### Run Tests

```bash
# Run tests in watch mode
npm test

# Run tests once
npm run test:run

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### File Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── MyComponent.tsx
│   ├── test/
│   │   ├── setup.ts              # Global test setup
│   │   ├── utils.tsx             # Test utilities and helpers
│   │   └── vitest-basic.test.ts  # Setup verification tests
│   └── __tests__/                # Test files (optional location)
├── vitest.config.ts               # Vitest configuration
└── TESTING.md                     # This file
```

## Writing Tests

### Basic Test Structure

```tsx
import { describe, it, expect } from 'vitest'

describe('MyComponent', () => {
  it('should render correctly', () => {
    // Arrange
    const value = 'test'

    // Act
    const result = value.toUpperCase()

    // Assert
    expect(result).toBe('TEST')
  })
})
```

### Testing React Components

```tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MyComponent } from '../components/MyComponent'

describe('MyComponent', () => {
  it('should display the correct text', () => {
    // Arrange & Act
    render(<MyComponent name="World" />)

    // Assert
    expect(screen.getByText('Hello, World!')).toBeInTheDocument()
  })

  it('should handle click events', async () => {
    // Arrange
    const { user } = userEvent.setup()
    render(<MyComponent />)

    // Act
    await user.click(screen.getByRole('button'))

    // Assert
    expect(screen.getByText('Clicked!')).toBeInTheDocument()
  })
})
```

### Testing with Redux

Use the `renderWithProviders` helper for components that use Redux:

```tsx
import { renderWithProviders, mockUser } from '../test/utils'

describe('UserProfile', () => {
  it('should display user information', () => {
    // Arrange
    const preloadedState = {
      auth: {
        user: mockUser,
        isAuthenticated: true,
      },
    }

    // Act
    const { getByText } = renderWithProviders(<UserProfile />, { preloadedState })

    // Assert
    expect(getByText(mockUser.email)).toBeInTheDocument()
  })
})
```

### Testing with Router

```tsx
import { renderWithProviders } from '../test/utils'

describe('Navigation', () => {
  it('should navigate to correct route', () => {
    // Arrange & Act
    renderWithProviders(<App />, { route: '/dashboard' })

    // Assert
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })
})
```

### Mocking API Calls

```tsx
import { vi } from 'vitest'
import axios from 'axios'

vi.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('API Integration', () => {
  it('should fetch data successfully', async () => {
    // Arrange
    const mockData = { id: 1, name: 'Test' }
    mockedAxios.get.mockResolvedValue({ data: mockData })

    // Act
    render(<DataComponent />)
    await screen.findByText('Test')

    // Assert
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/data')
    expect(screen.getByText('Test')).toBeInTheDocument()
  })
})
```

## Test Utilities

### Available Helpers

The `src/test/utils.tsx` file provides:

- **renderWithProviders**: Render components with Redux and Router
- **mockUser**: Pre-configured mock user object
- **mockTestCase**: Pre-configured mock test case
- **mockTestSuite**: Pre-configured mock test suite
- **mockTestRun**: Pre-configured mock test run
- **wait**: Utility for waiting in tests
- **createMockResponse**: Create mock axios responses

### Example Usage

```tsx
import {
  renderWithProviders,
  mockUser,
  mockTestCase,
  wait,
} from '../test/utils'

it('should work with mock data', async () => {
  const { store } = renderWithProviders(<MyComponent />)

  // Use mock data
  expect(mockUser.email).toBe('test@example.com')

  // Wait for async operations
  await wait(100)

  // Check store state
  expect(store.getState().auth.user).toBeDefined()
})
```

## Common Patterns

### Testing Loading States

```tsx
it('should show loading spinner', async () => {
  render(<DataComponent />)

  // Loading state
  expect(screen.getByText('Loading...')).toBeInTheDocument()

  // Wait for data
  await screen.findByText('Data loaded')

  // Loading state should be gone
  expect(screen.queryByText('Loading...')).not.toBeInTheDocument()
})
```

### Testing Error States

```tsx
it('should display error message', async () => {
  // Arrange
  mockedAxios.get.mockRejectedValue(new Error('Network error'))

  // Act
  render(<DataComponent />)

  // Assert
  await screen.findByText(/error/i)
  expect(screen.getByText(/network error/i)).toBeInTheDocument()
})
```

### Testing Forms

```tsx
import { userEvent } from '@testing-library/user-event'

it('should submit form with valid data', async () => {
  // Arrange
  const user = userEvent.setup()
  const onSubmit = vi.fn()
  render(<LoginForm onSubmit={onSubmit} />)

  // Act
  await user.type(screen.getByLabelText(/email/i), 'test@example.com')
  await user.type(screen.getByLabelText(/password/i), 'password123')
  await user.click(screen.getByRole('button', { name: /login/i }))

  // Assert
  expect(onSubmit).toHaveBeenCalledWith({
    email: 'test@example.com',
    password: 'password123',
  })
})
```

### Testing Async Actions

```tsx
it('should dispatch async action', async () => {
  // Arrange
  const { store } = renderWithProviders(<Component />)

  // Act
  await user.click(screen.getByRole('button', { name: /load data/i }))

  // Wait for async action
  await waitFor(() => {
    expect(store.getState().data.loading).toBe(false)
  })

  // Assert
  expect(store.getState().data.items).toHaveLength(5)
})
```

## Best Practices

### 1. Test User Behavior, Not Implementation

```tsx
// ❌ Bad - testing implementation details
expect(component.state.count).toBe(5)

// ✅ Good - testing user-visible behavior
expect(screen.getByText('Count: 5')).toBeInTheDocument()
```

### 2. Use Accessible Queries

```tsx
// ❌ Avoid
screen.getByTestId('submit-button')

// ✅ Prefer (in order of preference)
screen.getByRole('button', { name: /submit/i })
screen.getByLabelText(/email/i)
screen.getByText(/welcome/i)
screen.getByPlaceholderText(/search/i)
```

### 3. Clean Up After Tests

Cleanup is automatic with @testing-library/react, but for manual cleanup:

```tsx
import { cleanup } from '@testing-library/react'

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})
```

### 4. Use describe for Organization

```tsx
describe('LoginPage', () => {
  describe('when user is not authenticated', () => {
    it('should show login form', () => {
      // test
    })
  })

  describe('when user is authenticated', () => {
    it('should redirect to dashboard', () => {
      // test
    })
  })
})
```

### 5. Keep Tests Focused

```tsx
// ❌ Bad - testing too much at once
it('should handle entire user flow', () => {
  // 50 lines of test code
})

// ✅ Good - one thing per test
it('should validate email format', () => {
  // focused test
})

it('should show error for invalid email', () => {
  // focused test
})
```

## Configuration

### vitest.config.ts

Key configuration options:

- **environment**: 'happy-dom' (lightweight DOM)
- **globals**: true (use expect, describe globally)
- **setupFiles**: Global setup before tests
- **coverage**: v8 provider with thresholds (80%)

### Coverage Thresholds

- Statements: 80%
- Branches: 80%
- Functions: 80%
- Lines: 80%

## Debugging Tests

### View Test Output

```bash
# Verbose output
npm run test:run -- --reporter=verbose

# UI mode (interactive)
npm run test:ui
```

### Debug in VS Code

Add to `.vscode/launch.json`:

```json
{
  "type": "node",
  "request": "launch",
  "name": "Debug Tests",
  "runtimeExecutable": "npm",
  "runtimeArgs": ["run", "test:run"],
  "console": "integratedTerminal",
  "internalConsoleOptions": "neverOpen"
}
```

### Console Logging

```tsx
import { screen, debug } from '@testing-library/react'

it('debug test', () => {
  render(<Component />)

  // Print DOM tree
  screen.debug()

  // Print specific element
  screen.debug(screen.getByRole('button'))
})
```

## Troubleshooting

### Tests Won't Run

```bash
# Clear cache
rm -rf node_modules/.vite

# Reinstall
npm install
```

### Module Not Found

Check imports use correct paths (no path aliases configured):

```tsx
// ✅ Good
import { Component } from '../components/Component'

// ❌ Bad (aliases not configured)
import { Component } from '@/components/Component'
```

### Async Tests Timing Out

Increase timeout in test:

```tsx
it('slow test', async () => {
  // code
}, 10000) // 10 second timeout
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [User Event Documentation](https://testing-library.com/docs/user-event/intro)

## Summary

- Use `npm test` for development (watch mode)
- Use `npm run test:run` for CI/CD (single run)
- Test user behavior, not implementation
- Use accessible queries (getByRole, getByLabelText)
- Keep tests focused and organized
- Aim for 80%+ coverage
