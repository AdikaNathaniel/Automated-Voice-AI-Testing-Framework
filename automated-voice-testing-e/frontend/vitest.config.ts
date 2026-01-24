/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  test: {
    // Use happy-dom as the test environment (faster than jsdom)
    environment: 'happy-dom',

    // Global test setup
    globals: true,

    // Setup files to run before each test file
    setupFiles: ['./src/test/setup.ts'],

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
        'dist/',
        '.eslintrc.cjs'
      ],
      // Coverage thresholds
      statements: 80,
      branches: 80,
      functions: 80,
      lines: 80
    },

    // Test file patterns
    include: [
      '**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      'tests/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
    ],

    // Files to exclude from test discovery
    exclude: [
      'node_modules',
      'dist',
      '.idea',
      '.git',
      '.cache',
      'e2e' // Playwright E2E tests, not Vitest tests
    ],

    // Reporters for test output
    reporters: ['verbose'],

    // Test timeout (in milliseconds)
    testTimeout: 10000,

    // Hook timeout
    hookTimeout: 10000,

    // Bail after first test failure (useful for CI)
    // bail: 1,

    // Number of threads to run tests
    threads: true,

    // Watch mode configuration
    watch: false,

    // Mock configuration
    mockReset: true,
    restoreMocks: true,
    clearMocks: true,
  },
})
