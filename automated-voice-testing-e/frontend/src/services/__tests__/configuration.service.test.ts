import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  getConfigurations,
  getConfiguration,
  updateConfiguration,
  getConfigurationHistory,
} from '../configuration.service';

const mockGet = vi.fn();
const mockPatch = vi.fn();

vi.mock('../api', () => ({
  default: {
    get: (...args: unknown[]) => mockGet(...args),
    patch: (...args: unknown[]) => mockPatch(...args),
  },
}));

describe('configuration.service', () => {
  beforeEach(() => {
    mockGet.mockReset();
    mockPatch.mockReset();
  });

  describe('getConfigurations', () => {
    it('fetches configurations with minimal parameters', async () => {
      mockGet.mockResolvedValue({
        data: {
          total: 1,
          items: [
            {
              id: 'config-1',
              config_key: 'api_settings',
              description: 'API configuration',
              is_active: true,
              config_data: {
                type: 'api',
                environment: 'production',
              },
              created_at: '2025-03-15T10:00:00Z',
              updated_at: '2025-03-15T12:00:00Z',
            },
          ],
        },
      });

      const result = await getConfigurations({});

      expect(mockGet).toHaveBeenCalledWith('/v1/configurations', {
        params: {
          type: undefined,
          environment: undefined,
          include_inactive: false,
        },
      });

      expect(result).toEqual({
        total: 1,
        items: [
          {
            id: 'config-1',
            configKey: 'api_settings',
            description: 'API configuration',
            type: 'api',
            environment: 'production',
            isActive: true,
            createdAt: '2025-03-15T10:00:00Z',
            updatedAt: '2025-03-15T12:00:00Z',
          },
        ],
      });
    });

    it('applies filters when provided', async () => {
      mockGet.mockResolvedValue({
        data: {
          total: 0,
          items: [],
        },
      });

      await getConfigurations({
        type: 'telephony',
        environment: 'staging',
        includeInactive: true,
      });

      expect(mockGet).toHaveBeenCalledWith('/v1/configurations', {
        params: {
          type: 'telephony',
          environment: 'staging',
          include_inactive: true,
        },
      });
    });

    it('handles null config_data fields', async () => {
      mockGet.mockResolvedValue({
        data: {
          total: 1,
          items: [
            {
              id: 'config-2',
              config_key: 'empty_config',
              description: null,
              is_active: false,
              config_data: null,
              created_at: '2025-03-16T08:00:00Z',
              updated_at: '2025-03-16T08:00:00Z',
            },
          ],
        },
      });

      const result = await getConfigurations({});

      expect(result.items[0]).toEqual({
        id: 'config-2',
        configKey: 'empty_config',
        description: null,
        type: null,
        environment: null,
        isActive: false,
        createdAt: '2025-03-16T08:00:00Z',
        updatedAt: '2025-03-16T08:00:00Z',
      });
    });

    it('normalizes non-string type and environment to null', async () => {
      mockGet.mockResolvedValue({
        data: {
          total: 1,
          items: [
            {
              id: 'config-3',
              config_key: 'mixed_config',
              description: 'Config with non-string values',
              is_active: true,
              config_data: {
                type: 123,
                environment: { nested: true },
              },
              created_at: '2025-03-17T10:00:00Z',
              updated_at: '2025-03-17T10:00:00Z',
            },
          ],
        },
      });

      const result = await getConfigurations({});

      expect(result.items[0].type).toBeNull();
      expect(result.items[0].environment).toBeNull();
    });
  });

  describe('getConfiguration', () => {
    it('fetches single configuration by id', async () => {
      mockGet.mockResolvedValue({
        data: {
          id: 'config-1',
          config_key: 'api_settings',
          description: 'API configuration',
          is_active: true,
          config_data: {
            type: 'api',
            environment: 'production',
            timeout: 30000,
            retries: 3,
          },
          created_at: '2025-03-15T10:00:00Z',
          updated_at: '2025-03-15T12:00:00Z',
        },
      });

      const result = await getConfiguration('config-1');

      expect(mockGet).toHaveBeenCalledWith('/v1/configurations/config-1', {
        params: { include_inactive: true },
      });

      expect(result).toEqual({
        id: 'config-1',
        configKey: 'api_settings',
        description: 'API configuration',
        type: 'api',
        environment: 'production',
        isActive: true,
        createdAt: '2025-03-15T10:00:00Z',
        updatedAt: '2025-03-15T12:00:00Z',
        configData: {
          type: 'api',
          environment: 'production',
          timeout: 30000,
          retries: 3,
        },
      });
    });

    it('handles null config_data', async () => {
      mockGet.mockResolvedValue({
        data: {
          id: 'config-2',
          config_key: 'empty_config',
          description: null,
          is_active: false,
          config_data: null,
          created_at: '2025-03-16T08:00:00Z',
          updated_at: '2025-03-16T08:00:00Z',
        },
      });

      const result = await getConfiguration('config-2');

      expect(result.configData).toEqual({});
    });
  });

  describe('updateConfiguration', () => {
    it('updates configuration with all fields', async () => {
      mockPatch.mockResolvedValue({
        data: {
          id: 'config-1',
          config_key: 'api_settings',
          description: 'Updated description',
          is_active: false,
          config_data: {
            type: 'api',
            environment: 'staging',
            timeout: 60000,
          },
          created_at: '2025-03-15T10:00:00Z',
          updated_at: '2025-03-18T14:00:00Z',
        },
      });

      const result = await updateConfiguration('config-1', {
        configData: {
          type: 'api',
          environment: 'staging',
          timeout: 60000,
        },
        description: 'Updated description',
        isActive: false,
      });

      expect(mockPatch).toHaveBeenCalledWith('/v1/configurations/config-1', {
        config_data: {
          type: 'api',
          environment: 'staging',
          timeout: 60000,
        },
        description: 'Updated description',
        is_active: false,
      });

      expect(result).toEqual({
        id: 'config-1',
        configKey: 'api_settings',
        description: 'Updated description',
        type: 'api',
        environment: 'staging',
        isActive: false,
        createdAt: '2025-03-15T10:00:00Z',
        updatedAt: '2025-03-18T14:00:00Z',
        configData: {
          type: 'api',
          environment: 'staging',
          timeout: 60000,
        },
      });
    });

    it('updates configuration with only configData', async () => {
      mockPatch.mockResolvedValue({
        data: {
          id: 'config-1',
          config_key: 'api_settings',
          description: 'Original description',
          is_active: true,
          config_data: { newField: 'value' },
          created_at: '2025-03-15T10:00:00Z',
          updated_at: '2025-03-18T15:00:00Z',
        },
      });

      await updateConfiguration('config-1', {
        configData: { newField: 'value' },
      });

      expect(mockPatch).toHaveBeenCalledWith('/v1/configurations/config-1', {
        config_data: { newField: 'value' },
        description: undefined,
        is_active: undefined,
      });
    });
  });

  describe('getConfigurationHistory', () => {
    it('fetches configuration history', async () => {
      mockGet.mockResolvedValue({
        data: {
          total: 2,
          items: [
            {
              id: 'history-1',
              configuration_id: 'config-1',
              config_key: 'api_settings',
              old_value: {
                config_key: 'api_settings',
                config_data: { timeout: 30000 },
                description: 'Old description',
                is_active: true,
              },
              new_value: {
                config_key: 'api_settings',
                config_data: { timeout: 60000 },
                description: 'New description',
                is_active: true,
              },
              changed_by: 'user-123',
              change_reason: 'Increased timeout',
              created_at: '2025-03-18T14:00:00Z',
            },
            {
              id: 'history-2',
              configuration_id: 'config-1',
              config_key: 'api_settings',
              old_value: null,
              new_value: {
                config_key: 'api_settings',
                config_data: { timeout: 30000 },
                description: 'Initial config',
                is_active: true,
              },
              changed_by: 'user-456',
              change_reason: null,
              created_at: '2025-03-15T10:00:00Z',
            },
          ],
        },
      });

      const result = await getConfigurationHistory('config-1');

      expect(mockGet).toHaveBeenCalledWith('/v1/configurations/config-1/history');

      expect(result).toEqual({
        total: 2,
        items: [
          {
            id: 'history-1',
            configurationId: 'config-1',
            configKey: 'api_settings',
            oldValue: {
              config_key: 'api_settings',
              config_data: { timeout: 30000 },
              description: 'Old description',
              is_active: true,
            },
            newValue: {
              config_key: 'api_settings',
              config_data: { timeout: 60000 },
              description: 'New description',
              is_active: true,
            },
            changedBy: 'user-123',
            changeReason: 'Increased timeout',
            createdAt: '2025-03-18T14:00:00Z',
          },
          {
            id: 'history-2',
            configurationId: 'config-1',
            configKey: 'api_settings',
            oldValue: null,
            newValue: {
              config_key: 'api_settings',
              config_data: { timeout: 30000 },
              description: 'Initial config',
              is_active: true,
            },
            changedBy: 'user-456',
            changeReason: null,
            createdAt: '2025-03-15T10:00:00Z',
          },
        ],
      });
    });

    it('handles empty history', async () => {
      mockGet.mockResolvedValue({
        data: {
          total: 0,
          items: [],
        },
      });

      const result = await getConfigurationHistory('config-2');

      expect(result).toEqual({
        total: 0,
        items: [],
      });
    });

    it('handles history entries with null values', async () => {
      mockGet.mockResolvedValue({
        data: {
          total: 1,
          items: [
            {
              id: 'history-3',
              configuration_id: 'config-3',
              config_key: null,
              old_value: undefined,
              new_value: {
                config_key: 'test',
                config_data: null,
                description: null,
                is_active: false,
              },
              changed_by: null,
              change_reason: null,
              created_at: '2025-03-19T08:00:00Z',
            },
          ],
        },
      });

      const result = await getConfigurationHistory('config-3');

      expect(result.items[0].configKey).toBeNull();
      expect(result.items[0].oldValue).toBeNull();
      expect(result.items[0].newValue).toEqual({
        config_key: 'test',
        config_data: null,
        description: null,
        is_active: false,
      });
    });
  });
});
