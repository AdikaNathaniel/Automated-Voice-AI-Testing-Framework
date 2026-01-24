/**
 * Build configuration tests (TASK-280).
 *
 * Ensures Vite build is configured for aggressive tree shaking and chunk splitting.
 */

import { describe, expect, test } from 'vitest'
import config from '../../vite.config'

describe('Vite build configuration', () => {
  test('enables recommended tree shaking and separates vendor chunk', () => {
    expect(config.build).toBeDefined()
    expect(config.build?.rollupOptions?.treeshake).toBe('recommended')

    const manualChunks = config.build?.rollupOptions?.output?.manualChunks
    expect(manualChunks).toBeDefined()

    if (typeof manualChunks === 'function') {
      const vendorChunk = manualChunks('node_modules/react/index.js', 'node_modules/react/index.js')
      expect(vendorChunk).toBe('vendor')
    } else if (manualChunks && typeof manualChunks === 'object') {
      expect(manualChunks).toHaveProperty('vendor')
    } else {
      throw new Error('manualChunks must be defined as function or object')
    }
  })
})
