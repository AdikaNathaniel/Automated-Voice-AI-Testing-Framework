"""
Ensures tenant_id fields exist on core models (TODO §5.2).
"""

from importlib import import_module

import pytest
from sqlalchemy import inspect

MODEL_PATHS = [
    ("models.user", "User"),
    ("models.test_case", "TestCase"),
    ("models.test_suite", "TestSuite"),
    ("models.test_run", "TestRun"),
    ("models.validation_result", "ValidationResult"),
    ("models.defect", "Defect"),
]


@pytest.mark.parametrize("module_path, class_name", MODEL_PATHS)
def test_models_expose_tenant_id_column(module_path, class_name):
    module = import_module(module_path)
    model_cls = getattr(module, class_name)
    mapper = inspect(model_cls)
    assert "tenant_id" in mapper.columns, f"{class_name} missing tenant_id column"
