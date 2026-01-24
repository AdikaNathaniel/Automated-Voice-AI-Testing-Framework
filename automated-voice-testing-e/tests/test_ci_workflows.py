"""
Test suite for CI workflow validation.

Validates that GitHub Actions workflows are properly configured with:
- Required jobs and steps
- Service containers (PostgreSQL, Redis)
- Environment variables
- Artifact uploads
"""

import os
import pytest
import yaml
from pathlib import Path


class TestCIWorkflowFiles:
    """Test that CI workflow files exist and are valid YAML"""

    @pytest.fixture
    def workflows_dir(self):
        """Get the workflows directory path"""
        project_root = Path(__file__).parent.parent
        return project_root / ".github" / "workflows"

    def test_github_workflows_directory_exists(self, workflows_dir):
        """Test that .github/workflows directory exists"""
        assert workflows_dir.exists(), \
            ".github/workflows directory should exist"
        assert workflows_dir.is_dir(), \
            ".github/workflows should be a directory"

    def test_backend_ci_workflow_exists(self, workflows_dir):
        """Test that backend-ci.yml exists"""
        backend_ci = workflows_dir / "backend-ci.yml"
        assert backend_ci.exists(), \
            "backend-ci.yml should exist in .github/workflows/"

    def test_frontend_ci_workflow_exists(self, workflows_dir):
        """Test that frontend-ci.yml exists"""
        frontend_ci = workflows_dir / "frontend-ci.yml"
        assert frontend_ci.exists(), \
            "frontend-ci.yml should exist in .github/workflows/"

    def test_backend_ci_is_valid_yaml(self, workflows_dir):
        """Test that backend-ci.yml is valid YAML"""
        backend_ci = workflows_dir / "backend-ci.yml"
        with open(backend_ci) as f:
            try:
                content = yaml.safe_load(f)
                assert content is not None
            except yaml.YAMLError as e:
                pytest.fail(f"backend-ci.yml is not valid YAML: {e}")

    def test_frontend_ci_is_valid_yaml(self, workflows_dir):
        """Test that frontend-ci.yml is valid YAML"""
        frontend_ci = workflows_dir / "frontend-ci.yml"
        with open(frontend_ci) as f:
            try:
                content = yaml.safe_load(f)
                assert content is not None
            except yaml.YAMLError as e:
                pytest.fail(f"frontend-ci.yml is not valid YAML: {e}")


class TestBackendCIWorkflow:
    """Test backend CI workflow configuration"""

    @pytest.fixture
    def workflow(self):
        """Load the backend CI workflow"""
        project_root = Path(__file__).parent.parent
        workflow_path = project_root / ".github" / "workflows" / "backend-ci.yml"
        with open(workflow_path) as f:
            return yaml.safe_load(f)

    def test_has_name(self, workflow):
        """Test that workflow has a name"""
        assert "name" in workflow, "Workflow should have a name"
        assert workflow["name"] == "Backend CI"

    def test_has_trigger_on_push(self, workflow):
        """Test that workflow triggers on push"""
        assert "on" in workflow, "Workflow should have triggers"
        triggers = workflow["on"]
        assert "push" in triggers, "Workflow should trigger on push"

    def test_has_trigger_on_pull_request(self, workflow):
        """Test that workflow triggers on pull request"""
        triggers = workflow["on"]
        assert "pull_request" in triggers, \
            "Workflow should trigger on pull_request"

    def test_has_jobs(self, workflow):
        """Test that workflow has jobs defined"""
        assert "jobs" in workflow, "Workflow should have jobs"
        assert len(workflow["jobs"]) > 0, "Workflow should have at least one job"

    def test_has_test_and_lint_job(self, workflow):
        """Test that workflow has test-and-lint job"""
        jobs = workflow["jobs"]
        assert "test-and-lint" in jobs, \
            "Workflow should have test-and-lint job"

    def test_test_job_runs_on_ubuntu(self, workflow):
        """Test that test job runs on ubuntu-latest"""
        job = workflow["jobs"]["test-and-lint"]
        assert job["runs-on"] == "ubuntu-latest", \
            "Job should run on ubuntu-latest"

    def test_has_postgres_service(self, workflow):
        """Test that workflow has PostgreSQL service"""
        job = workflow["jobs"]["test-and-lint"]
        assert "services" in job, "Job should have services defined"
        services = job["services"]
        assert "postgres" in services, \
            "Job should have PostgreSQL service"

    def test_postgres_service_configuration(self, workflow):
        """Test PostgreSQL service is properly configured"""
        postgres = workflow["jobs"]["test-and-lint"]["services"]["postgres"]

        # Check image
        assert "image" in postgres, "PostgreSQL should have image"
        assert "postgres" in postgres["image"], \
            "Should use PostgreSQL image"

        # Check environment
        assert "env" in postgres, "PostgreSQL should have env vars"
        env = postgres["env"]
        assert "POSTGRES_USER" in env
        assert "POSTGRES_PASSWORD" in env
        assert "POSTGRES_DB" in env

        # Check ports
        assert "ports" in postgres, "PostgreSQL should expose ports"

    def test_has_redis_service(self, workflow):
        """Test that workflow has Redis service"""
        job = workflow["jobs"]["test-and-lint"]
        services = job["services"]
        assert "redis" in services, "Job should have Redis service"

    def test_redis_service_configuration(self, workflow):
        """Test Redis service is properly configured"""
        redis = workflow["jobs"]["test-and-lint"]["services"]["redis"]

        # Check image
        assert "image" in redis, "Redis should have image"
        assert "redis" in redis["image"], "Should use Redis image"

        # Check ports
        assert "ports" in redis, "Redis should expose ports"

    def test_has_python_setup_step(self, workflow):
        """Test that workflow has Python setup step"""
        steps = workflow["jobs"]["test-and-lint"]["steps"]
        python_steps = [s for s in steps if "setup-python" in s.get("uses", "")]
        assert len(python_steps) > 0, \
            "Workflow should have Python setup step"

    def test_has_install_dependencies_step(self, workflow):
        """Test that workflow has install dependencies step"""
        steps = workflow["jobs"]["test-and-lint"]["steps"]
        install_steps = [s for s in steps
                        if "Install dependencies" in s.get("name", "")]
        assert len(install_steps) > 0, \
            "Workflow should have install dependencies step"

    def test_has_pytest_step(self, workflow):
        """Test that workflow has pytest step"""
        steps = workflow["jobs"]["test-and-lint"]["steps"]
        pytest_steps = [s for s in steps
                       if "pytest" in s.get("name", "").lower()
                       or "test" in s.get("name", "").lower()]
        assert len(pytest_steps) > 0, \
            "Workflow should have pytest/test step"

    def test_pytest_step_has_env_vars(self, workflow):
        """Test that pytest step has required environment variables"""
        steps = workflow["jobs"]["test-and-lint"]["steps"]
        pytest_step = None
        for step in steps:
            # Find the step that runs pytest as its main command
            run_cmd = step.get("run", "")
            if run_cmd.strip().startswith("pytest"):
                pytest_step = step
                break

        assert pytest_step is not None, "Should have pytest step"
        assert "env" in pytest_step, "Pytest step should have env vars"
        env = pytest_step["env"]

        assert "DATABASE_URL" in env, "Should have DATABASE_URL"
        assert "REDIS_URL" in env, "Should have REDIS_URL"

    def test_has_coverage_upload(self, workflow):
        """Test that workflow uploads coverage"""
        steps = workflow["jobs"]["test-and-lint"]["steps"]
        coverage_steps = [s for s in steps
                         if "coverage" in s.get("name", "").lower()
                         or "codecov" in s.get("uses", "").lower()]
        assert len(coverage_steps) > 0, \
            "Workflow should have coverage upload step"


class TestFrontendCIWorkflow:
    """Test frontend CI workflow configuration"""

    @pytest.fixture
    def workflow(self):
        """Load the frontend CI workflow"""
        project_root = Path(__file__).parent.parent
        workflow_path = project_root / ".github" / "workflows" / "frontend-ci.yml"
        with open(workflow_path) as f:
            return yaml.safe_load(f)

    def test_has_name(self, workflow):
        """Test that workflow has a name"""
        assert "name" in workflow, "Workflow should have a name"
        assert workflow["name"] == "Frontend CI"

    def test_has_trigger_on_push(self, workflow):
        """Test that workflow triggers on push"""
        assert "on" in workflow, "Workflow should have triggers"
        triggers = workflow["on"]
        assert "push" in triggers, "Workflow should trigger on push"

    def test_has_trigger_on_pull_request(self, workflow):
        """Test that workflow triggers on pull request"""
        triggers = workflow["on"]
        assert "pull_request" in triggers, \
            "Workflow should trigger on pull_request"

    def test_has_jobs(self, workflow):
        """Test that workflow has jobs defined"""
        assert "jobs" in workflow, "Workflow should have jobs"
        assert len(workflow["jobs"]) > 0, \
            "Workflow should have at least one job"

    def test_has_test_and_build_job(self, workflow):
        """Test that workflow has test-and-build job"""
        jobs = workflow["jobs"]
        assert "test-and-build" in jobs, \
            "Workflow should have test-and-build job"

    def test_test_job_runs_on_ubuntu(self, workflow):
        """Test that test job runs on ubuntu-latest"""
        job = workflow["jobs"]["test-and-build"]
        assert job["runs-on"] == "ubuntu-latest", \
            "Job should run on ubuntu-latest"

    def test_has_node_setup_step(self, workflow):
        """Test that workflow has Node.js setup step"""
        steps = workflow["jobs"]["test-and-build"]["steps"]
        node_steps = [s for s in steps if "setup-node" in s.get("uses", "")]
        assert len(node_steps) > 0, \
            "Workflow should have Node.js setup step"

    def test_has_install_dependencies_step(self, workflow):
        """Test that workflow has install dependencies step"""
        steps = workflow["jobs"]["test-and-build"]["steps"]
        install_steps = [s for s in steps
                        if "Install dependencies" in s.get("name", "")]
        assert len(install_steps) > 0, \
            "Workflow should have install dependencies step"

    def test_uses_npm_ci(self, workflow):
        """Test that workflow uses npm ci for dependencies"""
        steps = workflow["jobs"]["test-and-build"]["steps"]
        install_step = None
        for step in steps:
            if "Install dependencies" in step.get("name", ""):
                install_step = step
                break

        assert install_step is not None
        assert "npm ci" in install_step.get("run", ""), \
            "Should use npm ci for reproducible builds"

    def test_has_lint_step(self, workflow):
        """Test that workflow has lint step"""
        steps = workflow["jobs"]["test-and-build"]["steps"]
        lint_steps = [s for s in steps
                     if "lint" in s.get("name", "").lower()]
        assert len(lint_steps) > 0, \
            "Workflow should have lint step"

    def test_has_test_step(self, workflow):
        """Test that workflow has test step"""
        steps = workflow["jobs"]["test-and-build"]["steps"]
        test_steps = [s for s in steps
                     if "test" in s.get("name", "").lower()]
        assert len(test_steps) > 0, \
            "Workflow should have test step"

    def test_has_build_step(self, workflow):
        """Test that workflow has build step"""
        steps = workflow["jobs"]["test-and-build"]["steps"]
        build_steps = [s for s in steps
                      if "build" in s.get("name", "").lower()]
        assert len(build_steps) > 0, \
            "Workflow should have build step"

    def test_has_artifact_upload(self, workflow):
        """Test that workflow uploads build artifacts"""
        steps = workflow["jobs"]["test-and-build"]["steps"]
        artifact_steps = [s for s in steps
                         if "upload-artifact" in s.get("uses", "")]
        assert len(artifact_steps) > 0, \
            "Workflow should have artifact upload step"

    def test_working_directory_is_frontend(self, workflow):
        """Test that steps use frontend working directory"""
        steps = workflow["jobs"]["test-and-build"]["steps"]

        # Find a step that should have working-directory
        for step in steps:
            if "npm" in step.get("run", ""):
                assert step.get("working-directory") == "./frontend", \
                    "npm steps should use ./frontend working directory"
                break


class TestWorkflowBranches:
    """Test that workflows trigger on correct branches"""

    @pytest.fixture
    def workflows_dir(self):
        """Get the workflows directory path"""
        project_root = Path(__file__).parent.parent
        return project_root / ".github" / "workflows"

    def test_backend_triggers_on_main_branches(self, workflows_dir):
        """Test backend CI triggers on main/master/develop"""
        workflow_path = workflows_dir / "backend-ci.yml"
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)

        push_branches = workflow["on"]["push"]["branches"]

        # Should trigger on at least one main branch
        main_branches = {"main", "master", "develop"}
        triggered_branches = set(push_branches)

        assert len(main_branches & triggered_branches) > 0, \
            "Should trigger on main/master/develop branches"

    def test_frontend_triggers_on_main_branches(self, workflows_dir):
        """Test frontend CI triggers on main/master/develop"""
        workflow_path = workflows_dir / "frontend-ci.yml"
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)

        push_branches = workflow["on"]["push"]["branches"]

        # Should trigger on at least one main branch
        main_branches = {"main", "master", "develop"}
        triggered_branches = set(push_branches)

        assert len(main_branches & triggered_branches) > 0, \
            "Should trigger on main/master/develop branches"
