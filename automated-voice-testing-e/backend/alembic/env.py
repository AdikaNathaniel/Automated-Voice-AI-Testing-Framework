from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add backend to Python path for imports
# Since alembic is inside backend/, go up one directory to get to backend root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import application config to get DATABASE_URL
from api.config import get_settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with DATABASE_URL from application settings
settings = get_settings()
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models here for autogenerate support
# Base model created in TASK-015
try:
    from models.base import Base

    # Import all models so they register with Base.metadata
    from models.user import User  # noqa: F401
    from models.test_suite import TestSuite  # noqa: F401
    from models.suite_run import SuiteRun  # noqa: F401
    from models.configuration import Configuration  # noqa: F401
    from models.configuration_history import ConfigurationHistory  # noqa: F401
    from models.test_metric import TestMetric  # noqa: F401
    from models.escalation_policy import EscalationPolicy  # noqa: F401
    from models.validator_performance import ValidatorPerformance  # noqa: F401
    from models.scenario_script import ScenarioScript, ScenarioStep  # noqa: F401
    from models.knowledge_base import KnowledgeBase  # noqa: F401
    from models.activity_log import ActivityLog  # noqa: F401
    from models.comment import Comment  # noqa: F401
    from models.defect import Defect  # noqa: F401
    from models.edge_case import EdgeCase  # noqa: F401
    from models.pattern_group import PatternGroup, EdgeCasePatternLink  # noqa: F401
    from models.expected_outcome import ExpectedOutcome  # noqa: F401
    from models.multi_turn_execution import MultiTurnExecution, StepExecution  # noqa: F401
    from models.test_execution_queue import TestExecutionQueue  # noqa: F401
    from models.device_test_execution import DeviceTestExecution  # noqa: F401
    from models.validation_result import ValidationResult  # noqa: F401
    from models.validation_queue import ValidationQueue  # noqa: F401
    from models.human_validation import HumanValidation  # noqa: F401

    target_metadata = Base.metadata
except ImportError as e:
    # If models can't be imported, set to None and log warning
    import logging
    logging.warning(f"Could not import models: {e}")
    target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Create alembic_version table with larger VARCHAR if it doesn't exist
        # This allows for descriptive revision IDs longer than 32 characters
        from sqlalchemy import text
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS alembic_version (
                version_num VARCHAR(100) NOT NULL,
                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
            )
        """))
        connection.commit()

        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
