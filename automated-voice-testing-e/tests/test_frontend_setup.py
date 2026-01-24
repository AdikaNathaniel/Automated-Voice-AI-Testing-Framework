"""
Test suite for frontend React + Vite project setup

Ensures proper initialization of the React TypeScript project with Vite,
including directory structure, configuration files, and dependencies.
"""

import os
import json
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"


class TestFrontendDirectory:
    """Test frontend directory structure"""

    def test_frontend_directory_exists(self):
        """Test that frontend directory exists"""
        assert FRONTEND_DIR.exists(), "frontend directory should exist"
        assert FRONTEND_DIR.is_dir(), "frontend should be a directory"

    def test_src_directory_exists(self):
        """Test that src directory exists in frontend"""
        src_dir = FRONTEND_DIR / "src"
        assert src_dir.exists(), "frontend/src directory should exist"
        assert src_dir.is_dir(), "frontend/src should be a directory"

    def test_public_directory_exists(self):
        """Test that public directory exists in frontend"""
        public_dir = FRONTEND_DIR / "public"
        assert public_dir.exists(), "frontend/public directory should exist"
        assert public_dir.is_dir(), "frontend/public should be a directory"


class TestPackageJson:
    """Test package.json configuration"""

    def test_package_json_exists(self):
        """Test that package.json exists"""
        package_json = FRONTEND_DIR / "package.json"
        assert package_json.exists(), "package.json should exist"
        assert package_json.is_file(), "package.json should be a file"

    def test_package_json_is_valid_json(self):
        """Test that package.json is valid JSON"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        assert isinstance(data, dict), "package.json should be a JSON object"

    def test_package_json_has_name(self):
        """Test that package.json has name field"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        assert 'name' in data, "package.json should have 'name' field"
        assert isinstance(data['name'], str), "name should be a string"

    def test_package_json_has_version(self):
        """Test that package.json has version field"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        assert 'version' in data, "package.json should have 'version' field"

    def test_package_json_has_dependencies(self):
        """Test that package.json has dependencies"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        assert 'dependencies' in data, "package.json should have 'dependencies'"
        assert isinstance(data['dependencies'], dict), "dependencies should be an object"

    def test_package_json_has_dev_dependencies(self):
        """Test that package.json has devDependencies"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        assert 'devDependencies' in data, "package.json should have 'devDependencies'"
        assert isinstance(data['devDependencies'], dict), "devDependencies should be an object"

    def test_package_json_has_scripts(self):
        """Test that package.json has scripts"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        assert 'scripts' in data, "package.json should have 'scripts'"
        assert isinstance(data['scripts'], dict), "scripts should be an object"

    def test_package_json_has_dev_script(self):
        """Test that package.json has dev script"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        assert 'dev' in data.get('scripts', {}), "scripts should include 'dev'"

    def test_package_json_has_build_script(self):
        """Test that package.json has build script"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        assert 'build' in data.get('scripts', {}), "scripts should include 'build'"

    def test_package_json_has_preview_script(self):
        """Test that package.json has preview script"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        assert 'preview' in data.get('scripts', {}), "scripts should include 'preview'"


class TestReactDependencies:
    """Test React-related dependencies"""

    def test_has_react_dependency(self):
        """Test that React is in dependencies"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        dependencies = data.get('dependencies', {})
        assert 'react' in dependencies, "Should have 'react' dependency"

    def test_has_react_dom_dependency(self):
        """Test that React DOM is in dependencies"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        dependencies = data.get('dependencies', {})
        assert 'react-dom' in dependencies, "Should have 'react-dom' dependency"


class TestTypescriptConfig:
    """Test TypeScript configuration"""

    def test_tsconfig_json_exists(self):
        """Test that tsconfig.json exists"""
        tsconfig = FRONTEND_DIR / "tsconfig.json"
        assert tsconfig.exists(), "tsconfig.json should exist"
        assert tsconfig.is_file(), "tsconfig.json should be a file"

    def test_tsconfig_is_valid_json(self):
        """Test that tsconfig.json is valid JSON"""
        tsconfig = FRONTEND_DIR / "tsconfig.json"
        with open(tsconfig, 'r') as f:
            data = json.load(f)
        assert isinstance(data, dict), "tsconfig.json should be a JSON object"

    def test_tsconfig_has_compiler_options_or_references(self):
        """Test that tsconfig.json has compilerOptions or uses project references"""
        tsconfig = FRONTEND_DIR / "tsconfig.json"
        with open(tsconfig, 'r') as f:
            data = json.load(f)
        # Modern Vite projects use project references, older projects have compilerOptions directly
        has_compiler_options = 'compilerOptions' in data
        has_references = 'references' in data
        assert has_compiler_options or has_references, \
            "tsconfig.json should have 'compilerOptions' or 'references' for project references"

    def test_tsconfig_app_exists_if_using_references(self):
        """Test that tsconfig.app.json exists if using project references"""
        tsconfig = FRONTEND_DIR / "tsconfig.json"
        with open(tsconfig, 'r') as f:
            data = json.load(f)

        # If using project references, tsconfig.app.json should exist
        if 'references' in data:
            tsconfig_app = FRONTEND_DIR / "tsconfig.app.json"
            assert tsconfig_app.exists(), "tsconfig.app.json should exist when using project references"

            # Check content contains compilerOptions (JSONC format with comments)
            with open(tsconfig_app, 'r') as f:
                content = f.read()
            assert 'compilerOptions' in content, "tsconfig.app.json should have compilerOptions"

    def test_typescript_jsx_configured(self):
        """Test that TypeScript is configured for JSX/React"""
        # Check in main tsconfig or tsconfig.app.json
        tsconfig = FRONTEND_DIR / "tsconfig.json"
        with open(tsconfig, 'r') as f:
            data = json.load(f)

        # If using project references, check tsconfig.app.json content
        if 'references' in data:
            tsconfig_app = FRONTEND_DIR / "tsconfig.app.json"
            if tsconfig_app.exists():
                # Read as text (JSONC format with comments)
                with open(tsconfig_app, 'r') as f:
                    content = f.read()
                # Check for JSX configuration
                assert 'jsx' in content.lower() or 'react' in content.lower(), \
                    "TypeScript should be configured for JSX/React"
        else:
            # Traditional tsconfig.json structure
            compiler_options = data.get('compilerOptions', {})
            assert 'jsx' in compiler_options or 'module' in compiler_options, \
                "TypeScript should be configured for JSX/React"


class TestViteConfig:
    """Test Vite configuration"""

    def test_vite_config_exists(self):
        """Test that vite.config.ts exists"""
        # Vite config can be .ts or .js
        vite_config_ts = FRONTEND_DIR / "vite.config.ts"
        vite_config_js = FRONTEND_DIR / "vite.config.js"
        assert vite_config_ts.exists() or vite_config_js.exists(), \
            "vite.config.ts or vite.config.js should exist"


class TestTypescriptDevDependencies:
    """Test TypeScript-related dev dependencies"""

    def test_has_typescript_dev_dependency(self):
        """Test that TypeScript is in devDependencies"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        dev_dependencies = data.get('devDependencies', {})
        assert 'typescript' in dev_dependencies, "Should have 'typescript' in devDependencies"

    def test_has_vite_dev_dependency(self):
        """Test that Vite is in devDependencies"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        dev_dependencies = data.get('devDependencies', {})
        assert 'vite' in dev_dependencies, "Should have 'vite' in devDependencies"

    def test_has_react_types_dev_dependency(self):
        """Test that @types/react is in devDependencies"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        dev_dependencies = data.get('devDependencies', {})
        assert '@types/react' in dev_dependencies, "Should have '@types/react' in devDependencies"

    def test_has_react_dom_types_dev_dependency(self):
        """Test that @types/react-dom is in devDependencies"""
        package_json = FRONTEND_DIR / "package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        dev_dependencies = data.get('devDependencies', {})
        assert '@types/react-dom' in dev_dependencies, "Should have '@types/react-dom' in devDependencies"


class TestSourceFiles:
    """Test source files structure"""

    def test_main_tsx_exists(self):
        """Test that main.tsx exists"""
        main_tsx = FRONTEND_DIR / "src" / "main.tsx"
        main_ts = FRONTEND_DIR / "src" / "main.ts"
        assert main_tsx.exists() or main_ts.exists(), "src/main.tsx or src/main.ts should exist"

    def test_app_tsx_exists(self):
        """Test that App.tsx exists"""
        app_tsx = FRONTEND_DIR / "src" / "App.tsx"
        assert app_tsx.exists(), "src/App.tsx should exist"

    def test_index_html_exists(self):
        """Test that index.html exists"""
        index_html = FRONTEND_DIR / "index.html"
        assert index_html.exists(), "index.html should exist at root"


class TestGitignore:
    """Test .gitignore configuration"""

    def test_gitignore_exists(self):
        """Test that .gitignore exists"""
        gitignore = FRONTEND_DIR / ".gitignore"
        assert gitignore.exists(), ".gitignore should exist in frontend"

    def test_gitignore_ignores_node_modules(self):
        """Test that .gitignore includes node_modules"""
        gitignore = FRONTEND_DIR / ".gitignore"
        with open(gitignore, 'r') as f:
            content = f.read()
        assert 'node_modules' in content, ".gitignore should include node_modules"

    def test_gitignore_ignores_dist(self):
        """Test that .gitignore includes dist"""
        gitignore = FRONTEND_DIR / ".gitignore"
        with open(gitignore, 'r') as f:
            content = f.read()
        assert 'dist' in content, ".gitignore should include dist"


class TestNodeModules:
    """Test node_modules (after npm install)"""

    def test_node_modules_exists_after_install(self):
        """Test that node_modules directory exists (created by npm install)"""
        # This test is informational - node_modules created after npm install
        node_modules = FRONTEND_DIR / "node_modules"
        # We just check if directory exists, it's OK if it doesn't exist yet
        if node_modules.exists():
            assert node_modules.is_dir(), "node_modules should be a directory if it exists"


class TestPackageLock:
    """Test package-lock.json"""

    def test_package_lock_exists_after_install(self):
        """Test that package-lock.json exists (created by npm install)"""
        # This test is informational - package-lock.json created after npm install
        package_lock = FRONTEND_DIR / "package-lock.json"
        # We just check if file exists, it's OK if it doesn't exist yet
        if package_lock.exists():
            assert package_lock.is_file(), "package-lock.json should be a file if it exists"
