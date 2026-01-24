/**
 * Package script safety tests (TASK-280).
 */

import { describe, expect, test } from 'vitest'
import { readFileSync } from 'node:fs'
import { join } from 'node:path'

const packageJson = JSON.parse(
  readFileSync(join(__dirname, '..', '..', 'package.json'), 'utf-8'),
) as { scripts?: Record<string, string> }

describe('package.json build script', () => {
  test('build script uses production mode', () => {
    const buildScript = packageJson.scripts?.build ?? ''
    expect(buildScript).toContain('vite build')
    expect(buildScript).toContain('--mode production')
  })
})
