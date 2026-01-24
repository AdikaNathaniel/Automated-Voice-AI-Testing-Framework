"""
Test GitHub Actions Backend CI Workflow

This module tests the backend CI workflow to ensure it properly:
- Sets up Python environment
- Installs dependencies
- Runs linting (ruff/black)
- Executes tests
- Uploads coverage reports

Test Coverage:
    - Workflow file structure and syntax
    - Trigger configuration (push/pull_request)
    - Job steps and actions
    - Environment setup
    - Linting and testing steps
    - Coverage reporting
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

class TestBackendCIWorkflowStructure:
    """Test backend CI workflow file structure"""

    def test_github_workflows_directory_exists(self):
        """Test that .github/workflows directory exists"""
        # Arrange
        project_root = Path(__file__).parent.parent
        workflows_dir = project_root / ".github" / "workflows"

        # Act & Assert
        assert workflows_dir.exists(), ".github/workflows directory should exist"
        assert workflows_dir.is_dir(), ".github/workflows should be a directory"

    def test_backend_ci_workflow_file_exists(self):
        """Test that backend-ci.yml file exists"""
        # Arrange
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "backend-ci.yml"

        # Act & Assert
        assert workflow_file.exists(), "backend-ci.yml should exist"
        assert workflow_file.is_file(), "backend-ci.yml should be a file"

    def test_backend_ci_workflow_has_content(self):
        """Test that backend-ci.yml has content"""
        # Arrange
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "backend-ci.yml"

        # Act
        content = workflow_file.read_text()

        # Assert
        assert len(content) > 50, "Workflow file should have substantial content"

    def test_backend_ci_workflow_is_valid_yaml(self):
        """Test that backend-ci.yml is valid YAML"""
        # Arrange
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "backend-ci.yml"

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

class TestBackendCIWorkflowMetadata:
    """Test backend CI workflow metadata"""

    @pytest.fixture
    def workflow(self):
        """Load workflow file"""
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "backend-ci.yml"
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
        assert 'backend' in name or 'python' in name or 'ci' in name, \
            "Workflow name should indicate backend/Python CI"


# =============================================================================
# Workflow Trigger Tests
# =============================================================================

class TestBackendCIWorkflowTriggers:
    """Test backend CI workflow triggers"""

    @pytest.fixture
    def workflow(self):
        """Load workflow file"""
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "backend-ci.yml"
        with open(workflow_file, 'r') as f:
            return yaml.safe_load(f)

    def test_workflow_has_triggers(self, workflow):
        """Test that workflow has trigger configuration"""
        # Assert
        assert 'on' in workflow or 'true' in workflow, \
            "Workflow should have 'on' trigger configuration"

    def test_workflow_triggers_on_push(self, workflow):
        """Test that workflow triggers on push"""
        # Assert
        assert 'on' in workflow, "Workflow should have 'on' section"
        triggers = workflow['on']

        # Can be a list or dict
        if isinstance(triggers, list):
            assert 'push' in triggers, "Workflow should trigger on push"
        elif isinstance(triggers, dict):
            assert 'push' in triggers, "Workflow should trigger on push"

    def test_workflow_triggers_on_pull_request(self, workflow):
        """Test that workflow triggers on pull requests"""
        # Assert
        triggers = workflow['on']

        if isinstance(triggers, list):
            assert 'pull_request' in triggers, "Workflow should trigger on pull_request"
        elif isinstance(triggers, dict):
            assert 'pull_request' in triggers, "Workflow should trigger on pull_request"


# =============================================================================
# Workflow Jobs Tests
# =============================================================================

class TestBackendCIWorkflowJobs:
    """Test backend CI workflow jobs"""

    @pytest.fixture
    def workflow(self):
        """Load workflow file"""
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "backend-ci.yml"
        with open(workflow_file, 'r') as f:
            return yaml.safe_load(f)

    def test_workflow_has_jobs(self, workflow):
        """Test that workflow has jobs defined"""
        # Assert
        assert 'jobs' in workflow, "Workflow should have jobs section"
        assert isinstance(workflow['jobs'], dict), "Jobs should be a dictionary"
        assert len(workflow['jobs']) > 0, "Workflow should have at least one job"

    def test_workflow_has_test_job(self, workflow):
        """Test that workflow has a test/lint/ci job"""
        # Assert
        jobs = workflow['jobs']
        job_names = [name.lower() for name in jobs.keys()]

        # Should have a job related to testing/linting/ci
        has_relevant_job = any(
            keyword in ' '.join(job_names)
            for keyword in ['test', 'lint', 'ci', 'check', 'build']
        )
        assert has_relevant_job, "Workflow should have a test/lint/ci job"

    def test_job_runs_on_ubuntu(self, workflow):
        """Test that job runs on Ubuntu"""
        # Assert
        jobs = workflow['jobs']
        first_job = list(jobs.values())[0]

        assert 'runs-on' in first_job, "Job should specify runs-on"
        assert 'ubuntu' in first_job['runs-on'].lower(), \
            "Job should run on Ubuntu"


# =============================================================================
# Job Steps Tests
# =============================================================================

class TestBackendCIJobSteps:
    """Test backend CI job steps"""

    @pytest.fixture
    def workflow(self):
        """Load workflow file"""
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "backend-ci.yml"
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

    def test_has_python_setup_step(self, steps):
        """Test that job has Python setup step"""
        # Assert
        python_steps = [
            step for step in steps
            if 'uses' in step and 'actions/setup-python' in step['uses']
        ]
        assert len(python_steps) > 0, "Job should have Python setup step"

    def test_python_setup_specifies_version(self, steps):
        """Test that Python setup specifies version"""
        # Arrange
        python_steps = [
            step for step in steps
            if 'uses' in step and 'actions/setup-python' in step['uses']
        ]

        # Assert
        assert len(python_steps) > 0, "Should have Python setup step"
        python_step = python_steps[0]
        assert 'with' in python_step, "Python setup should have 'with' section"
        assert 'python-version' in python_step['with'], \
            "Python setup should specify python-version"

    def test_has_dependency_installation_step(self, steps):
        """Test that job has dependency installation step"""
        # Assert
        install_steps = [
            step for step in steps
            if 'run' in step and 'pip install' in step['run']
        ]
        assert len(install_steps) > 0, \
            "Job should have pip install step for dependencies"

    def test_has_linting_step(self, steps):
        """Test that job has linting step"""
        # Assert
        lint_steps = [
            step for step in steps
            if 'run' in step and ('ruff' in step['run'].lower() or 'black' in step['run'].lower() or 'lint' in step['run'].lower())
        ]
        assert len(lint_steps) > 0, "Job should have linting step (ruff or black)"

    def test_has_test_execution_step(self, steps):
        """Test that job has test execution step"""
        # Assert
        test_steps = [
            step for step in steps
            if 'run' in step and 'pytest' in step['run'].lower()
        ]
        assert len(test_steps) > 0, "Job should have pytest test execution step"

    def test_has_coverage_step(self, steps):
        """Test that job has coverage reporting step"""
        # Assert
        coverage_steps = [
            step for step in steps
            if ('run' in step and 'coverage' in step['run'].lower()) or
               ('uses' in step and 'codecov' in step['uses'].lower())
        ]
        assert len(coverage_steps) > 0, \
            "Job should have coverage reporting step (pytest-cov or codecov)"


# =============================================================================
# Workflow Best Practices Tests
# =============================================================================

class TestBackendCIBestPractices:
    """Test backend CI workflow follows best practices"""

    @pytest.fixture
    def workflow(self):
        """Load workflow file"""
        project_root = Path(__file__).parent.parent
        workflow_file = project_root / ".github" / "workflows" / "backend-ci.yml"
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

    def test_uses_caching_for_dependencies(self, workflow):
        """Test that workflow uses caching for pip dependencies"""
        # Arrange
        jobs = workflow['jobs']
        first_job = list(jobs.values())[0]
        steps = first_job.get('steps', [])

        # Assert - Check if setup-python has cache enabled OR separate cache action
        python_steps = [
            step for step in steps
            if 'uses' in step and 'actions/setup-python' in step['uses']
        ]

        cache_steps = [
            step for step in steps
            if 'uses' in step and 'actions/cache' in step['uses']
        ]

        has_caching = False
        if python_steps and 'with' in python_steps[0]:
            has_caching = 'cache' in python_steps[0]['with']

        if cache_steps:
            has_caching = True

        assert has_caching, "Workflow should use caching for dependencies"
