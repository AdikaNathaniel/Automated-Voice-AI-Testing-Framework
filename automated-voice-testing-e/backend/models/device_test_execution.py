"""
DeviceTestExecution SQLAlchemy model for device test execution data

This module defines the DeviceTestExecution model which represents device test
execution data for the automated testing framework.

The DeviceTestExecution model includes:
    - Suite run reference: Link to the suite run
    - Device information: JSONB field for device details (model, OS, manufacturer, etc.)
    - Platform details: JSONB field for platform-specific information
    - Test results: JSONB field for test execution results and metrics

Example:
    >>> from models.device_test_execution import DeviceTestExecution
    >>>
    >>> # Create device test execution
    >>> execution = DeviceTestExecution(
    ...     suite_run_id=run.id
    ... )
    >>>
    >>> # Set device information
    >>> execution.set_device_info("model", "iPhone 14 Pro")
    >>> execution.set_device_info("os_version", "iOS 17.2")
    >>>
    >>> # Set platform details
    >>> execution.set_platform_detail("screen_size", "6.1 inches")
    >>> execution.set_platform_detail("resolution", "2532x1170")
    >>>
    >>> # Set test results
    >>> execution.set_test_result("status", "passed")
    >>> execution.set_test_result("duration_ms", 1250)
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, JSON
from sqlalchemy.dialects import postgresql

from sqlalchemy.orm import relationship

from models.base import Base, BaseModel, GUID

# Avoid circular imports for type hints
if TYPE_CHECKING:
    pass


class DeviceTestExecution(Base, BaseModel):
    """
    DeviceTestExecution model for storing device test execution data.

    Represents a device test execution with flexible JSONB fields for device
    information, platform details, and test results.

    Attributes:
        id (UUID): Unique identifier (inherited from BaseModel)
        suite_run_id (UUID): Foreign key to suite run, required
        device_info (Dict, optional): Device information (model, OS version, manufacturer, etc.)
        platform_details (Dict, optional): Platform-specific details (capabilities, features, etc.)
        test_results (Dict, optional): Test execution results and metrics
        created_at (datetime): Creation timestamp (inherited)
        updated_at (datetime): Last update timestamp (inherited)
        suite_run (SuiteRun): Relationship to the suite run

    Example:
        >>> execution = DeviceTestExecution(suite_run_id=run_id)
        >>> execution.set_device_info("model", "iPhone 14 Pro")
        >>> execution.set_platform_detail("screen_size", "6.1 inches")
        >>> execution.set_test_result("status", "passed")
        >>> print(execution.get_device_info("model"))
        'iPhone 14 Pro'
        >>> print(execution.get_all_device_info())
        {'model': 'iPhone 14 Pro'}

    Note:
        - All JSONB fields are nullable and can store flexible key-value data
        - Helper methods initialize JSONB fields as empty dicts if None
        - suite_run_id is required (not nullable)
    """

    __tablename__ = 'device_test_executions'

    # Foreign key to suite_runs
    suite_run_id = Column(
        GUID(),
        ForeignKey('suite_runs.id'),
        nullable=False,
        index=True,
        comment="Suite run this execution belongs to"
    )

    # JSONB fields for flexible device test data
    device_info = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Device information (model, OS version, manufacturer, etc.)"
    )

    platform_details = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Platform-specific details (capabilities, features, etc.)"
    )

    test_results = Column(
        postgresql.JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        comment="Test execution results and metrics"
    )

    # Relationships
    suite_run = relationship(
        'SuiteRun',
        foreign_keys=[suite_run_id],
        primaryjoin="DeviceTestExecution.suite_run_id == SuiteRun.id",
        lazy='joined'
    )

    def __repr__(self) -> str:
        """
        String representation of DeviceTestExecution instance.

        Returns:
            String with suite_run_id

        Example:
            >>> execution = DeviceTestExecution(suite_run_id=some_uuid)
            >>> print(execution)
            <DeviceTestExecution(suite_run_id='...')>
        """
        return f"<DeviceTestExecution(suite_run_id='{self.suite_run_id}')>"

    # Device info helper methods
    def set_device_info(self, key: str, value: Any) -> None:
        """
        Set a device information field.

        Args:
            key: Device info key
            value: Device info value

        Example:
            >>> execution = DeviceTestExecution(suite_run_id=run_id)
            >>> execution.set_device_info("model", "iPhone 14 Pro")
            >>> execution.device_info
            {'model': 'iPhone 14 Pro'}
        """
        if self.device_info is None:
            self.device_info = {}
        self.device_info[key] = value

    def get_device_info(self, key: str) -> Optional[Any]:
        """
        Get a device information value.

        Args:
            key: Device info key

        Returns:
            Device info value or None if not found

        Example:
            >>> execution = DeviceTestExecution(suite_run_id=run_id)
            >>> execution.set_device_info("model", "iPhone 14 Pro")
            >>> execution.get_device_info("model")
            'iPhone 14 Pro'
            >>> execution.get_device_info("nonexistent")
            None
        """
        if self.device_info is None:
            return None
        return self.device_info.get(key)

    def get_all_device_info(self) -> Dict[str, Any]:
        """
        Get all device information.

        Returns:
            Dictionary of all device info, empty dict if none set

        Example:
            >>> execution = DeviceTestExecution(suite_run_id=run_id)
            >>> execution.set_device_info("model", "iPhone 14 Pro")
            >>> execution.set_device_info("os_version", "iOS 17.2")
            >>> execution.get_all_device_info()
            {'model': 'iPhone 14 Pro', 'os_version': 'iOS 17.2'}
        """
        if self.device_info is None:
            return {}
        return dict(self.device_info)

    # Platform details helper methods
    def set_platform_detail(self, key: str, value: Any) -> None:
        """
        Set a platform detail.

        Args:
            key: Platform detail key
            value: Platform detail value

        Example:
            >>> execution = DeviceTestExecution(suite_run_id=run_id)
            >>> execution.set_platform_detail("screen_size", "6.1 inches")
            >>> execution.platform_details
            {'screen_size': '6.1 inches'}
        """
        if self.platform_details is None:
            self.platform_details = {}
        self.platform_details[key] = value

    def get_platform_detail(self, key: str) -> Optional[Any]:
        """
        Get a platform detail value.

        Args:
            key: Platform detail key

        Returns:
            Platform detail value or None if not found

        Example:
            >>> execution = DeviceTestExecution(suite_run_id=run_id)
            >>> execution.set_platform_detail("screen_size", "6.1 inches")
            >>> execution.get_platform_detail("screen_size")
            '6.1 inches'
            >>> execution.get_platform_detail("nonexistent")
            None
        """
        if self.platform_details is None:
            return None
        return self.platform_details.get(key)

    def get_all_platform_details(self) -> Dict[str, Any]:
        """
        Get all platform details.

        Returns:
            Dictionary of all platform details, empty dict if none set

        Example:
            >>> execution = DeviceTestExecution(suite_run_id=run_id)
            >>> execution.set_platform_detail("screen_size", "6.1 inches")
            >>> execution.set_platform_detail("resolution", "2532x1170")
            >>> execution.get_all_platform_details()
            {'screen_size': '6.1 inches', 'resolution': '2532x1170'}
        """
        if self.platform_details is None:
            return {}
        return dict(self.platform_details)

    # Test results helper methods
    def set_test_result(self, key: str, value: Any) -> None:
        """
        Set a test result field.

        Args:
            key: Test result key
            value: Test result value

        Example:
            >>> execution = DeviceTestExecution(suite_run_id=run_id)
            >>> execution.set_test_result("status", "passed")
            >>> execution.test_results
            {'status': 'passed'}
        """
        if self.test_results is None:
            self.test_results = {}
        self.test_results[key] = value

    def get_test_result(self, key: str) -> Optional[Any]:
        """
        Get a test result value.

        Args:
            key: Test result key

        Returns:
            Test result value or None if not found

        Example:
            >>> execution = DeviceTestExecution(suite_run_id=run_id)
            >>> execution.set_test_result("status", "passed")
            >>> execution.get_test_result("status")
            'passed'
            >>> execution.get_test_result("nonexistent")
            None
        """
        if self.test_results is None:
            return None
        return self.test_results.get(key)

    def get_all_test_results(self) -> Dict[str, Any]:
        """
        Get all test results.

        Returns:
            Dictionary of all test results, empty dict if none set

        Example:
            >>> execution = DeviceTestExecution(suite_run_id=run_id)
            >>> execution.set_test_result("status", "passed")
            >>> execution.set_test_result("duration_ms", 1250)
            >>> execution.get_all_test_results()
            {'status': 'passed', 'duration_ms': 1250}
        """
        if self.test_results is None:
            return {}
        return dict(self.test_results)
