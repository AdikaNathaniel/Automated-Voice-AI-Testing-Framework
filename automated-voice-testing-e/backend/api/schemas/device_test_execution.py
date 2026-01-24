"""
Pydantic schemas for device test execution

This module defines Pydantic schemas for device test execution API operations
in the automated testing framework.

The module includes:
    - DeviceTestExecutionSchema: Full execution with all fields
    - DeviceTestExecutionCreate: Schema for creating executions
    - DeviceTestExecutionUpdate: Schema for updating executions

Example:
    >>> from api.schemas.device_test_execution import DeviceTestExecutionSchema
    >>>
    >>> execution = DeviceTestExecutionSchema(
    ...     id=uuid4(),
    ...     suite_run_id=uuid4(),
    ...     device_info={'model': 'iPhone 14 Pro', 'os_version': 'iOS 17.2'}
    ... )
"""

from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DeviceTestExecutionBase(BaseModel):
    """
    Base schema for device test execution fields.

    Contains common fields shared across create/update/response schemas.
    """

    suite_run_id: UUID = Field(
        ...,
        description="Suite run this execution belongs to"
    )
    device_info: Optional[Dict[str, Any]] = Field(
        None,
        description="Device information (model, OS version, manufacturer, etc.)"
    )
    platform_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Platform-specific details (capabilities, features, etc.)"
    )
    test_results: Optional[Dict[str, Any]] = Field(
        None,
        description="Test execution results and metrics"
    )


class DeviceTestExecutionCreate(DeviceTestExecutionBase):
    """
    Schema for creating a new device test execution.

    Example:
        >>> create_data = DeviceTestExecutionCreate(
        ...     suite_run_id=uuid4(),
        ...     device_info={'model': 'iPhone 14 Pro', 'os_version': 'iOS 17.2'}
        ... )
    """

    pass


class DeviceTestExecutionUpdate(BaseModel):
    """
    Schema for updating a device test execution.

    All fields are optional to allow partial updates.
    """

    device_info: Optional[Dict[str, Any]] = None
    platform_details: Optional[Dict[str, Any]] = None
    test_results: Optional[Dict[str, Any]] = None


class DeviceTestExecutionSchema(DeviceTestExecutionBase):
    """
    Full device test execution schema with all fields.

    Used for API responses containing complete execution data.

    Example:
        >>> execution = DeviceTestExecutionSchema(
        ...     id=uuid4(),
        ...     suite_run_id=uuid4(),
        ...     device_info={'model': 'iPhone 14 Pro', 'os_version': 'iOS 17.2'},
        ...     platform_details={'screen_size': '6.1 inches'},
        ...     created_at=datetime.now()
        ... )
    """

    id: UUID = Field(..., description="Unique identifier")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
