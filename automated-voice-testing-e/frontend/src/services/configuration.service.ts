/**
 * Configuration service helpers.
 *
 * Provides access to configuration listing endpoints.
 */

import apiClient from './api';
import type {
  ConfigurationDetail,
  ConfigurationHistoryEntry,
  ConfigurationHistoryResponse,
  ConfigurationListParams,
  ConfigurationListResponse,
  ConfigurationRecord,
  ConfigurationUpdateInput,
} from '../types/configuration';

type ApiConfigurationRecord = {
  id: string;
  config_key: string;
  description: string | null;
  is_active: boolean;
  config_data: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

type ApiConfigurationListResponse = {
  total: number;
  items: ApiConfigurationRecord[];
};

const normalizeString = (value: unknown): string | null => {
  if (typeof value === 'string') {
    return value || null;
  }
  return null;
};

const toConfigurationRecord = (payload: ApiConfigurationRecord): ConfigurationRecord => {
  const configData = payload.config_data ?? {};
  const typeValue = normalizeString((configData as Record<string, unknown>).type);
  const environmentValue = normalizeString((configData as Record<string, unknown>).environment);

  return {
    id: payload.id,
    configKey: payload.config_key,
    description: payload.description,
    type: typeValue,
    environment: environmentValue,
    isActive: Boolean(payload.is_active),
    createdAt: payload.created_at,
    updatedAt: payload.updated_at,
  };
};

export const getConfigurations = async (
  params: ConfigurationListParams
): Promise<ConfigurationListResponse> => {
  const response = await apiClient.get<ApiConfigurationListResponse>('/configurations', {
    params: {
      type: params.type ?? undefined,
      environment: params.environment ?? undefined,
      include_inactive: params.includeInactive ?? false,
    },
  });

  return {
    total: response.data.total,
    items: response.data.items.map(toConfigurationRecord),
  };
};

export const getConfiguration = async (configId: string): Promise<ConfigurationDetail> => {
  const response = await apiClient.get<ApiConfigurationRecord>(`/v1/configurations/${configId}`, {
    params: { include_inactive: true },
  });

  const record = toConfigurationRecord(response.data);
  return {
    ...record,
    configData: (response.data.config_data as Record<string, unknown> | null) ?? {},
  };
};

export const updateConfiguration = async (
  configId: string,
  payload: ConfigurationUpdateInput
): Promise<ConfigurationDetail> => {
  const response = await apiClient.patch<ApiConfigurationRecord>(
    `/v1/configurations/${configId}`,
    {
      config_data: payload.configData,
      description: payload.description ?? undefined,
      is_active: payload.isActive ?? undefined,
    }
  );

  const record = toConfigurationRecord(response.data);
  return {
    ...record,
    configData: (response.data.config_data as Record<string, unknown> | null) ?? {},
  };
};

const mapHistorySnapshot = (snapshot: unknown | null | undefined) => {
  if (!snapshot) {
    return null;
  }
  const configData =
    snapshot && typeof snapshot.config_data === 'object' && snapshot.config_data !== null
      ? (snapshot.config_data as Record<string, unknown>)
      : null;

  return {
    config_key: typeof snapshot.config_key === 'string' ? snapshot.config_key : null,
    config_data: configData,
    description:
      typeof snapshot.description === 'string'
        ? snapshot.description
        : snapshot.description ?? null,
    is_active:
      typeof snapshot.is_active === 'boolean'
        ? snapshot.is_active
        : snapshot.is_active === true
        ? true
        : snapshot.is_active === false
        ? false
        : null,
  };
};

export const getConfigurationHistory = async (
  configId: string
): Promise<ConfigurationHistoryResponse> => {
  const response = await apiClient.get<{
    total: number;
    items: Array<{
      id: string;
      configuration_id: string;
      config_key: string | null;
      old_value: unknown;
      new_value: unknown;
      changed_by: string | null;
      change_reason: string | null;
      created_at: string;
    }>;
  }>(
    `/v1/configurations/${configId}/history`
  );

  const items: ConfigurationHistoryEntry[] = response.data.items.map((entry) => ({
    id: entry.id,
    configurationId: entry.configuration_id,
    configKey: entry.config_key,
    oldValue: mapHistorySnapshot(entry.old_value),
    newValue: mapHistorySnapshot(entry.new_value),
    changedBy: entry.changed_by,
    changeReason: entry.change_reason,
    createdAt: entry.created_at,
  }));

  return { total: response.data.total, items };
};

export default {
  getConfigurations,
  getConfiguration,
  updateConfiguration,
  getConfigurationHistory,
};
