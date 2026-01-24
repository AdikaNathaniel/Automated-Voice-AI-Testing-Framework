/**
 * Configuration domain types.
 */

export type ConfigurationRecord = {
  id: string;
  configKey: string;
  description: string | null;
  type: string | null;
  environment: string | null;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
};

export type ConfigurationListResponse = {
  total: number;
  items: ConfigurationRecord[];
};

export type ConfigurationListParams = {
  type: string | null;
  environment: string | null;
  includeInactive?: boolean;
};

export type ConfigurationDetail = ConfigurationRecord & {
  configData: Record<string, unknown>;
};

export type ConfigurationUpdateInput = {
  configData: Record<string, unknown>;
  description?: string | null;
  isActive?: boolean;
};

export type ConfigurationHistorySnapshot = {
  config_key?: string | null;
  config_data?: Record<string, unknown> | null;
  description?: string | null;
  is_active?: boolean | null;
};

export type ConfigurationHistoryEntry = {
  id: string;
  configurationId: string;
  configKey: string | null;
  oldValue: ConfigurationHistorySnapshot | null;
  newValue: ConfigurationHistorySnapshot | null;
  changedBy: string | null;
  changeReason: string | null;
  createdAt: string;
};

export type ConfigurationHistoryResponse = {
  total: number;
  items: ConfigurationHistoryEntry[];
};
