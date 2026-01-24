/**
 * Tests for App routing with lazy-loaded pages (TASK-279).
 */

import { render, screen, waitForElementToBeRemoved } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { vi } from 'vitest'
import App from '../App'
import authReducer from '../store/slices/authSlice'
import validationReducer from '../store/slices/validationSlice'
import githubIntegrationReducer from '../store/slices/githubIntegrationSlice'

vi.mock('../pages/Integrations/GitHub', () => ({
  default: () => <div>Mock GitHub Integration Page</div>,
}))

vi.mock('../pages/Integrations/Jira', () => ({
  default: () => <div>Mock Jira Integration Page</div>,
}))

vi.mock('../pages/Integrations/Slack', () => ({
  default: () => <div>Mock Slack Integration Page</div>,
}))

vi.mock('../pages/Integrations/IntegrationsDashboard', () => ({
  default: () => <div>Mock Integrations Dashboard Page</div>,
}))

vi.mock('../pages/KnowledgeBase/KnowledgeBase', () => ({
  default: () => <div>Mock Knowledge Base Page</div>,
}))

vi.mock('../pages/KnowledgeBase/KnowledgeBaseSearch', () => ({
  default: () => <div>Mock Knowledge Base Search Page</div>,
}))

vi.mock('../pages/KnowledgeBase/ArticleView', () => ({
  default: () => <div>Mock Knowledge Base Article</div>,
}))

vi.mock('../pages/KnowledgeBase/ArticleEditor', () => ({
  default: () => <div>Mock Knowledge Base Article Editor</div>,
}))

vi.mock('../pages/Regressions/RegressionList', () => ({
  default: () => <div>Mock Regression List Page</div>,
}))

vi.mock('../pages/Regressions/RegressionComparison', () => ({
  default: () => <div>Mock Regression Comparison Page</div>,
}))

vi.mock('../pages/Regressions/BaselineManagement', () => ({
  default: () => <div>Mock Baseline Management Page</div>,
}))

type AuthState = ReturnType<typeof authReducer>
type ValidationState = ReturnType<typeof validationReducer>
type GitHubIntegrationState = ReturnType<typeof githubIntegrationReducer>

interface RenderOptions {
  authOverrides?: Partial<AuthState>
  validationOverrides?: Partial<ValidationState>
  githubIntegrationOverrides?: Partial<GitHubIntegrationState>
}

const renderApp = (path: string, options: RenderOptions = {}) => {
  const { authOverrides = {}, validationOverrides = {}, githubIntegrationOverrides = {} } = options

  window.history.pushState({}, 'Test page', path)

  const authInitialState = authReducer(undefined, { type: '@@INIT' } as unknown)
  const validationInitialState = validationReducer(undefined, { type: '@@INIT' } as unknown)
  const githubIntegrationInitialState = githubIntegrationReducer(undefined, { type: '@@INIT' } as unknown)

  const store = configureStore({
    reducer: {
      auth: authReducer,
      validation: validationReducer,
      githubIntegration: githubIntegrationReducer,
    },
    preloadedState: {
      auth: { ...authInitialState, ...authOverrides },
      validation: { ...validationInitialState, ...validationOverrides },
      githubIntegration: { ...githubIntegrationInitialState, ...githubIntegrationOverrides },
    },
  })

  return render(
    <Provider store={store}>
      <App />
    </Provider>,
  )
}

describe('App lazy route loading', () => {
  test('shows loading fallback before rendering protected dashboard route', async () => {
    renderApp('/dashboard', { authOverrides: { isAuthenticated: true } })

    // Suspense fallback should render immediately
    const loader = await screen.findByTestId('app-loading-indicator')
    expect(loader).toBeInTheDocument()

    // Wait until fallback unmounts and dashboard content appears
    await waitForElementToBeRemoved(loader)
    expect(await screen.findByRole('heading', { name: /dashboard/i })).toBeInTheDocument()
  })

  test('lazy loads public home route with fallback', async () => {
    renderApp('/')

    const loader = await screen.findByTestId('app-loading-indicator')
    expect(loader).toBeInTheDocument()

    await waitForElementToBeRemoved(loader)
    expect(await screen.findByRole('heading', { name: /automated testing platform/i })).toBeInTheDocument()
  })

  test('renders GitHub integration route for authenticated users', async () => {
    renderApp('/integrations/github', { authOverrides: { isAuthenticated: true } })

    const loader = await screen.findByTestId('app-loading-indicator')
    expect(loader).toBeInTheDocument()

    await waitForElementToBeRemoved(loader)
    expect(await screen.findByText(/Mock GitHub Integration Page/)).toBeInTheDocument()
  })

  test('renders Jira integration route for authenticated users', async () => {
    renderApp('/integrations/jira', { authOverrides: { isAuthenticated: true } })

    const loader = await screen.findByTestId('app-loading-indicator')
    expect(loader).toBeInTheDocument()

    await waitForElementToBeRemoved(loader)
    expect(await screen.findByText(/Mock Jira Integration Page/)).toBeInTheDocument()
  })

  test('renders Slack integration route for authenticated users', async () => {
    renderApp('/integrations/slack', { authOverrides: { isAuthenticated: true } })

    const loader = await screen.findByTestId('app-loading-indicator')
    expect(loader).toBeInTheDocument()

    await waitForElementToBeRemoved(loader)
    expect(await screen.findByText(/Mock Slack Integration Page/)).toBeInTheDocument()
  })

  test('renders integrations dashboard route for authenticated users', async () => {
    renderApp('/integrations', { authOverrides: { isAuthenticated: true } })

    const loader = await screen.findByTestId('app-loading-indicator')
    expect(loader).toBeInTheDocument()

    await waitForElementToBeRemoved(loader)
    expect(await screen.findByText(/Mock Integrations Dashboard Page/)).toBeInTheDocument()
  })

  test('renders regressions route for authenticated users', async () => {
    renderApp('/regressions', { authOverrides: { isAuthenticated: true } })

    const loader = await screen.findByTestId('app-loading-indicator')
    expect(loader).toBeInTheDocument()

    await waitForElementToBeRemoved(loader)
    expect(await screen.findByText(/Mock Regression List Page/)).toBeInTheDocument()
  })

  test('renders regression comparison route for authenticated users', async () => {
    renderApp('/regressions/case-123/comparison', { authOverrides: { isAuthenticated: true } })

    const loader = await screen.findByTestId('app-loading-indicator')
    expect(loader).toBeInTheDocument()

    await waitForElementToBeRemoved(loader)
    expect(await screen.findByText(/Mock Regression Comparison Page/)).toBeInTheDocument()
  })

  test('renders baseline management route for authenticated users', async () => {
    renderApp('/regressions/case-123/baselines', { authOverrides: { isAuthenticated: true } })

    const loader = await screen.findByTestId('app-loading-indicator')
    expect(loader).toBeInTheDocument()

    await waitForElementToBeRemoved(loader)
    expect(await screen.findByText(/Mock Baseline Management Page/)).toBeInTheDocument()
  })

  test('renders knowledge base list route for authenticated users', async () => {
    renderApp('/knowledge-base', { authOverrides: { isAuthenticated: true } })

    const loader = await screen.findByTestId('app-loading-indicator')
    expect(loader).toBeInTheDocument()

    await waitForElementToBeRemoved(loader)
    expect(await screen.findByText(/Mock Knowledge Base Page/)).toBeInTheDocument()
  })

  test('renders knowledge base search route for authenticated users', async () => {
    renderApp('/knowledge-base/search', { authOverrides: { isAuthenticated: true } })

    const loader = await screen.findByTestId('app-loading-indicator')
    expect(loader).toBeInTheDocument()

    await waitForElementToBeRemoved(loader)
    expect(await screen.findByText(/Mock Knowledge Base Search Page/)).toBeInTheDocument()
  })

  test('renders knowledge base article route for authenticated users', async () => {
    renderApp('/knowledge-base/article-123', { authOverrides: { isAuthenticated: true } })

    const loader = await screen.findByTestId('app-loading-indicator')
    expect(loader).toBeInTheDocument()

    await waitForElementToBeRemoved(loader)
    expect(await screen.findByText(/Mock Knowledge Base Article/)).toBeInTheDocument()
  })

  test('renders knowledge base editor route for creating an article', async () => {
    renderApp('/knowledge-base/new', { authOverrides: { isAuthenticated: true } })

    expect(await screen.findByText(/Mock Knowledge Base Article Editor/)).toBeInTheDocument()
  })

  test('renders knowledge base editor route for updating an article', async () => {
    renderApp('/knowledge-base/article-42/edit', { authOverrides: { isAuthenticated: true } })

    expect(await screen.findByText(/Mock Knowledge Base Article Editor/)).toBeInTheDocument()
  })
})
