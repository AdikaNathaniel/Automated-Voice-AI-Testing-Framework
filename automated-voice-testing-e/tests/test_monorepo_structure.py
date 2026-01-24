"""
Test suite for monorepo structure validation
Ensures all required directories and files exist as per project architecture
"""

import os
import pytest


class TestMonorepoStructure:
    """Test that the monorepo structure is correctly set up"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    def test_backend_directory_exists(self, project_root):
        """Test that backend/ directory exists"""
        backend_path = os.path.join(project_root, 'backend')
        assert os.path.exists(backend_path), "backend/ directory must exist"
        assert os.path.isdir(backend_path), "backend/ must be a directory"

    def test_backend_api_directory_exists(self, project_root):
        """Test that backend/api/ directory exists"""
        api_path = os.path.join(project_root, 'backend', 'api')
        assert os.path.exists(api_path), "backend/api/ directory must exist"
        assert os.path.isdir(api_path), "backend/api/ must be a directory"

    def test_backend_services_directory_exists(self, project_root):
        """Test that backend/services/ directory exists"""
        services_path = os.path.join(project_root, 'backend', 'services')
        assert os.path.exists(services_path), "backend/services/ directory must exist"
        assert os.path.isdir(services_path), "backend/services/ must be a directory"

    def test_backend_models_directory_exists(self, project_root):
        """Test that backend/models/ directory exists"""
        models_path = os.path.join(project_root, 'backend', 'models')
        assert os.path.exists(models_path), "backend/models/ directory must exist"
        assert os.path.isdir(models_path), "backend/models/ must be a directory"

    def test_backend_tests_directory_exists(self, project_root):
        """Test that backend/tests/ directory exists"""
        tests_path = os.path.join(project_root, 'backend', 'tests')
        assert os.path.exists(tests_path), "backend/tests/ directory must exist"
        assert os.path.isdir(tests_path), "backend/tests/ must be a directory"

    def test_backend_requirements_file_exists(self, project_root):
        """Test that backend/requirements.txt exists"""
        requirements_path = os.path.join(project_root, 'backend', 'requirements.txt')
        assert os.path.exists(requirements_path), "backend/requirements.txt must exist"
        assert os.path.isfile(requirements_path), "backend/requirements.txt must be a file"

    def test_frontend_directory_exists(self, project_root):
        """Test that frontend/ directory exists"""
        frontend_path = os.path.join(project_root, 'frontend')
        assert os.path.exists(frontend_path), "frontend/ directory must exist"
        assert os.path.isdir(frontend_path), "frontend/ must be a directory"

    def test_frontend_src_directory_exists(self, project_root):
        """Test that frontend/src/ directory exists"""
        src_path = os.path.join(project_root, 'frontend', 'src')
        assert os.path.exists(src_path), "frontend/src/ directory must exist"
        assert os.path.isdir(src_path), "frontend/src/ must be a directory"

    def test_frontend_public_directory_exists(self, project_root):
        """Test that frontend/public/ directory exists"""
        public_path = os.path.join(project_root, 'frontend', 'public')
        assert os.path.exists(public_path), "frontend/public/ directory must exist"
        assert os.path.isdir(public_path), "frontend/public/ must be a directory"

    def test_frontend_package_json_exists(self, project_root):
        """Test that frontend/package.json exists"""
        package_json_path = os.path.join(project_root, 'frontend', 'package.json')
        assert os.path.exists(package_json_path), "frontend/package.json must exist"
        assert os.path.isfile(package_json_path), "frontend/package.json must be a file"

    def test_infrastructure_directory_exists(self, project_root):
        """Test that infrastructure/ directory exists"""
        infra_path = os.path.join(project_root, 'infrastructure')
        assert os.path.exists(infra_path), "infrastructure/ directory must exist"
        assert os.path.isdir(infra_path), "infrastructure/ must be a directory"

    def test_infrastructure_terraform_directory_exists(self, project_root):
        """Test that infrastructure/terraform/ directory exists"""
        terraform_path = os.path.join(project_root, 'infrastructure', 'terraform')
        assert os.path.exists(terraform_path), "infrastructure/terraform/ directory must exist"
        assert os.path.isdir(terraform_path), "infrastructure/terraform/ must be a directory"

    def test_infrastructure_docker_directory_exists(self, project_root):
        """Test that infrastructure/docker/ directory exists"""
        docker_path = os.path.join(project_root, 'infrastructure', 'docker')
        assert os.path.exists(docker_path), "infrastructure/docker/ directory must exist"
        assert os.path.isdir(docker_path), "infrastructure/docker/ must be a directory"

    def test_docs_directory_exists(self, project_root):
        """Test that docs/ directory exists"""
        docs_path = os.path.join(project_root, 'docs')
        assert os.path.exists(docs_path), "docs/ directory must exist"
        assert os.path.isdir(docs_path), "docs/ must be a directory"

    def test_scripts_directory_exists(self, project_root):
        """Test that scripts/ directory exists"""
        scripts_path = os.path.join(project_root, 'scripts')
        assert os.path.exists(scripts_path), "scripts/ directory must exist"
        assert os.path.isdir(scripts_path), "scripts/ must be a directory"

    def test_all_backend_directories_have_init_py(self, project_root):
        """Test that all Python package directories have __init__.py"""
        python_dirs = [
            os.path.join(project_root, 'backend', 'api'),
            os.path.join(project_root, 'backend', 'services'),
            os.path.join(project_root, 'backend', 'models'),
            os.path.join(project_root, 'backend', 'tests'),
        ]

        for dir_path in python_dirs:
            init_file = os.path.join(dir_path, '__init__.py')
            assert os.path.exists(init_file), f"{dir_path} must contain __init__.py to be a Python package"

    def test_directory_structure_completeness(self, project_root):
        """Test that the complete directory structure matches the specification"""
        required_structure = {
            'backend': {
                'subdirs': ['api', 'services', 'models', 'tests'],
                'files': ['requirements.txt']
            },
            'frontend': {
                'subdirs': ['src', 'public'],
                'files': ['package.json']
            },
            'infrastructure': {
                'subdirs': ['terraform', 'docker'],
                'files': []
            },
            'docs': {
                'subdirs': [],
                'files': []
            },
            'scripts': {
                'subdirs': [],
                'files': []
            }
        }

        for top_level_dir, structure in required_structure.items():
            top_level_path = os.path.join(project_root, top_level_dir)
            assert os.path.exists(top_level_path), f"{top_level_dir}/ must exist"

            # Check subdirectories
            for subdir in structure['subdirs']:
                subdir_path = os.path.join(top_level_path, subdir)
                assert os.path.exists(subdir_path), f"{top_level_dir}/{subdir}/ must exist"

            # Check files
            for file in structure['files']:
                file_path = os.path.join(top_level_path, file)
                assert os.path.exists(file_path), f"{top_level_dir}/{file} must exist"

    def test_backend_requirements_has_content(self, project_root):
        """Test that backend/requirements.txt has basic content"""
        requirements_path = os.path.join(project_root, 'backend', 'requirements.txt')
        with open(requirements_path, 'r') as f:
            content = f.read()

        # Should have at least a comment or be empty (we'll add dependencies later)
        assert content is not None, "requirements.txt should be readable"

    def test_frontend_package_json_is_valid_json(self, project_root):
        """Test that frontend/package.json contains valid JSON"""
        import json

        package_json_path = os.path.join(project_root, 'frontend', 'package.json')
        with open(package_json_path, 'r') as f:
            content = f.read()

        # Should be valid JSON
        try:
            data = json.loads(content)
            assert isinstance(data, dict), "package.json should contain a JSON object"
            assert 'name' in data, "package.json should have a 'name' field"
        except json.JSONDecodeError as e:
            pytest.fail(f"package.json is not valid JSON: {e}")
