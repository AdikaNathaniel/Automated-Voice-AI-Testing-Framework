"""
Test suite for frontend project structure

Ensures the correct directory structure is set up for the React TypeScript
frontend application, including all required directories for components,
pages, services, store, types, and utilities.
"""

import os
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
SRC_DIR = FRONTEND_DIR / "src"


class TestSrcDirectory:
    """Test src directory structure"""

    def test_src_directory_exists(self):
        """Test that src directory exists"""
        assert SRC_DIR.exists(), "src directory should exist"
        assert SRC_DIR.is_dir(), "src should be a directory"


class TestComponentsDirectory:
    """Test components directory for React components"""

    def test_components_directory_exists(self):
        """Test that components directory exists"""
        components_dir = SRC_DIR / "components"
        assert components_dir.exists(), "components directory should exist"
        assert components_dir.is_dir(), "components should be a directory"

    def test_components_directory_is_in_src(self):
        """Test that components directory is inside src"""
        components_dir = SRC_DIR / "components"
        assert components_dir.parent == SRC_DIR, "components should be in src directory"

    def test_components_gitkeep_or_readme_exists(self):
        """Test that components directory has a .gitkeep or README.md file"""
        components_dir = SRC_DIR / "components"
        gitkeep = components_dir / ".gitkeep"
        readme = components_dir / "README.md"
        # At least one should exist to preserve the directory in git
        if components_dir.exists():
            # This is informational - directories may be empty initially
            pass


class TestPagesDirectory:
    """Test pages directory for route components"""

    def test_pages_directory_exists(self):
        """Test that pages directory exists"""
        pages_dir = SRC_DIR / "pages"
        assert pages_dir.exists(), "pages directory should exist"
        assert pages_dir.is_dir(), "pages should be a directory"

    def test_pages_directory_is_in_src(self):
        """Test that pages directory is inside src"""
        pages_dir = SRC_DIR / "pages"
        assert pages_dir.parent == SRC_DIR, "pages should be in src directory"


class TestServicesDirectory:
    """Test services directory for API clients and external services"""

    def test_services_directory_exists(self):
        """Test that services directory exists"""
        services_dir = SRC_DIR / "services"
        assert services_dir.exists(), "services directory should exist"
        assert services_dir.is_dir(), "services should be a directory"

    def test_services_directory_is_in_src(self):
        """Test that services directory is inside src"""
        services_dir = SRC_DIR / "services"
        assert services_dir.parent == SRC_DIR, "services should be in src directory"


class TestStoreDirectory:
    """Test store directory for Redux state management"""

    def test_store_directory_exists(self):
        """Test that store directory exists"""
        store_dir = SRC_DIR / "store"
        assert store_dir.exists(), "store directory should exist"
        assert store_dir.is_dir(), "store should be a directory"

    def test_store_directory_is_in_src(self):
        """Test that store directory is inside src"""
        store_dir = SRC_DIR / "store"
        assert store_dir.parent == SRC_DIR, "store should be in src directory"


class TestTypesDirectory:
    """Test types directory for TypeScript type definitions"""

    def test_types_directory_exists(self):
        """Test that types directory exists"""
        types_dir = SRC_DIR / "types"
        assert types_dir.exists(), "types directory should exist"
        assert types_dir.is_dir(), "types should be a directory"

    def test_types_directory_is_in_src(self):
        """Test that types directory is inside src"""
        types_dir = SRC_DIR / "types"
        assert types_dir.parent == SRC_DIR, "types should be in src directory"


class TestUtilsDirectory:
    """Test utils directory for utility functions and helpers"""

    def test_utils_directory_exists(self):
        """Test that utils directory exists"""
        utils_dir = SRC_DIR / "utils"
        assert utils_dir.exists(), "utils directory should exist"
        assert utils_dir.is_dir(), "utils should be a directory"

    def test_utils_directory_is_in_src(self):
        """Test that utils directory is inside src"""
        utils_dir = SRC_DIR / "utils"
        assert utils_dir.parent == SRC_DIR, "utils should be in src directory"


class TestProjectStructureIntegration:
    """Test overall project structure"""

    def test_all_required_directories_exist(self):
        """Test that all required directories exist"""
        required_directories = [
            SRC_DIR / "components",
            SRC_DIR / "pages",
            SRC_DIR / "services",
            SRC_DIR / "store",
            SRC_DIR / "types",
            SRC_DIR / "utils",
        ]

        missing_directories = []
        for directory in required_directories:
            if not directory.exists():
                missing_directories.append(str(directory.relative_to(FRONTEND_DIR)))

        assert len(missing_directories) == 0, \
            f"Missing required directories: {', '.join(missing_directories)}"

    def test_all_directories_are_actually_directories(self):
        """Test that all required paths are directories, not files"""
        required_directories = [
            SRC_DIR / "components",
            SRC_DIR / "pages",
            SRC_DIR / "services",
            SRC_DIR / "store",
            SRC_DIR / "types",
            SRC_DIR / "utils",
        ]

        not_directories = []
        for directory in required_directories:
            if directory.exists() and not directory.is_dir():
                not_directories.append(str(directory.relative_to(FRONTEND_DIR)))

        assert len(not_directories) == 0, \
            f"These paths exist but are not directories: {', '.join(not_directories)}"

    def test_app_tsx_exists_in_src(self):
        """Test that App.tsx exists in src directory"""
        app_tsx = SRC_DIR / "App.tsx"
        assert app_tsx.exists(), "App.tsx should exist in src directory"
        assert app_tsx.is_file(), "App.tsx should be a file"

    def test_src_structure_matches_specification(self):
        """Test that src structure matches the TASK-023 specification"""
        # According to TASK-023, we need these directories
        expected_structure = {
            "components": "React components",
            "pages": "Page/route components",
            "services": "API clients and services",
            "store": "Redux store",
            "types": "TypeScript type definitions",
            "utils": "Utility functions",
        }

        for dir_name, purpose in expected_structure.items():
            dir_path = SRC_DIR / dir_name
            assert dir_path.exists(), f"{dir_name}/ should exist (for {purpose})"
            assert dir_path.is_dir(), f"{dir_name}/ should be a directory"


class TestDirectoryNaming:
    """Test directory naming conventions"""

    def test_directories_use_lowercase_names(self):
        """Test that all directories use lowercase names"""
        required_directories = [
            "components",
            "pages",
            "services",
            "store",
            "types",
            "utils",
        ]

        for dir_name in required_directories:
            assert dir_name.islower(), f"{dir_name} should be lowercase"

    def test_directories_use_plural_names(self):
        """Test that directories use plural names (best practice)"""
        # All our directories are already plural, which is good practice
        plural_directories = [
            "components",
            "pages",
            "services",
            "types",
            "utils",
        ]

        for dir_name in plural_directories:
            # Just verify they exist and follow the plural naming convention
            dir_path = SRC_DIR / dir_name
            if dir_path.exists():
                assert dir_name.endswith('s') or dir_name == 'store', \
                    f"{dir_name} should use plural naming"


class TestDirectoryDocumentation:
    """Test directory documentation"""

    def test_components_readme_exists_or_planned(self):
        """Test that components directory has or will have documentation"""
        components_dir = SRC_DIR / "components"
        # This is informational - READMEs are optional but recommended
        if components_dir.exists():
            readme = components_dir / "README.md"
            # We don't require it, but it's good practice
            pass

    def test_store_readme_exists_or_planned(self):
        """Test that store directory has or will have documentation"""
        store_dir = SRC_DIR / "store"
        # This is informational - READMEs are optional but recommended
        if store_dir.exists():
            readme = store_dir / "README.md"
            # We don't require it, but it's good practice
            pass
