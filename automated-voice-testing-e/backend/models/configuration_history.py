"""
ConfigurationHistory SQLAlchemy model for tracking configuration changes

This module defines the ConfigurationHistory model which represents historical
records of configuration changes in the automated testing framework.

The ConfigurationHistory model includes:
    - Configuration reference: Foreign key to the configuration that was changed
    - Configuration key: Denormalized config_key for historical record
    - Old value: JSONB field storing the previous configuration state
    - New value: JSONB field storing the new configuration state
    - Changed by: Foreign key to the user who made the change
    - Change tracking: Methods for accessing historical configuration data

Example:
    >>> from models.configuration_history import ConfigurationHistory
    >>> from datetime import datetime
    >>>
    >>> # Create history entry
    >>> history = ConfigurationHistory(
    ...     configuration_id=config_uuid,
    ...     config_key="smtp_settings",
    ...     changed_by=user_uuid
    ... )
    >>>
    >>> # Set old and new values
    >>> history.set_old_value("host", "old.smtp.example.com")
    >>> history.set_new_value("host", "new.smtp.example.com")
    >>>
    >>> # Get individual values
    >>> print(history.get_old_value("host"))
    'old.smtp.example.com'
    >>> print(history.get_new_value("host"))
    'new.smtp.example.com'
    >>>
    >>> # Get all values
    >>> old_data = history.get_all_old_value()
    >>> new_data = history.get_all_new_value()
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import Column, String, ForeignKey, JSON, Text
from sqlalchemy.dialects import postgresql

from sqlalchemy.orm import relationship, remote

from models.base import Base, BaseModel, GUID

JSONB_VARIANT = postgresql.JSONB().with_variant(JSON(), "sqlite")

if TYPE_CHECKING:
    pass


class ConfigurationHistory(Base, BaseModel):
    """
    ConfigurationHistory model for tracking configuration changes.

    Represents a historical record of a configuration change with old and new
    values stored in JSONB fields for flexible data comparison.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        created_at (datetime): Creation timestamp (inherited)
        updated_at (datetime): Last update timestamp (inherited)
        configuration_id (UUID): Foreign key to configurations table, required
        config_key (str, optional): Configuration key at time of change
        old_value (Dict, optional): Previous configuration value in JSON format
        new_value (Dict, optional): New configuration value in JSON format
        changed_by (UUID, optional): Foreign key to users table
        configuration: Relationship to Configuration model
        user: Relationship to User model (who made the change)

    Example:
        >>> history = ConfigurationHistory(
        ...     configuration_id=config_uuid,
        ...     config_key="smtp_settings",
        ...     changed_by=user_uuid
        ... )
        >>> history.set_old_value("host", "old.example.com")
        >>> history.set_new_value("host", "new.example.com")
        >>> print(history.get_old_value("host"))
        'old.example.com'
        >>> print(history.get_new_value("host"))
        'new.example.com'

    Note:
        - configuration_id is required (not nullable)
        - old_value and new_value are nullable JSONB fields
        - Helper methods initialize JSONB fields as empty dict if None
        - config_key is denormalized for historical accuracy
    """

    __tablename__ = 'configuration_history'

    tenant_id = Column(
        GUID(),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Tenant (organization or user) that owns this history record"
    )

    # Foreign key to configurations
    configuration_id = Column(
        GUID(),
        ForeignKey('configurations.id'),
        nullable=False,
        comment="Configuration this history entry belongs to"
    )

    # Configuration key at the time of change (denormalized)
    config_key = Column(
        String(255),
        nullable=True,
        comment="Configuration key at time of change"
    )

    # JSONB field for old configuration value
    old_value = Column(
        JSONB_VARIANT,
        nullable=True,
        comment="Previous configuration value"
    )

    # JSONB field for new configuration value
    new_value = Column(
        JSONB_VARIANT,
        nullable=True,
        comment="New configuration value"
    )

    # Foreign key to users (who made the change)
    changed_by = Column(
        GUID(),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="User who made the change"
    )

    change_reason = Column(
        Text,
        nullable=True,
        comment="Reason provided for the configuration change"
    )

    # Relationships
    configuration = relationship(
        "Configuration",
        backref="history",
        foreign_keys=[configuration_id],
        primaryjoin="ConfigurationHistory.configuration_id == Configuration.id"
    )

    user = relationship(
        "User",
        foreign_keys=[changed_by],
        primaryjoin="ConfigurationHistory.changed_by == remote(User.id)",
        viewonly=True
    )

    def __repr__(self) -> str:
        """
        String representation of ConfigurationHistory instance.

        Returns:
            String with configuration_id and config_key

        Example:
            >>> history = ConfigurationHistory(
            ...     configuration_id=some_uuid,
            ...     config_key="smtp_settings"
            ... )
            >>> print(history)
            <ConfigurationHistory(config_key='smtp_settings')>
        """
        return f"<ConfigurationHistory(config_key='{self.config_key}')>"

    # Old value helper methods
    def set_old_value(self, key: str, value: Any) -> None:
        """
        Set a value in the old_value JSONB field.

        Args:
            key: Configuration value key
            value: Configuration value

        Example:
            >>> history = ConfigurationHistory(configuration_id=some_uuid)
            >>> history.set_old_value("host", "old.smtp.example.com")
            >>> history.old_value
            {'host': 'old.smtp.example.com'}
        """
        if self.old_value is None:
            self.old_value = {}
        self.old_value[key] = value

    def get_old_value(self, key: str) -> Optional[Any]:
        """
        Get a value from the old_value JSONB field.

        Args:
            key: Configuration value key

        Returns:
            Configuration value or None if not found

        Example:
            >>> history = ConfigurationHistory(configuration_id=some_uuid)
            >>> history.set_old_value("host", "old.smtp.example.com")
            >>> history.get_old_value("host")
            'old.smtp.example.com'
            >>> history.get_old_value("nonexistent")
            None
        """
        if self.old_value is None:
            return None
        return self.old_value.get(key)

    def get_all_old_value(self) -> Dict[str, Any]:
        """
        Get all old_value data.

        Returns:
            Dictionary of all old value data, empty dict if none set

        Example:
            >>> history = ConfigurationHistory(configuration_id=some_uuid)
            >>> history.set_old_value("host", "old.smtp.example.com")
            >>> history.set_old_value("port", 587)
            >>> history.get_all_old_value()
            {'host': 'old.smtp.example.com', 'port': 587}
        """
        if self.old_value is None:
            return {}
        return dict(self.old_value)

    # New value helper methods
    def set_new_value(self, key: str, value: Any) -> None:
        """
        Set a value in the new_value JSONB field.

        Args:
            key: Configuration value key
            value: Configuration value

        Example:
            >>> history = ConfigurationHistory(configuration_id=some_uuid)
            >>> history.set_new_value("host", "new.smtp.example.com")
            >>> history.new_value
            {'host': 'new.smtp.example.com'}
        """
        if self.new_value is None:
            self.new_value = {}
        self.new_value[key] = value

    def get_new_value(self, key: str) -> Optional[Any]:
        """
        Get a value from the new_value JSONB field.

        Args:
            key: Configuration value key

        Returns:
            Configuration value or None if not found

        Example:
            >>> history = ConfigurationHistory(configuration_id=some_uuid)
            >>> history.set_new_value("host", "new.smtp.example.com")
            >>> history.get_new_value("host")
            'new.smtp.example.com'
            >>> history.get_new_value("nonexistent")
            None
        """
        if self.new_value is None:
            return None
        return self.new_value.get(key)

    def get_all_new_value(self) -> Dict[str, Any]:
        """
        Get all new_value data.

        Returns:
            Dictionary of all new value data, empty dict if none set

        Example:
            >>> history = ConfigurationHistory(configuration_id=some_uuid)
            >>> history.set_new_value("host", "new.smtp.example.com")
            >>> history.set_new_value("port", 25)
            >>> history.get_all_new_value()
            {'host': 'new.smtp.example.com', 'port': 25}
        """
        if self.new_value is None:
            return {}
        return dict(self.new_value)
