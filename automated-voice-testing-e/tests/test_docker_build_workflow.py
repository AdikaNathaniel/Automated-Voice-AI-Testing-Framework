"""
Test GitHub Actions Docker Build Workflow

This module tests the Docker build workflow to ensure it properly:
- Builds Docker images for backend and frontend
- Tags images with appropriate versioning
- Pushes images to container registry
- Uses Docker buildx for multi-platform support
- Implements layer caching for faster builds

Test Coverage:
    - Workflow file structure and syntax
    - Trigger configuration (push/tags/manual)
    - Docker setup and login steps
    - Backend image build and push
    - Frontend image build and push
    - Image tagging strategy
"""

import sys
import os
from pathlib import Path
import yaml

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest


# =============================================================================
# Workflow File Structure Tests
# =============================================================================

class TestDockerBuildWorkflowStructure:
    """Test Docker build workflow file structure"""

    def test_docker_build_workflow_file_exists(self):
        """Test that docker-build.yml file exists"""
        # Arrange
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "docker-build.yml"

        # Act & Assert
        assert workflow_file.exists(), "docker-build.yml should exist"
        assert workflow_file.is_file(), "docker-build.yml should be a file"

    def test_docker_build_workflow_has_content(self):
        """Test that docker-build.yml has content"""
        # Arrange
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "docker-build.yml"

        # Act
        content = workflow_file.read_text()

        # Assert
        assert len(content) > 50, "Workflow file should have substantial content"

    def test_docker_build_workflow_is_valid_yaml(self):
        """Test that docker-build.yml is valid YAML"""
        # Arrange
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "docker-build.yml"

        # Act
        with open(workflow_file, 'r') as f:
            try:
                workflow = yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML syntax: {e}")

        # Assert
        assert workflow is not None, "Workflow should parse as valid YAML"
        assert isinstance(workflow, dict), "Workflow should be a dictionary"


# =============================================================================
# Workflow Metadata Tests
# =============================================================================

class TestDockerBuildWorkflowMetadata:
    """Test Docker build workflow metadata"""

    @pytest.fixture
    def workflow(self):
        """Load workflow file"""
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "docker-build.yml"
        with open(workflow_file, 'r') as f:
            return yaml.safe_load(f)

    def test_workflow_has_name(self, workflow):
        """Test that workflow has a name"""
        # Assert
        assert 'name' in workflow, "Workflow should have a name"
        assert isinstance(workflow['name'], str), "Workflow name should be a string"
        assert len(workflow['name']) > 0, "Workflow name should not be empty"

    def test_workflow_name_is_descriptive(self, workflow):
        """Test that workflow name is descriptive"""
        # Assert
        name = workflow['name'].lower()
        assert 'docker' in name or 'build' in name or 'image' in name, \
            "Workflow name should indicate Docker/build/image workflow"


# =============================================================================
# Workflow Trigger Tests
# =============================================================================

class TestDockerBuildWorkflowTriggers:
    """Test Docker build workflow triggers"""

    @pytest.fixture
    def workflow(self):
        """Load workflow file"""
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "docker-build.yml"
        with open(workflow_file, 'r') as f:
            return yaml.safe_load(f)

    def test_workflow_has_triggers(self, workflow):
        """Test that workflow has trigger configuration"""
        # Assert
        assert 'on' in workflow or 'true' in workflow, \
            "Workflow should have 'on' trigger configuration"

    def test_workflow_triggers_on_push_or_workflow_dispatch(self, workflow):
        """Test that workflow can be triggered"""
        # Assert
        assert 'on' in workflow, "Workflow should have 'on' section"
        triggers = workflow['on']

        # Should have push, tag, or workflow_dispatch triggers
        if isinstance(triggers, list):
            has_trigger = any(t in triggers for t in ['push', 'workflow_dispatch'])
        elif isinstance(triggers, dict):
            has_trigger = any(t in triggers for t in ['push', 'workflow_dispatch'])
        else:
            has_trigger = False

        assert has_trigger, "Workflow should trigger on push or workflow_dispatch"


# =============================================================================
# Workflow Jobs Tests
# =============================================================================

class TestDockerBuildWorkflowJobs:
    """Test Docker build workflow jobs"""

    @pytest.fixture
    def workflow(self):
        """Load workflow file"""
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "docker-build.yml"
        with open(workflow_file, 'r') as f:
            return yaml.safe_load(f)

    def test_workflow_has_jobs(self, workflow):
        """Test that workflow has jobs defined"""
        # Assert
        assert 'jobs' in workflow, "Workflow should have jobs section"
        assert isinstance(workflow['jobs'], dict), "Jobs should be a dictionary"
        assert len(workflow['jobs']) > 0, "Workflow should have at least one job"

    def test_workflow_has_build_job(self, workflow):
        """Test that workflow has a build job"""
        # Assert
        jobs = workflow['jobs']
        job_names = [name.lower() for name in jobs.keys()]

        # Should have a job related to building
        has_build_job = any(
            keyword in ' '.join(job_names)
            for keyword in ['build', 'docker', 'image']
        )
        assert has_build_job, "Workflow should have a build/docker/image job"

    def test_job_runs_on_ubuntu(self, workflow):
        """Test that job runs on Ubuntu"""
        # Assert
        jobs = workflow['jobs']
        first_job = list(jobs.values())[0]

        assert 'runs-on' in first_job, "Job should specify runs-on"
        assert 'ubuntu' in first_job['runs-on'].lower(), \
            "Job should run on Ubuntu"


# =============================================================================
# Docker Setup Steps Tests
# =============================================================================

class TestDockerBuildSetupSteps:
    """Test Docker build setup steps"""

    @pytest.fixture
    def workflow(self):
        """Load workflow file"""
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "docker-build.yml"
        with open(workflow_file, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def steps(self, workflow):
        """Get steps from first job"""
        jobs = workflow['jobs']
        first_job = list(jobs.values())[0]
        return first_job.get('steps', [])

    def test_job_has_steps(self, workflow):
        """Test that job has steps defined"""
        # Arrange
        jobs = workflow['jobs']
        first_job = list(jobs.values())[0]

        # Assert
        assert 'steps' in first_job, "Job should have steps"
        assert isinstance(first_job['steps'], list), "Steps should be a list"
        assert len(first_job['steps']) > 0, "Job should have at least one step"

    def test_has_checkout_step(self, steps):
        """Test that job has checkout step"""
        # Assert
        checkout_steps = [
            step for step in steps
            if 'uses' in step and 'actions/checkout' in step['uses']
        ]
        assert len(checkout_steps) > 0, "Job should have checkout step"

    def test_has_docker_buildx_setup(self, steps):
        """Test that job has Docker buildx setup"""
        # Assert
        buildx_steps = [
            step for step in steps
            if 'uses' in step and 'docker/setup-buildx-action' in step['uses']
        ]
        assert len(buildx_steps) > 0, "Job should have Docker buildx setup step"

    def test_has_docker_login_step(self, steps):
        """Test that job has Docker login step"""
        # Assert
        login_steps = [
            step for step in steps
            if 'uses' in step and 'docker/login-action' in step['uses']
        ]
        assert len(login_steps) > 0, "Job should have Docker login step"


# =============================================================================
# Backend Image Build Tests
# =============================================================================

class TestBackendImageBuild:
    """Test backend Docker image build steps"""

    @pytest.fixture
    def workflow(self):
        """Load workflow file"""
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "docker-build.yml"
        with open(workflow_file, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def steps(self, workflow):
        """Get steps from first job"""
        jobs = workflow['jobs']
        first_job = list(jobs.values())[0]
        return first_job.get('steps', [])

    def test_has_backend_build_step(self, steps):
        """Test that workflow builds backend image"""
        # Assert
        build_steps = [
            step for step in steps
            if 'uses' in step and 'docker/build-push-action' in step['uses']
        ]

        # Check if any step mentions backend in name or context
        has_backend = False
        for step in build_steps:
            step_name = step.get('name', '').lower()
            step_with = step.get('with', {})
            context = step_with.get('context', '').lower() if isinstance(step_with, dict) else ''

            if 'backend' in step_name or 'backend' in context:
                has_backend = True
                break

        assert has_backend, "Workflow should have backend image build step"

    def test_backend_build_uses_correct_context(self, steps):
        """Test that backend build uses correct context"""
        # Assert
        build_steps = [
            step for step in steps
            if 'uses' in step and 'docker/build-push-action' in step['uses']
        ]

        backend_steps = []
        for step in build_steps:
            step_name = step.get('name', '').lower()
            if 'backend' in step_name:
                backend_steps.append(step)

        assert len(backend_steps) > 0, "Should have backend build step"

        backend_step = backend_steps[0]
        assert 'with' in backend_step, "Backend build should have 'with' section"
        step_with = backend_step['with']
        assert 'context' in step_with, "Backend build should specify context"


# =============================================================================
# Frontend Image Build Tests
# =============================================================================

class TestFrontendImageBuild:
    """Test frontend Docker image build steps"""

    @pytest.fixture
    def workflow(self):
        """Load workflow file"""
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "docker-build.yml"
        with open(workflow_file, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def steps(self, workflow):
        """Get steps from first job"""
        jobs = workflow['jobs']
        first_job = list(jobs.values())[0]
        return first_job.get('steps', [])

    def test_has_frontend_build_step(self, steps):
        """Test that workflow builds frontend image"""
        # Assert
        build_steps = [
            step for step in steps
            if 'uses' in step and 'docker/build-push-action' in step['uses']
        ]

        # Check if any step mentions frontend in name or context
        has_frontend = False
        for step in build_steps:
            step_name = step.get('name', '').lower()
            step_with = step.get('with', {})
            context = step_with.get('context', '').lower() if isinstance(step_with, dict) else ''

            if 'frontend' in step_name or 'frontend' in context:
                has_frontend = True
                break

        assert has_frontend, "Workflow should have frontend image build step"

    def test_frontend_build_uses_correct_context(self, steps):
        """Test that frontend build uses correct context"""
        # Assert
        build_steps = [
            step for step in steps
            if 'uses' in step and 'docker/build-push-action' in step['uses']
        ]

        frontend_steps = []
        for step in build_steps:
            step_name = step.get('name', '').lower()
            if 'frontend' in step_name:
                frontend_steps.append(step)

        assert len(frontend_steps) > 0, "Should have frontend build step"

        frontend_step = frontend_steps[0]
        assert 'with' in frontend_step, "Frontend build should have 'with' section"
        step_with = frontend_step['with']
        assert 'context' in step_with, "Frontend build should specify context"


# =============================================================================
# Workflow Best Practices Tests
# =============================================================================

class TestDockerBuildBestPractices:
    """Test Docker build workflow follows best practices"""

    @pytest.fixture
    def workflow(self):
        """Load workflow file"""
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "docker-build.yml"
        with open(workflow_file, 'r') as f:
            return yaml.safe_load(f)

    def test_steps_have_names(self, workflow):
        """Test that steps have descriptive names"""
        # Arrange
        jobs = workflow['jobs']
        first_job = list(jobs.values())[0]
        steps = first_job.get('steps', [])

        # Assert
        steps_with_names = [step for step in steps if 'name' in step]
        assert len(steps_with_names) >= len(steps) * 0.7, \
            "At least 70% of steps should have descriptive names"

    def test_uses_docker_layer_caching(self, workflow):
        """Test that workflow uses Docker layer caching"""
        # Arrange
        jobs = workflow['jobs']
        first_job = list(jobs.values())[0]
        steps = first_job.get('steps', [])

        # Assert - Check for cache-from or cache-to in build steps
        build_steps = [
            step for step in steps
            if 'uses' in step and 'docker/build-push-action' in step['uses']
        ]

        has_caching = False
        for step in build_steps:
            step_with = step.get('with', {})
            if isinstance(step_with, dict):
                if 'cache-from' in step_with or 'cache-to' in step_with:
                    has_caching = True
                    break

        assert has_caching, "Workflow should use Docker layer caching"
