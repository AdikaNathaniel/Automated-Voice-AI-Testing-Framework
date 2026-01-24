"""
Tests ensuring ML dependencies are declared in backend/requirements.txt.
"""

from pathlib import Path


def test_backend_requirements_include_ml_dependencies():
    project_root = Path(__file__).resolve().parents[2]
    requirements_path = project_root / "backend" / "requirements.txt"
    contents = requirements_path.read_text(encoding="utf-8")

    expected_dependencies = {
        "transformers==4.37.0",
        "sentence-transformers==2.3.1",
        "torch==2.1.2",
        "spacy==3.7.2",
        "scikit-learn==1.4.0",
    }

    # Ensure each dependency string appears on its own line.
    missing = [
        dependency
        for dependency in expected_dependencies
        if dependency not in contents
    ]

    assert not missing, f"Missing ML dependencies in requirements.txt: {missing}"
