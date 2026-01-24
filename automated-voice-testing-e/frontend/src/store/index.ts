/**
 * Redux Store Configuration
 *
 * Configures the Redux Toolkit store with:
 * - Reducer configuration
 * - Default middleware (Redux Thunk, Immutability check, Serializability check)
 * - Redux DevTools Extension support (enabled by default in development)
 */

import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import validationReducer from './slices/validationSlice';
import githubIntegrationReducer from './slices/githubIntegrationSlice';
import jiraIntegrationReducer from './slices/jiraIntegrationSlice';
import slackIntegrationReducer from './slices/slackIntegrationSlice';
import integrationHealthReducer from './slices/integrationHealthSlice';

/**
 * Configure the Redux store
 *
 * The store is configured with slice reducers for:
 * - auth: Authentication state (user, tokens, loading, errors)
 * - validation: Validation queue state
 * - integrations: GitHub, Jira, Slack integration states
 * - integrationHealth: Integration health monitoring state
 */
const store = configureStore({
  reducer: {
    auth: authReducer,
    validation: validationReducer,
    githubIntegration: githubIntegrationReducer,
    jiraIntegration: jiraIntegrationReducer,
    slackIntegration: slackIntegrationReducer,
    integrationHealth: integrationHealthReducer,
  },
});

/**
 * Export the configured store
 * Exported both as default and named export for different use cases
 */
export { store };
export default store;

/**
 * Infer the `RootState` type from the store itself
 * This type represents the entire Redux state tree
 */
export type RootState = ReturnType<typeof store.getState>;

/**
 * Infer the `AppDispatch` type from the store's dispatch function
 * This type includes thunk action types for async actions
 */
export type AppDispatch = typeof store.dispatch;

/**
 * Export the AppStore type for testing
 * This type represents the entire store instance
 */
export type AppStore = typeof store;
