"""
Configuration SQLAlchemy model for system configuration management

This module defines the Configuration model which represents system
configurations for the automated testing framework.

The Configuration model includes:
    - Configuration key: Unique identifier for the configuration
    - Configuration data: JSONB field for flexible configuration storage
    - Configuration management: Methods for getting and setting config values

Example:
    >>> from models.configuration import Configuration
    >>>
    >>> # Create configuration
    >>> config = Configuration(
    ...     config_key="smtp_settings"
    ... )
    >>>
    >>> # Set configuration values
    >>> config.set_config("host", "smtp.example.com")
    >>> config.set_config("port", 587)
    >>>
    >>> # Get individual config values
    >>> print(config.get_config("host"))
    'smtp.example.com'
    >>>
    >>> # Get all config data
    >>> data = config.get_all_config()
    >>> print(data)
    {'host': 'smtp.example.com', 'port': 587}
"""

from typing import Optional, Dict, Any

from sqlalchemy import Column, String, JSON, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects import postgresql


from models.base import Base, BaseModel, GUID

CONFIG_DATA_TYPE = postgresql.JSONB().with_variant(JSON(), "sqlite")


class Configuration(Base, BaseModel):
    """
    Configuration model for storing system configurations.

    Represents a configuration with a unique key and flexible JSONB data field
    for storing configuration values.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        config_key (str): Unique configuration key, required
        config_data (Dict, optional): Configuration data in JSON format
        created_at (datetime): Creation timestamp (inherited)
        updated_at (datetime): Last update timestamp (inherited)

    Example:
        >>> config = Configuration(config_key="smtp_settings")
        >>> config.set_config("host", "smtp.example.com")
        >>> config.set_config("port", 587)
        >>> print(config.get_config("host"))
        'smtp.example.com'
        >>> print(config.get_all_config())
        {'host': 'smtp.example.com', 'port': 587}

    Note:
        - config_key must be unique across all configurations
        - config_data is nullable and can store flexible key-value data
        - Helper methods initialize config_data as empty dict if None
    """

    __tablename__ = 'configurations'
    __table_args__ = (
        UniqueConstraint('tenant_id', 'config_key', name='uq_configuration_tenant_key'),
    )

    tenant_id = Column(
        GUID(),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Tenant (organization or user) that owns this configuration"
    )

    # Configuration key (unique per tenant)
    config_key = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Configuration key (unique per tenant)"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Optional description for administrators"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the configuration is active"
    )

    # JSONB field for flexible configuration data
    config_data = Column(
        CONFIG_DATA_TYPE,
        nullable=True,
        comment="Configuration data in JSON format"
    )

    def __repr__(self) -> str:
        """
        String representation of Configuration instance.

        Returns:
            String with config_key

        Example:
            >>> config = Configuration(config_key="smtp_settings")
            >>> print(config)
            <Configuration(config_key='smtp_settings')>
        """
        return f"<Configuration(config_key='{self.config_key}')>"

    # Configuration data helper methods
    def set_config(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration value key
            value: Configuration value

        Example:
            >>> config = Configuration(config_key="smtp_settings")
            >>> config.set_config("host", "smtp.example.com")
            >>> config.config_data
            {'host': 'smtp.example.com'}

        Note:
            After using this method, you must call flag_modified() from the
            service layer to ensure SQLAlchemy detects the JSONB change:

            from sqlalchemy.orm.attributes import flag_modified
            config.set_config("key", "value")
            flag_modified(config, "config_data")
        """
        if self.config_data is None:
            self.config_data = {}
        # Create new dict to help SQLAlchemy detect changes
        new_data = dict(self.config_data)
        new_data[key] = value
        self.config_data = new_data

    def get_config(self, key: str) -> Optional[Any]:
        """
        Get a configuration value.

        Args:
            key: Configuration value key

        Returns:
            Configuration value or None if not found

        Example:
            >>> config = Configuration(config_key="smtp_settings")
            >>> config.set_config("host", "smtp.example.com")
            >>> config.get_config("host")
            'smtp.example.com'
            >>> config.get_config("nonexistent")
            None
        """
        if self.config_data is None:
            return None
        return self.config_data.get(key)

    def get_all_config(self) -> Dict[str, Any]:
        """
        Get all configuration data.

        Returns:
            Dictionary of all configuration data, empty dict if none set

        Example:
            >>> config = Configuration(config_key="smtp_settings")
            >>> config.set_config("host", "smtp.example.com")
            >>> config.set_config("port", 587)
            >>> config.get_all_config()
            {'host': 'smtp.example.com', 'port': 587}
        """
        if self.config_data is None:
            return {}
        return dict(self.config_data)
