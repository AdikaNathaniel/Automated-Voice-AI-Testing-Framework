import os

README_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")


def test_readme_describes_secret_management():
    content = open(README_PATH, encoding="utf-8").read()
    assert "Secret Management" in content, "README should document secret management section"
    assert "Kubernetes" in content, "README should mention Kubernetes secrets guidance"
    assert "rotation" in content.lower(), "README should describe credential rotation"
