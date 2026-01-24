from pathlib import Path


def test_backend_dockerfile_uses_non_root_user():
    dockerfile = Path(__file__).resolve().parents[1] / "Dockerfile"
    contents = dockerfile.read_text()
    assert "USER appuser" in contents, "Backend Dockerfile must drop privileges to a non-root user"
