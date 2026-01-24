"""
Test suite service for CRUD operations and scenario management

This module provides business logic for test suite management including:
- Test suite creation
- Test suite retrieval by ID
- Test suite listing with filters and pagination
- Test suite updates
- Test suite deletion
- Adding/removing scenarios to/from suites
- Running all scenarios in a suite

All operations are async and use SQLAlchemy with AsyncSession for database access.

Functions:
    create_test_suite(db: AsyncSession, data: TestSuiteCreate, user_id: UUID) -> TestSuite:
        Create a new test suite

    get_test_suite(db: AsyncSession, test_suite_id: UUID) -> TestSuite | None:
        Retrieve test suite by UUID

    get_test_suite_with_scenarios(db: AsyncSession, test_suite_id: UUID) -> TestSuite | None:
        Retrieve test suite with scenarios eager loaded

    list_test_suites(db: AsyncSession, filters: dict, pagination: dict) -> tuple[list[TestSuite], int]:
        List test suites with filters and pagination

    update_test_suite(db: AsyncSession, test_suite_id: UUID, data: TestSuiteUpdate) -> TestSuite:
        Update test suite fields

    delete_test_suite(db: AsyncSession, test_suite_id: UUID) -> bool:
        Delete test suite from database

    add_scenarios_to_suite(db: AsyncSession, suite_id: UUID, scenario_ids: list) -> TestSuite:
        Add scenarios to a test suite

    remove_scenarios_from_suite(db: AsyncSession, suite_id: UUID, scenario_ids: list) -> TestSuite:
        Remove scenarios from a test suite

    reorder_suite_scenarios(db: AsyncSession, suite_id: UUID, scenario_order: list) -> TestSuite:
        Reorder scenarios in a suite

Example:
    >>> from services.test_suite_service import create_test_suite, list_test_suites
    >>> from api.schemas.test_suite import TestSuiteCreate
    >>> from api.database import SessionLocal
    >>>
    >>> async with SessionLocal() as db:
    ...     # Create test suite
    ...     suite_data = TestSuiteCreate(
    ...         name="API Tests",
    ...         description="Test suite for API endpoints",
    ...         category="API"
    ...     )
    ...     suite = await create_test_suite(db, suite_data, user_id)
    ...
    ...     # List test suites
    ...     suites, total = await list_test_suites(db, {}, {"skip": 0, "limit": 10})
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
import uuid

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from models.test_suite import TestSuite
from models.test_suite_scenario import TestSuiteScenario
from models.scenario_script import ScenarioScript
from api.schemas.test_suite import TestSuiteCreate, TestSuiteUpdate

logger = logging.getLogger(__name__)


def resolve_suite_languages(
    suite_language_config: Optional[Dict[str, Any]],
    scenario_languages: List[str],
    scenario_primary_language: str = "en-US"
) -> Dict[str, Any]:
    """
    Resolve which languages to execute for a scenario based on suite configuration.

    Args:
        suite_language_config: Suite's language configuration dict with mode, languages, fallback_behavior
        scenario_languages: List of languages available in the scenario
        scenario_primary_language: Scenario's primary language (default: en-US)

    Returns:
        Dict with:
            - languages: List of language codes to execute
            - warnings: List of warning messages for missing languages
            - fallback_used: Boolean indicating if fallback was applied

    Example:
        >>> config = {"mode": "specific", "languages": ["en-US", "es-ES"], "fallback_behavior": "smart"}
        >>> result = resolve_suite_languages(config, ["en-US", "fr-FR"], "en-US")
        >>> result
        {'languages': ['en-US'], 'warnings': ['Language es-ES not available, using primary language en-US'], 'fallback_used': True}
    """
    # Default: run primary language only
    if not suite_language_config:
        return {
            "languages": [scenario_primary_language],
            "warnings": [],
            "fallback_used": False
        }

    mode = suite_language_config.get("mode", "primary")
    requested_languages = suite_language_config.get("languages", [])
    fallback_behavior = suite_language_config.get("fallback_behavior", "smart")

    # Mode 1: Primary language only
    if mode == "primary":
        return {
            "languages": [scenario_primary_language],
            "warnings": [],
            "fallback_used": False
        }

    # Mode 2: All available languages
    if mode == "all":
        return {
            "languages": scenario_languages if scenario_languages else [scenario_primary_language],
            "warnings": [],
            "fallback_used": False
        }

    # Mode 3: Specific languages
    if mode == "specific":
        if not requested_languages:
            # No languages specified, default to primary
            return {
                "languages": [scenario_primary_language],
                "warnings": ["No languages specified in config, using primary language"],
                "fallback_used": True
            }

        languages_to_execute = []
        warnings = []
        fallback_used = False

        for lang in requested_languages:
            if lang in scenario_languages:
                languages_to_execute.append(lang)
            else:
                # Language not available - apply fallback behavior
                if fallback_behavior == "smart":
                    # Smart: fallback to primary language
                    if scenario_primary_language not in languages_to_execute:
                        languages_to_execute.append(scenario_primary_language)
                    warnings.append(f"Language {lang} not available, using primary language {scenario_primary_language}")
                    fallback_used = True
                elif fallback_behavior == "skip":
                    # Skip: don't execute this scenario
                    return {
                        "languages": [],
                        "warnings": [f"Language {lang} not available, skipping scenario"],
                        "fallback_used": False,
                        "should_skip": True
                    }
                elif fallback_behavior == "fail":
                    # Fail: mark as failed
                    return {
                        "languages": [],
                        "warnings": [f"Language {lang} not available, marking as failed"],
                        "fallback_used": False,
                        "should_fail": True
                    }

        # If no languages could be resolved, fallback to primary
        if not languages_to_execute:
            languages_to_execute = [scenario_primary_language]
            warnings.append("No requested languages available, falling back to primary language")
            fallback_used = True

        return {
            "languages": languages_to_execute,
            "warnings": warnings,
            "fallback_used": fallback_used
        }

    # Unknown mode, default to primary
    return {
        "languages": [scenario_primary_language],
        "warnings": [f"Unknown language mode '{mode}', using primary language"],
        "fallback_used": True
    }


class TestSuiteService:
    """
    Service class for test suite management operations.

    Provides CRUD operations for test suites.

    Example:
        >>> service = TestSuiteService()
        >>> suite = await service.create_test_suite(db, data, user_id)
    """

    def __init__(self):
        """Initialize the test suite service."""
        pass

    async def create_test_suite(self, db: AsyncSession, data: TestSuiteCreate, user_id: UUID) -> TestSuite:
        """Create a new test suite."""
        return await create_test_suite(db, data, user_id)

    async def get_test_suite(self, db: AsyncSession, test_suite_id: UUID) -> Optional[TestSuite]:
        """Retrieve test suite by UUID."""
        return await get_test_suite(db, test_suite_id)

    async def list_test_suites(self, db: AsyncSession, filters: Dict[str, Any], pagination: Dict[str, Any]) -> Tuple[List[TestSuite], int]:
        """List test suites with filters and pagination."""
        return await list_test_suites(db, filters, pagination)

    async def update_test_suite(self, db: AsyncSession, test_suite_id: UUID, data: TestSuiteUpdate) -> TestSuite:
        """Update test suite fields."""
        return await update_test_suite(db, test_suite_id, data)

    async def delete_test_suite(self, db: AsyncSession, test_suite_id: UUID) -> bool:
        """Delete test suite from database."""
        return await delete_test_suite(db, test_suite_id)


async def create_test_suite(
    db: AsyncSession,
    data: TestSuiteCreate,
    user_id: UUID,
    tenant_id: Optional[UUID] = None,
) -> TestSuite:
    """
    Create a new test suite.

    Takes test suite creation data, creates a TestSuite object, and persists
    it to the database.

    Args:
        db: Async database session
        data: Test suite creation schema with all fields
        user_id: UUID of the user creating the test suite

    Returns:
        TestSuite: The newly created test suite with all fields populated

    Raises:
        IntegrityError: If test suite with same name already exists
        Exception: If creation fails for other reasons

    Example:
        >>> suite_data = TestSuiteCreate(
        ...     name="Authentication Tests",
        ...     description="Tests for auth flows",
        ...     category="Security"
        ... )
        >>> suite = await create_test_suite(db, suite_data, user_id)
        >>> print(suite.name)
        Authentication Tests

    Note:
        - UUID is automatically generated for the new test suite
        - created_at and updated_at timestamps are set automatically
        - created_by is set to the provided user_id
        - is_active defaults to True if not specified
    """
    try:
        # Create test suite
        test_suite = TestSuite(
            id=uuid.uuid4(),
            name=data.name,
            description=data.description,
            category=data.category,
            is_active=data.is_active if data.is_active is not None else True,
            language_config=data.language_config.model_dump() if data.language_config else None,
            created_by=user_id,
            tenant_id=tenant_id,
        )

        db.add(test_suite)
        await db.commit()
        await db.refresh(test_suite)

        logger.debug(f"Created test suite: {test_suite.id}")

        # Add scenarios if provided
        if data.scenario_ids:
            from models.test_suite_scenario import TestSuiteScenario

            for order, scenario_id in enumerate(data.scenario_ids):
                association = TestSuiteScenario(
                    id=uuid.uuid4(),
                    suite_id=test_suite.id,
                    scenario_id=scenario_id,
                    order=order
                )
                db.add(association)

            await db.commit()
            logger.debug(f"Added {len(data.scenario_ids)} scenarios to test suite: {test_suite.id}")

        return test_suite

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"IntegrityError creating test suite {data.name}: {e}")
        raise IntegrityError(f"Test suite creation failed: {str(e)}", params=None, orig=e.orig)
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating test suite {data.name}: {e}")
        raise Exception(f"Failed to create test suite: {str(e)}")


async def get_test_suite(
    db: AsyncSession,
    test_suite_id: UUID,
    tenant_id: Optional[UUID] = None,
) -> Optional[TestSuite]:
    """
    Retrieve a test suite by ID.

    Fetches a single test suite from the database by its UUID.

    Args:
        db: Async database session
        test_suite_id: UUID of the test suite to retrieve

    Returns:
        TestSuite | None: The test suite if found, None otherwise

    Example:
        >>> suite_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        >>> suite = await get_test_suite(db, suite_id)
        >>> if suite:
        ...     print(f"Found suite: {suite.name}")
        ... else:
        ...     print("Suite not found")

    Note:
        - Returns None if test suite doesn't exist
        - No exception raised for missing test suites
    """
    try:
        stmt = select(TestSuite).where(TestSuite.id == test_suite_id)
        if tenant_id:
            stmt = stmt.where(TestSuite.tenant_id == tenant_id)
        result = await db.execute(stmt)
        test_suite = result.scalar_one_or_none()
        if test_suite:
            logger.debug(f"Found test suite: {test_suite_id}")
        return test_suite

    except Exception as e:
        logger.error(f"Error getting test suite {test_suite_id}: {e}")
        raise Exception(f"Failed to get test suite: {str(e)}")


async def list_test_suites(
    db: AsyncSession,
    filters: Dict[str, Any],
    pagination: Dict[str, int],
    tenant_id: Optional[UUID] = None,
) -> Tuple[List[TestSuite], int]:
    """
    List test suites with optional filters and pagination.

    Retrieves test suites matching the specified filters with pagination support.
    Returns both the matching test suites and total count.

    Args:
        db: Async database session
        filters: Dictionary of filter criteria:
            - category: Filter by category (exact match)
            - is_active: Filter by active status (boolean)
        pagination: Dictionary with pagination parameters:
            - skip: Number of records to skip (offset)
            - limit: Maximum number of records to return

    Returns:
        tuple[list[TestSuite], int]: Tuple containing:
            - List of test suites matching filters
            - Total count of matching test suites (before pagination)

    Example:
        >>> filters = {"category": "API", "is_active": True}
        >>> pagination = {"skip": 0, "limit": 10}
        >>> suites, total = await list_test_suites(db, filters, pagination)
        >>> print(f"Found {total} suites, showing {len(suites)}")
        Found 25 suites, showing 10

    Note:
        - Empty filters dictionary returns all test suites
        - Filters are combined with AND logic
        - Total count is computed before pagination is applied
    """
    try:
        # Build base query
        query = select(TestSuite)
        if tenant_id:
            query = query.where(TestSuite.tenant_id == tenant_id)

        # Apply filters
        if "category" in filters and filters["category"]:
            query = query.where(TestSuite.category == filters["category"])

        if "is_active" in filters and filters["is_active"] is not None:
            query = query.where(TestSuite.is_active == filters["is_active"])

        # Count total matching records
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        skip = pagination.get("skip", 0)
        limit = pagination.get("limit", 100)
        query = query.offset(skip).limit(limit)

        # Order by created_at descending
        query = query.order_by(TestSuite.created_at.desc())

        # Execute query
        result = await db.execute(query)
        test_suites = result.scalars().all()

        logger.debug(f"Listed {len(test_suites)} test suites (total: {total})")
        return list(test_suites), total

    except Exception as e:
        logger.error(f"Error listing test suites: {e}")
        raise Exception(f"Failed to list test suites: {str(e)}")


async def update_test_suite(
    db: AsyncSession,
    test_suite_id: UUID,
    data: TestSuiteUpdate,
    tenant_id: Optional[UUID] = None,
) -> TestSuite:
    """
    Update a test suite.

    Updates the specified test suite with provided data. Only fields present
    in the update data are modified.

    Args:
        db: Async database session
        test_suite_id: UUID of the test suite to update
        data: Test suite update schema with fields to update

    Returns:
        TestSuite: The updated test suite

    Raises:
        Exception: If test suite not found or update fails

    Example:
        >>> update_data = TestSuiteUpdate(
        ...     name="Updated Suite Name",
        ...     is_active=False
        ... )
        >>> suite = await update_test_suite(db, suite_id, update_data)
        >>> print(suite.name)
        Updated Suite Name

    Note:
        - Only fields with non-None values in data are updated
        - updated_at timestamp is automatically updated
        - Use exclude_unset=True to only update provided fields
    """
    try:
        # Get existing test suite
        stmt = select(TestSuite).where(TestSuite.id == test_suite_id)
        if tenant_id:
            stmt = stmt.where(TestSuite.tenant_id == tenant_id)
        result = await db.execute(stmt)
        test_suite = result.scalar_one_or_none()

        if not test_suite:
            raise Exception(f"Test suite {test_suite_id} not found")

        # Update fields - only update fields that were explicitly set
        update_data = data.model_dump(exclude_unset=True)

        # Handle language_config if present (convert Pydantic model to dict)
        if 'language_config' in update_data and update_data['language_config'] is not None:
            if hasattr(update_data['language_config'], 'model_dump'):
                update_data['language_config'] = update_data['language_config'].model_dump()

        for field, value in update_data.items():
            setattr(test_suite, field, value)

        await db.commit()
        await db.refresh(test_suite)

        logger.debug(f"Updated test suite: {test_suite_id}")
        return test_suite

    except Exception as e:
        await db.rollback()
        if "not found" in str(e).lower():
            raise
        logger.error(f"Error updating test suite {test_suite_id}: {e}")
        raise Exception(f"Failed to update test suite: {str(e)}")


async def delete_test_suite(
    db: AsyncSession,
    test_suite_id: UUID,
    tenant_id: Optional[UUID] = None,
) -> bool:
    """
    Delete a test suite.

    Permanently deletes the specified test suite from the database.

    Args:
        db: Async database session
        test_suite_id: UUID of the test suite to delete

    Returns:
        bool: True if deletion successful, False if test suite not found

    Example:
        >>> deleted = await delete_test_suite(db, suite_id)
        >>> if deleted:
        ...     print("Test suite deleted successfully")
        ... else:
        ...     print("Test suite not found")

    Note:
        - Returns False if test suite doesn't exist (no exception raised)
        - Associated test cases may be deleted via cascade depending on
          foreign key constraints
        - This is a permanent deletion - consider soft delete (is_active=False)
          for preserving historical data
    """
    try:
        # Get existing test suite
        stmt = select(TestSuite).where(TestSuite.id == test_suite_id)
        if tenant_id:
            stmt = stmt.where(TestSuite.tenant_id == tenant_id)
        result = await db.execute(stmt)
        test_suite = result.scalar_one_or_none()

        if not test_suite:
            return False

        # Delete test suite
        await db.delete(test_suite)
        await db.commit()

        logger.debug(f"Deleted test suite: {test_suite_id}")
        return True

    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting test suite {test_suite_id}: {e}")
        raise Exception(f"Failed to delete test suite: {str(e)}")


# =============================================================================
# Scenario Management Functions
# =============================================================================


async def get_test_suite_with_scenarios(
    db: AsyncSession,
    test_suite_id: UUID,
    tenant_id: Optional[UUID] = None,
) -> Optional[TestSuite]:
    """
    Retrieve a test suite with scenarios eager loaded.

    Args:
        db: Async database session
        test_suite_id: UUID of the test suite to retrieve
        tenant_id: Optional tenant ID for filtering

    Returns:
        TestSuite | None: The test suite with scenarios if found, None otherwise
    """
    try:
        stmt = (
            select(TestSuite)
            .where(TestSuite.id == test_suite_id)
            .options(
                selectinload(TestSuite.suite_scenarios)
                .selectinload(TestSuiteScenario.scenario)
                .selectinload(ScenarioScript.steps)
            )
        )
        if tenant_id:
            stmt = stmt.where(TestSuite.tenant_id == tenant_id)

        result = await db.execute(stmt)
        test_suite = result.scalar_one_or_none()

        if test_suite:
            logger.debug(f"Found test suite with scenarios: {test_suite_id}")
        return test_suite

    except Exception as e:
        logger.error(f"Error getting test suite with scenarios {test_suite_id}: {e}")
        raise Exception(f"Failed to get test suite with scenarios: {str(e)}")


async def add_scenarios_to_suite(
    db: AsyncSession,
    suite_id: UUID,
    scenario_ids: List[UUID],
    tenant_id: Optional[UUID] = None,
) -> TestSuite:
    """
    Add scenarios to a test suite.

    Args:
        db: Async database session
        suite_id: UUID of the test suite
        scenario_ids: List of scenario script UUIDs to add
        tenant_id: Optional tenant ID for filtering

    Returns:
        TestSuite: The updated test suite

    Raises:
        Exception: If suite not found or operation fails
    """
    try:
        # Get existing test suite
        stmt = select(TestSuite).where(TestSuite.id == suite_id)
        if tenant_id:
            stmt = stmt.where(TestSuite.tenant_id == tenant_id)
        result = await db.execute(stmt)
        test_suite = result.scalar_one_or_none()

        if not test_suite:
            raise Exception(f"Test suite {suite_id} not found")

        # Get existing associations to determine max order
        existing_stmt = (
            select(TestSuiteScenario)
            .where(TestSuiteScenario.suite_id == suite_id)
            .order_by(TestSuiteScenario.order.desc())
        )
        existing_result = await db.execute(existing_stmt)
        existing_associations = existing_result.scalars().all()

        # Get existing scenario IDs
        existing_scenario_ids = {assoc.scenario_id for assoc in existing_associations}
        max_order = max((assoc.order for assoc in existing_associations), default=0)

        # Verify all scenarios exist
        scenarios_stmt = select(ScenarioScript).where(ScenarioScript.id.in_(scenario_ids))
        scenarios_result = await db.execute(scenarios_stmt)
        scenarios = {s.id: s for s in scenarios_result.scalars().all()}

        # Add new associations
        for i, scenario_id in enumerate(scenario_ids):
            if scenario_id in existing_scenario_ids:
                logger.debug(f"Scenario {scenario_id} already in suite, skipping")
                continue

            if scenario_id not in scenarios:
                logger.warning(f"Scenario {scenario_id} not found, skipping")
                continue

            association = TestSuiteScenario(
                id=uuid.uuid4(),
                suite_id=suite_id,
                scenario_id=scenario_id,
                order=max_order + i + 1
            )
            db.add(association)

        await db.commit()

        # Return updated suite with scenarios
        return await get_test_suite_with_scenarios(db, suite_id, tenant_id)

    except Exception as e:
        await db.rollback()
        if "not found" in str(e).lower():
            raise
        logger.error(f"Error adding scenarios to suite {suite_id}: {e}")
        raise Exception(f"Failed to add scenarios to suite: {str(e)}")


async def remove_scenarios_from_suite(
    db: AsyncSession,
    suite_id: UUID,
    scenario_ids: List[UUID],
    tenant_id: Optional[UUID] = None,
) -> TestSuite:
    """
    Remove scenarios from a test suite.

    Args:
        db: Async database session
        suite_id: UUID of the test suite
        scenario_ids: List of scenario script UUIDs to remove
        tenant_id: Optional tenant ID for filtering

    Returns:
        TestSuite: The updated test suite

    Raises:
        Exception: If suite not found or operation fails
    """
    try:
        # Verify suite exists
        stmt = select(TestSuite).where(TestSuite.id == suite_id)
        if tenant_id:
            stmt = stmt.where(TestSuite.tenant_id == tenant_id)
        result = await db.execute(stmt)
        test_suite = result.scalar_one_or_none()

        if not test_suite:
            raise Exception(f"Test suite {suite_id} not found")

        # Delete associations
        delete_stmt = (
            delete(TestSuiteScenario)
            .where(TestSuiteScenario.suite_id == suite_id)
            .where(TestSuiteScenario.scenario_id.in_(scenario_ids))
        )
        await db.execute(delete_stmt)
        await db.commit()

        logger.debug(f"Removed {len(scenario_ids)} scenarios from suite {suite_id}")

        # Return updated suite with scenarios
        return await get_test_suite_with_scenarios(db, suite_id, tenant_id)

    except Exception as e:
        await db.rollback()
        if "not found" in str(e).lower():
            raise
        logger.error(f"Error removing scenarios from suite {suite_id}: {e}")
        raise Exception(f"Failed to remove scenarios from suite: {str(e)}")


async def reorder_suite_scenarios(
    db: AsyncSession,
    suite_id: UUID,
    scenario_order: List[UUID],
    tenant_id: Optional[UUID] = None,
) -> TestSuite:
    """
    Reorder scenarios in a test suite.

    Args:
        db: Async database session
        suite_id: UUID of the test suite
        scenario_order: List of scenario UUIDs in the desired order
        tenant_id: Optional tenant ID for filtering

    Returns:
        TestSuite: The updated test suite

    Raises:
        Exception: If suite not found or operation fails
    """
    try:
        # Verify suite exists
        stmt = select(TestSuite).where(TestSuite.id == suite_id)
        if tenant_id:
            stmt = stmt.where(TestSuite.tenant_id == tenant_id)
        result = await db.execute(stmt)
        test_suite = result.scalar_one_or_none()

        if not test_suite:
            raise Exception(f"Test suite {suite_id} not found")

        # Get existing associations
        assoc_stmt = (
            select(TestSuiteScenario)
            .where(TestSuiteScenario.suite_id == suite_id)
        )
        assoc_result = await db.execute(assoc_stmt)
        associations = {a.scenario_id: a for a in assoc_result.scalars().all()}

        # Update order for each scenario
        for i, scenario_id in enumerate(scenario_order):
            if scenario_id in associations:
                associations[scenario_id].order = i + 1

        await db.commit()

        logger.debug(f"Reordered {len(scenario_order)} scenarios in suite {suite_id}")

        # Return updated suite with scenarios
        return await get_test_suite_with_scenarios(db, suite_id, tenant_id)

    except Exception as e:
        await db.rollback()
        if "not found" in str(e).lower():
            raise
        logger.error(f"Error reordering scenarios in suite {suite_id}: {e}")
        raise Exception(f"Failed to reorder scenarios in suite: {str(e)}")


async def get_suite_scenarios(
    db: AsyncSession,
    suite_id: UUID,
    tenant_id: Optional[UUID] = None,
) -> List[Dict[str, Any]]:
    """
    Get scenarios in a test suite with their order.

    Args:
        db: Async database session
        suite_id: UUID of the test suite
        tenant_id: Optional tenant ID for filtering

    Returns:
        List of scenario info dictionaries with order
    """
    try:
        suite = await get_test_suite_with_scenarios(db, suite_id, tenant_id)
        if not suite:
            return []

        scenarios = []
        for assoc in sorted(suite.suite_scenarios, key=lambda a: a.order):
            scenario = assoc.scenario
            if scenario:
                # Extract languages from step metadata
                languages = set()
                if scenario.steps:
                    for step in scenario.steps:
                        if step.step_metadata:
                            variants = step.step_metadata.get('language_variants', [])
                            for variant in variants:
                                if isinstance(variant, dict) and 'language_code' in variant:
                                    languages.add(variant['language_code'])
                            primary = step.step_metadata.get('primary_language')
                            if primary:
                                languages.add(primary)

                scenarios.append({
                    'scenario_id': scenario.id,
                    'name': scenario.name,
                    'description': scenario.description,
                    'version': scenario.version,
                    'is_active': scenario.is_active,
                    'order': assoc.order,
                    'languages': sorted(list(languages)) if languages else None
                })

        return scenarios

    except Exception as e:
        logger.error(f"Error getting suite scenarios {suite_id}: {e}")
        raise Exception(f"Failed to get suite scenarios: {str(e)}")
