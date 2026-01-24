/**
 * MainLayout Component Tests
 *
 * Note: Full integration tests require vitest setup for window.matchMedia
 * due to the useMediaQuery hook. These tests verify basic exports and types.
 */

import { describe, it, expect } from 'vitest';
import MainLayout from '../MainLayout';

describe('MainLayout component', () => {
  describe('Component export', () => {
    it('exports MainLayout component', () => {
      expect(MainLayout).toBeDefined();
    });

    it('is a function component', () => {
      expect(typeof MainLayout).toBe('function');
    });

    it('has the correct display name', () => {
      expect(MainLayout.name).toBe('MainLayout');
    });
  });
});
