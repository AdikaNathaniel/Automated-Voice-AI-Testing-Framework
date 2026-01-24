"""
Voice AI Testing Framework - Application Configuration
Centralized configuration management using Pydantic Settings
"""

from typing import Any, List, Optional
from pydantic import Field, field_validator, ValidationInfo, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import json


def _normalize_regression_suite_ids(value: Any) -> list[str]:
    """
    Normalize regression suite identifiers from environment values.

    Supports:
        - JSON arrays (["id1", "id2"])
        - Comma separated strings ("id1,id2")
        - Iterables of identifiers
    """
    if value in (None, "", []):
        return []

    candidates: list[Any]

    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            decoded = None

        if isinstance(decoded, (list, tuple, set)):
            candidates = list(decoded)
        elif isinstance(decoded, str):
            candidates = [decoded]
        else:
            candidates = value.split(",")
    elif isinstance(value, (list, tuple, set)):
        candidates = list(value)
    else:
        candidates = [value]

    normalized: list[str] = []
    for item in candidates:
        if item is None:
            continue
        text = str(item).strip()
        if text:
            normalized.append(text)

    return normalized


def _parse_settings_env_var(field_name: str, raw_value: Any) -> Any:
    """
    Custom parser for environment variables to support friendly formats.
    """
    if field_name == "REGRESSION_SUITE_IDS":
        return _normalize_regression_suite_ids(raw_value)
    # Don't try to parse REPORT_EMAIL_RECIPIENTS as JSON - let the field validator handle it
    if field_name == "REPORT_EMAIL_RECIPIENTS":
        return raw_value
    return raw_value


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables

    All settings are loaded from environment variables, with support for .env files.
    Required fields will raise ValidationError if not provided.
    """

    # ========================================================================
    # Database Configuration
    # ========================================================================

    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL database connection URL",
        examples=["postgresql://user:password@localhost:5432/voice_ai_testing"]
    )

    READ_REPLICA_URL: Optional[str] = Field(
        default=None,
        description="Optional PostgreSQL read replica connection URL"
    )

    DB_HOST: Optional[str] = Field(
        default="localhost",
        description="Database host"
    )

    DB_PORT: Optional[int] = Field(
        default=5432,
        description="Database port"
    )

    DB_NAME: Optional[str] = Field(
        default="voice_ai_testing",
        description="Database name"
    )

    DB_USER: Optional[str] = Field(
        default="voice_ai_user",
        description="Database user"
    )

    DB_PASSWORD: Optional[str] = Field(
        default=None,
        description="Database password"
    )

    DB_POOL_SIZE: int = Field(
        default=20,
        description="Database connection pool size"
    )

    DB_MAX_OVERFLOW: int = Field(
        default=10,
        description="Database max overflow connections"
    )

    DB_POOL_TIMEOUT: int = Field(
        default=30,
        description="Database connection pool timeout in seconds"
    )

    DB_POOL_RECYCLE: int = Field(
        default=3600,
        description="Database connection recycle interval in seconds"
    )

    # ========================================================================
    # Redis Configuration
    # ========================================================================

    REDIS_URL: str = Field(
        ...,
        description="Redis connection URL",
        examples=["redis://localhost:6379/0"]
    )

    REDIS_HOST: Optional[str] = Field(
        default="localhost",
        description="Redis host"
    )

    REDIS_PORT: Optional[int] = Field(
        default=6379,
        description="Redis port"
    )

    REDIS_DB: Optional[int] = Field(
        default=0,
        description="Redis database number"
    )

    REDIS_PASSWORD: Optional[str] = Field(
        default=None,
        description="Redis password"
    )

    REDIS_MAX_CONNECTIONS: int = Field(
        default=50,
        description="Redis max connections in pool"
    )

    CACHE_TTL: int = Field(
        default=3600,
        description="Cache TTL (time-to-live) in seconds"
    )

    # ========================================================================
    # JWT Authentication Configuration
    # ========================================================================

    JWT_SECRET_KEY: str = Field(
        ...,
        description="JWT secret key for token signing",
        min_length=16
    )

    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )

    JWT_EXPIRATION_MINUTES: int = Field(
        default=30,
        description="JWT access token expiration time in minutes"
    )

    JWT_REFRESH_EXPIRATION_DAYS: int = Field(
        default=14,
        description="JWT refresh token expiration in days"
    )

    PASSWORD_HASH_ROUNDS: int = Field(
        default=12,
        description="Password hashing algorithm rounds"
    )

    # ========================================================================
    # Rate Limiting Configuration
    # ========================================================================

    RATE_LIMIT_DEFAULT_REQUESTS: int = Field(
        default=100,
        description="Default rate limit requests per window"
    )

    RATE_LIMIT_DEFAULT_WINDOW: int = Field(
        default=60,
        description="Default rate limit window in seconds"
    )

    RATE_LIMIT_AUTH_REQUESTS: int = Field(
        default=10,
        description="Auth endpoint rate limit requests per window"
    )

    RATE_LIMIT_AUTH_WINDOW: int = Field(
        default=60,
        description="Auth endpoint rate limit window in seconds"
    )

    RATE_LIMIT_TRUSTED_PROXIES: str = Field(
        default="127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16",
        description="Comma-separated list of trusted proxy IPs/CIDRs for X-Forwarded-For"
    )

    # ========================================================================
    # SoundHound Voice AI Configuration
    # ========================================================================

    SOUNDHOUND_API_KEY: str = Field(
        ...,
        description="SoundHound API key"
    )

    SOUNDHOUND_CLIENT_ID: str = Field(
        ...,
        description="SoundHound client ID"
    )

    SOUNDHOUND_ENDPOINT: str = Field(
        default="https://api.houndify.com/v1",
        description="Houndify API endpoint (SoundHound's voice AI platform)"
    )

    SOUNDHOUND_TIMEOUT: int = Field(
        default=10,
        description="SoundHound request timeout in seconds"
    )

    SOUNDHOUND_MAX_RETRIES: int = Field(
        default=3,
        description="SoundHound max retries"
    )

    USE_HOUNDIFY_MOCK: bool = Field(
        default=True,
        description="Use mock Houndify client instead of real API (for development/testing)"
    )

    HOUNDIFY_SAMPLE_RATE: int = Field(
        default=16000,
        description="Audio sample rate for Houndify (8000 or 16000 Hz)"
    )

    # ========================================================================
    # AWS Configuration
    # ========================================================================

    AWS_ACCESS_KEY_ID: str = Field(
        ...,
        description="AWS access key ID"
    )

    AWS_SECRET_ACCESS_KEY: str = Field(
        ...,
        description="AWS secret access key"
    )

    AWS_REGION: str = Field(
        default="us-east-1",
        description="AWS region"
    )

    AWS_S3_BUCKET: Optional[str] = Field(
        default="voice-ai-testing-artifacts",
        description="AWS S3 bucket name for storing test artifacts"
    )

    S3_OBJECT_EXPIRATION_DAYS: int = Field(
        default=90,
        description="S3 object expiration in days"
    )

    # ========================================================================
    # MinIO Configuration (Local Development)
    # ========================================================================

    STORAGE_BACKEND: str = Field(
        default="minio",
        description="Storage backend: 's3' for AWS S3, 'minio' for local MinIO"
    )

    MINIO_ENDPOINT_URL: Optional[str] = Field(
        default="http://localhost:9000",
        description="MinIO endpoint URL for local development"
    )

    MINIO_ACCESS_KEY: Optional[str] = Field(
        default="minioadmin",
        description="MinIO access key"
    )

    MINIO_SECRET_KEY: Optional[str] = Field(
        default="minioadmin",
        description="MinIO secret key"
    )

    MINIO_REGION: str = Field(
        default="us-east-1",
        description="MinIO region (can be any value for MinIO)"
    )

    MINIO_AUDIO_BUCKET: str = Field(
        default="voice-ai-testing-audio",
        description="MinIO bucket name for audio files"
    )

    # ========================================================================
    # Reporting Configuration
    # ========================================================================

    REPORT_EMAIL_RECIPIENTS: List[str] = Field(
        default_factory=list,
        description="Comma-separated list of recipients for scheduled reports",
    )

    REPORT_EMAIL_SENDER: Optional[str] = Field(
        default=None,
        description="Email address used as the sender for scheduled reports",
    )

    REPORT_EMAIL_SMTP_HOST: Optional[str] = Field(
        default=None,
        description="SMTP server hostname used for emailing scheduled reports",
    )

    REPORT_EMAIL_SMTP_PORT: int = Field(
        default=587,
        description="SMTP server port used for scheduled report emails",
    )

    REPORT_EMAIL_SMTP_USERNAME: Optional[str] = Field(
        default=None,
        description="SMTP username for scheduled report email authentication",
    )

    REPORT_EMAIL_SMTP_PASSWORD: Optional[str] = Field(
        default=None,
        description="SMTP password for scheduled report email authentication",
    )

    REPORT_EMAIL_USE_TLS: bool = Field(
        default=True,
        description="Enable STARTTLS when sending scheduled report emails",
    )

    REPORT_EMAIL_TIMEOUT: int = Field(
        default=30,
        description="Timeout in seconds for sending scheduled report emails",
    )

    # ========================================================================
    # Application Configuration
    # ========================================================================

    ENVIRONMENT: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )

    APP_NAME: str = Field(
        default="Voice AI Testing Framework",
        description="Application name"
    )

    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )

    LOG_LEVEL: str = Field(
        default="INFO",
        description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )

    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    TENANCY_MODE: str = Field(
        default="soft_multi_tenant",
        description="Tenancy model: single_tenant or soft_multi_tenant"
    )

    # ========================================================================
    # Sentry Error Tracking
    # ========================================================================

    SENTRY_DSN: Optional[str] = Field(
        default=None,
        description="Sentry DSN for error tracking (only enabled in production/staging)"
    )

    SENTRY_SAMPLE_RATE: float = Field(
        default=1.0,
        description="Sentry traces sample rate (0.0 to 1.0)"
    )

    # ========================================================================
    # Auto-scaling Configuration
    # ========================================================================

    ENABLE_AUTO_SCALING: bool = Field(
        default=False,
        description="Enable Celery worker auto-scaling"
    )

    MIN_WORKERS: int = Field(
        default=1,
        description="Minimum Celery worker processes"
    )

    MAX_WORKERS: int = Field(
        default=10,
        description="Maximum Celery worker processes"
    )

    AUTO_SCALING_TARGET_TASKS_PER_WORKER: int = Field(
        default=10,
        description="Number of queued tasks per worker before scaling up"
    )

    AUTO_SCALING_SCALE_DOWN_THRESHOLD: int = Field(
        default=0,
        description="Queue depth threshold to scale back to minimum workers"
    )

    AUTO_SCALING_COOLDOWN_SECONDS: int = Field(
        default=30,
        description="Cooldown window between scaling actions in seconds"
    )

    AUTO_SCALING_QUEUE_NAME: str = Field(
        default="default",
        description="Celery queue name monitored for auto-scaling"
    )

    # ========================================================================
    # Regression Automation Configuration
    # ========================================================================

    ENABLE_AUTO_REGRESSION: bool = Field(
        default=False,
        description="Enable automatic execution of regression test suites",
    )

    REGRESSION_SUITE_IDS: List[str] = Field(
        default_factory=list,
        description="List of regression suite UUIDs to execute when automation is triggered",
    )

    # ========================================================================
    # Execution Engine Configuration
    # ========================================================================

    EXECUTION_CPU_LIMIT_PERCENT: Optional[float] = Field(
        default=85.0,
        description="Maximum CPU percent allowed for execution tasks (None to disable)"
    )

    EXECUTION_MEMORY_LIMIT_MB: Optional[int] = Field(
        default=2048,
        description="Maximum memory usage in MB for execution tasks (None to disable)"
    )

    # ========================================================================
    # GitHub OAuth Configuration
    # ========================================================================

    GITHUB_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="GitHub OAuth App Client ID"
    )

    GITHUB_CLIENT_SECRET: Optional[str] = Field(
        default=None,
        description="GitHub OAuth App Client Secret"
    )

    GITHUB_REDIRECT_URI: str = Field(
        default="http://localhost:8000/api/v1/integrations/github/callback",
        description="GitHub OAuth redirect URI (must match OAuth App settings)"
    )

    # ========================================================================
    # CI/CD Webhook Configuration
    # ========================================================================

    GITHUB_WEBHOOK_SECRET: Optional[str] = Field(
        default=None,
        description="Shared secret used to validate GitHub webhook signatures"
    )

    GITHUB_WEBHOOK_SECRET_PREVIOUS: Optional[str] = Field(
        default=None,
        description="Previous GitHub webhook secret for rotation support"
    )

    GITLAB_WEBHOOK_SECRET: Optional[str] = Field(
        default=None,
        description="Token used to validate GitLab webhook requests"
    )

    GITLAB_WEBHOOK_SECRET_PREVIOUS: Optional[str] = Field(
        default=None,
        description="Previous GitLab webhook secret for rotation support"
    )

    JENKINS_WEBHOOK_SECRET: Optional[str] = Field(
        default=None,
        description="Shared secret used to validate Jenkins webhook signatures"
    )

    JENKINS_WEBHOOK_SECRET_PREVIOUS: Optional[str] = Field(
        default=None,
        description="Previous Jenkins webhook secret for rotation support"
    )

    # ========================================================================
    # API Server Configuration
    # ========================================================================

    API_HOST: str = Field(
        default="0.0.0.0",
        description="API server host"
    )

    API_PORT: int = Field(
        default=8000,
        description="API server port"
    )

    API_TIMEOUT: int = Field(
        default=30,
        description="API request timeout in seconds"
    )

    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend URL for CORS"
    )

    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Allowed CORS origins (comma-separated)"
    )

    # ========================================================================
    # Testing Configuration
    # ========================================================================

    TEST_EXECUTION_TIMEOUT: int = Field(
        default=300,
        description="Test execution timeout in seconds"
    )

    MAX_CONCURRENT_TESTS: int = Field(
        default=10,
        description="Maximum concurrent test executions"
    )

    TEST_RESULT_RETENTION_DAYS: int = Field(
        default=90,
        description="Test result retention period in days"
    )

    # ========================================================================
    # Validation Configuration
    # ========================================================================

    VALIDATION_ACCURACY_THRESHOLD: float = Field(
        default=0.997,
        description="Validation accuracy threshold (0.0 - 1.0)"
    )

    SIMILARITY_THRESHOLD: float = Field(
        default=0.85,
        description="Similarity score threshold (0.0 - 1.0)"
    )

    ENABLE_HUMAN_VALIDATION: bool = Field(
        default=True,
        description="Enable human validation for low confidence results"
    )

    # ========================================================================
    # Houndify Validation Configuration
    # ========================================================================

    DEFAULT_SEMANTIC_SIMILARITY_THRESHOLD: float = Field(
        default=0.75,
        description="Default semantic similarity threshold (0.0 - 1.0)"
    )

    DEFAULT_INTENT_MATCH_THRESHOLD: float = Field(
        default=0.85,
        description="Default intent classification match threshold (0.0 - 1.0)"
    )

    DEFAULT_ENTITY_MATCH_THRESHOLD: float = Field(
        default=0.80,
        description="Default entity extraction match threshold (0.0 - 1.0)"
    )

    DEFAULT_WER_THRESHOLD: float = Field(
        default=0.15,
        description="Default Word Error Rate threshold (lower is better)"
    )

    DEFAULT_CER_THRESHOLD: float = Field(
        default=0.10,
        description="Default Character Error Rate threshold (lower is better)"
    )

    DEFAULT_CONFIDENCE_AUTO_PASS: float = Field(
        default=0.90,
        description="Confidence score threshold for automatic pass (0.0 - 1.0)"
    )

    DEFAULT_CONFIDENCE_NEEDS_REVIEW: float = Field(
        default=0.70,
        description="Confidence score threshold for needs review (0.0 - 1.0)"
    )

    DEFAULT_ASR_CONFIDENCE_MIN: float = Field(
        default=0.80,
        description="Default minimum ASR confidence score from Houndify (0.0 - 1.0)"
    )

    DEFAULT_COMMAND_KIND_MATCH_REQUIRED: bool = Field(
        default=True,
        description="Whether CommandKind must match expected value"
    )

    DEFAULT_NATIVE_DATA_VALIDATION_ENABLED: bool = Field(
        default=True,
        description="Enable validation of Houndify NativeData fields"
    )

    ENFORCE_COMMAND_INTENT_CONSISTENCY: bool = Field(
        default=True,
        description="Validate that extracted intent is consistent with CommandKind"
    )

    # ========================================================================
    # Slack Notification Configuration
    # ========================================================================

    SLACK_WEBHOOK_URL: Optional[str] = Field(
        default=None,
        description="Slack incoming webhook URL for notifications"
    )

    SLACK_ALERT_CHANNEL: Optional[str] = Field(
        default=None,
        description="Default Slack channel for alerts (e.g., #voice-ai-alerts)"
    )

    SLACK_EDGE_CASE_CHANNEL: Optional[str] = Field(
        default=None,
        description="Slack channel for edge case notifications (defaults to SLACK_ALERT_CHANNEL)"
    )

    SLACK_NOTIFICATIONS_ENABLED: bool = Field(
        default=True,
        description="Enable/disable Slack notifications globally"
    )

    # ========================================================================
    # Knowledge Base Generation Configuration
    # ========================================================================

    KB_GENERATION_LLM_PROVIDER: Optional[str] = Field(
        default=None,
        description="LLM provider for KB article generation: openai, anthropic, google, or openrouter. "
                    "If not set, uses template-based generation."
    )

    KB_GENERATION_LLM_MODEL: Optional[str] = Field(
        default=None,
        description="LLM model for KB article generation. If not set, uses provider default "
                    "(gpt-4o for OpenAI, claude-sonnet-4-5 for Anthropic, gemini-1.5-pro for Google)."
    )

    # ========================================================================
    # OpenRouter / Pattern Analysis LLM Configuration
    # ========================================================================

    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1",
        description="Base URL for OpenRouter API"
    )

    OPENROUTER_API_KEY: Optional[str] = Field(
        default=None,
        description="API key for OpenRouter. If not set, LLM-enhanced pattern analysis is disabled."
    )

    LLM_CURATOR_MODEL: str = Field(
        default="anthropic/claude-sonnet-4-20250514",
        description="LLM model for pattern analysis and curation"
    )

    SEMANTIC_SIMILARITY_MODEL: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence transformer model for semantic similarity matching in edge case clustering"
    )

    # ========================================================================
    # Validators
    # ========================================================================

    @field_validator('ENVIRONMENT')
    @classmethod
    def validate_environment(cls, v):
        """Validate that ENVIRONMENT is one of the allowed values"""
        allowed = ['development', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f'ENVIRONMENT must be one of {allowed}, got {v}')
        return v

    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        """Validate that LOG_LEVEL is one of the allowed values"""
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f'LOG_LEVEL must be one of {allowed}, got {v}')
        return v.upper()

    @field_validator('MIN_WORKERS', 'AUTO_SCALING_SCALE_DOWN_THRESHOLD', 'AUTO_SCALING_COOLDOWN_SECONDS')
    @classmethod
    def validate_non_negative(cls, v):
        """Ensure scaling configuration values are non-negative"""
        if v < 0:
            raise ValueError('Value must be non-negative')
        return v

    @field_validator('REPORT_EMAIL_RECIPIENTS', mode='before')
    @classmethod
    def parse_report_recipients(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return list(value)

    @field_validator('MAX_WORKERS')
    @classmethod
    def validate_max_workers(cls, v, info: ValidationInfo):
        """Ensure MAX_WORKERS is >= MIN_WORKERS and positive"""
        if v < 1:
            raise ValueError('MAX_WORKERS must be at least 1')
        min_workers = info.data.get('MIN_WORKERS')
        if min_workers is not None and v < min_workers:
            raise ValueError('MAX_WORKERS must be greater than or equal to MIN_WORKERS')
        return v

    @field_validator('AUTO_SCALING_TARGET_TASKS_PER_WORKER')
    @classmethod
    def validate_tasks_per_worker(cls, v):
        """Ensure tasks per worker is positive"""
        if v <= 0:
            raise ValueError('AUTO_SCALING_TARGET_TASKS_PER_WORKER must be positive')
        return v

    @field_validator('EXECUTION_CPU_LIMIT_PERCENT')
    @classmethod
    def validate_cpu_limit(cls, v):
        """Ensure CPU limit is within sensible bounds"""
        if v is None:
            return v
        if v <= 0 or v > 100:
            raise ValueError('EXECUTION_CPU_LIMIT_PERCENT must be between 0 and 100')
        return v

    @field_validator('EXECUTION_MEMORY_LIMIT_MB')
    @classmethod
    def validate_memory_limit(cls, v):
        """Ensure memory limit is positive"""
        if v is None:
            return v
        if v <= 0:
            raise ValueError('EXECUTION_MEMORY_LIMIT_MB must be positive when set')
        return v

    @field_validator('JWT_SECRET_KEY')
    @classmethod
    def validate_jwt_secret_key(cls, v):
        """Validate that JWT_SECRET_KEY is strong enough"""
        if len(v) < 16:
            raise ValueError('JWT_SECRET_KEY must be at least 16 characters long')
        return v

    @field_validator(
        'VALIDATION_ACCURACY_THRESHOLD',
        'SIMILARITY_THRESHOLD',
        'DEFAULT_SEMANTIC_SIMILARITY_THRESHOLD',
        'DEFAULT_INTENT_MATCH_THRESHOLD',
        'DEFAULT_ENTITY_MATCH_THRESHOLD',
        'DEFAULT_WER_THRESHOLD',
        'DEFAULT_CER_THRESHOLD',
        'DEFAULT_CONFIDENCE_AUTO_PASS',
        'DEFAULT_CONFIDENCE_NEEDS_REVIEW',
        'DEFAULT_ASR_CONFIDENCE_MIN'
    )
    @classmethod
    def validate_threshold(cls, v):
        """Validate that threshold is between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError('Threshold must be between 0 and 1')
        return v

    @field_validator('TENANCY_MODE')
    @classmethod
    def validate_tenancy_mode(cls, value: str) -> str:
        allowed = {"single_tenant", "soft_multi_tenant"}
        if value not in allowed:
            raise ValueError("TENANCY_MODE must be one of: single_tenant, soft_multi_tenant")
        return value

    @field_validator('KB_GENERATION_LLM_PROVIDER')
    @classmethod
    def validate_kb_llm_provider(cls, v):
        """Validate KB generation LLM provider is supported"""
        if v is None:
            return v
        allowed = {'openai', 'anthropic', 'google', 'openrouter'}
        v_lower = v.lower()
        if v_lower not in allowed:
            raise ValueError(f'KB_GENERATION_LLM_PROVIDER must be one of {allowed}, got {v}')
        return v_lower

    @field_validator("REGRESSION_SUITE_IDS", mode="before")
    @classmethod
    def parse_regression_suite_ids(cls, value):
        """
        Parse regression suite identifiers from supported input formats.
        """
        return _normalize_regression_suite_ids(value)

    @model_validator(mode="after")
    def ensure_non_dev_jwt_secret(self):
        """Prevent placeholder secrets outside development."""
        env_value = (self.ENVIRONMENT or "").lower()
        if env_value not in {"development", "dev", "local"}:
            secret_lower = self.JWT_SECRET_KEY.lower()
            placeholder_tokens = {
                "changeme",
                "default",
                "dev",
                "test",
                "secret",
                "example",
                "placeholder",
                "sample",
            }
            if any(token in secret_lower for token in placeholder_tokens):
                raise ValueError(
                    "JWT_SECRET_KEY must be a unique, non-placeholder value outside development environments"
                )
        return self


    # ========================================================================
    # Model Configuration
    # ========================================================================

    model_config = SettingsConfigDict(
        # Load from .env file
        env_file=".env",
        env_file_encoding="utf-8",
        # Case sensitive environment variables
        case_sensitive=True,
        # Extra fields are ignored (allows undefined env vars without errors)
        extra="ignore",
        # Don't try to parse complex types as JSON from env vars
        env_parse_none_str="null",
        parse_env_var=_parse_settings_env_var,
    )

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def get_database_url(self) -> str:
        """Get the database URL"""
        return self.DATABASE_URL

    def get_redis_url(self) -> str:
        """Get the Redis URL"""
        return self.REDIS_URL

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT == "development"

    def get_cors_origins(self) -> list[str]:
        """Get list of allowed CORS origins"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# ============================================================================
# Singleton Settings Instance
# ============================================================================

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (singleton)

    This function is cached to ensure only one Settings instance is created.
    Use this function to access settings throughout the application.

    Returns:
        Settings: Application settings instance

    Example:
        ```python
        from api.config import get_settings

        settings = get_settings()
        database_url = settings.DATABASE_URL
        ```
    """
    return Settings()


# ============================================================================
# Export for convenience
# ============================================================================

__all__ = ["Settings", "get_settings"]
