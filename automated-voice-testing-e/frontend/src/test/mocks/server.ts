/**
 * MSW Server Setup
 *
 * Creates and exports an MSW server instance configured
 * for Node.js test environments (Vitest).
 */

import { setupServer } from 'msw/node'
import { handlers } from './handlers'

// Create MSW server with our request handlers
export const server = setupServer(...handlers)
