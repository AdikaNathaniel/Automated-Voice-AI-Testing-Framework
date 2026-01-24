/**
 * Configuration Tabs Barrel Export
 *
 * Most tab components have been removed as those features are now accessed
 * via their dedicated nav pages which provide full functionality:
 * - IntegrationsTab → /integrations
 * - CICDTab → /cicd-config
 * - NotificationsTab → /integrations/slack
 *
 * LLMProvidersTab is kept but currently hidden.
 */

export { default as LLMProvidersTab } from './LLMProvidersTab';
