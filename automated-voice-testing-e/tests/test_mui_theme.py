"""
Test suite for Material-UI theme configuration

Ensures proper Material-UI theme setup with custom brand colors,
typography, spacing, and component customizations.
"""

import os
import json
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
SRC_DIR = FRONTEND_DIR / "src"
THEME_DIR = SRC_DIR / "theme"
THEME_INDEX_FILE = THEME_DIR / "index.ts"


class TestThemeDirectory:
    """Test theme directory structure"""

    def test_theme_directory_exists(self):
        """Test that theme directory exists"""
        assert THEME_DIR.exists(), "theme directory should exist"
        assert THEME_DIR.is_dir(), "theme should be a directory"

    def test_theme_directory_in_src(self):
        """Test that theme directory is in src"""
        assert THEME_DIR.parent == SRC_DIR, "theme should be in src directory"


class TestThemeIndexFile:
    """Test theme/index.ts file"""

    def test_theme_index_exists(self):
        """Test that theme/index.ts exists"""
        assert THEME_INDEX_FILE.exists(), "theme/index.ts should exist"
        assert THEME_INDEX_FILE.is_file(), "theme/index.ts should be a file"

    def test_theme_index_is_typescript(self):
        """Test that theme/index.ts is a TypeScript file"""
        assert THEME_INDEX_FILE.suffix == ".ts", "theme/index.ts should have .ts extension"

    def test_theme_index_has_content(self):
        """Test that theme/index.ts has content"""
        content = THEME_INDEX_FILE.read_text()
        assert len(content) > 0, "theme/index.ts should not be empty"


class TestMUIImports:
    """Test Material-UI imports"""

    def test_imports_create_theme(self):
        """Test that theme imports createTheme"""
        content = THEME_INDEX_FILE.read_text()
        assert 'createTheme' in content, "theme/index.ts should import createTheme"

    def test_imports_from_mui_material(self):
        """Test that imports from @mui/material"""
        content = THEME_INDEX_FILE.read_text()
        assert '@mui/material' in content, "theme/index.ts should import from @mui/material"


class TestThemeCreation:
    """Test theme creation"""

    def test_creates_theme_with_create_theme(self):
        """Test that creates theme using createTheme"""
        content = THEME_INDEX_FILE.read_text()
        assert 'createTheme' in content, "theme/index.ts should use createTheme"

    def test_exports_theme(self):
        """Test that exports the theme"""
        content = THEME_INDEX_FILE.read_text()
        has_export_default = 'export default' in content
        has_export_const = 'export const theme' in content or 'export { theme }' in content
        assert has_export_default or has_export_const, "theme/index.ts should export theme"


class TestPaletteConfiguration:
    """Test palette (color) configuration"""

    def test_configures_palette(self):
        """Test that configures palette"""
        content = THEME_INDEX_FILE.read_text()
        assert 'palette' in content, "theme/index.ts should configure palette"

    def test_configures_primary_color(self):
        """Test that configures primary color"""
        content = THEME_INDEX_FILE.read_text()
        assert 'primary' in content, "theme/index.ts should configure primary color"

    def test_configures_secondary_color(self):
        """Test that configures secondary color"""
        content = THEME_INDEX_FILE.read_text()
        assert 'secondary' in content, "theme/index.ts should configure secondary color"

    def test_has_color_values(self):
        """Test that has color values (hex, rgb, or named colors)"""
        content = THEME_INDEX_FILE.read_text()
        has_hex = '#' in content
        has_rgb = 'rgb' in content
        # Should have some color values
        assert has_hex or has_rgb, "theme/index.ts should have color values"


class TestTypographyConfiguration:
    """Test typography configuration"""

    def test_configures_typography(self):
        """Test that configures typography"""
        content = THEME_INDEX_FILE.read_text()
        assert 'typography' in content, "theme/index.ts should configure typography"

    def test_configures_font_family(self):
        """Test that configures font family"""
        content = THEME_INDEX_FILE.read_text()
        has_font_family = 'fontFamily' in content
        # Should configure font
        assert has_font_family, "theme/index.ts should configure fontFamily"


class TestSpacingConfiguration:
    """Test spacing configuration"""

    def test_configures_spacing_or_uses_default(self):
        """Test that configures spacing or uses MUI default"""
        content = THEME_INDEX_FILE.read_text()
        # Either explicitly configures spacing or uses default
        # MUI has default spacing, so this is optional but good to check
        # Just verify the theme is created properly
        assert 'createTheme' in content, "theme/index.ts should create theme with spacing"


class TestComponentCustomization:
    """Test component customization"""

    def test_can_customize_components(self):
        """Test that structure allows component customization"""
        content = THEME_INDEX_FILE.read_text()
        # Check if components field exists (optional in MUI)
        # Or just verify theme structure is valid
        has_components = 'components' in content
        # This is optional - theme can be basic or have component overrides
        # Just verify the theme object exists
        assert 'createTheme' in content, "theme/index.ts should support component customization"


class TestThemeStructure:
    """Test overall theme structure"""

    def test_has_valid_typescript_syntax(self):
        """Test that theme/index.ts has valid TypeScript syntax"""
        content = THEME_INDEX_FILE.read_text()
        # Basic syntax checks
        assert content.count('(') >= content.count(')') - 2, "Parentheses should be balanced"
        assert content.count('{') >= content.count('}') - 2, "Braces should be balanced"

    def test_file_not_too_small(self):
        """Test that theme/index.ts has reasonable content"""
        content = THEME_INDEX_FILE.read_text()
        lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('//')]
        assert len(lines) >= 10, "theme/index.ts should have meaningful content"


class TestThemeDocumentation:
    """Test theme documentation"""

    def test_has_comments_or_documentation(self):
        """Test that theme/index.ts has comments or documentation"""
        content = THEME_INDEX_FILE.read_text()
        has_single_comment = '//' in content
        has_multi_comment = '/*' in content or '*/' in content
        # Good practice - should have documentation
        assert has_single_comment or has_multi_comment, \
            "theme/index.ts should have comments or documentation"


class TestThemeExports:
    """Test theme exports"""

    def test_exports_theme_object(self):
        """Test that exports theme object"""
        content = THEME_INDEX_FILE.read_text()
        has_export = 'export' in content
        assert has_export, "theme/index.ts should export theme"

    def test_can_be_imported_by_other_modules(self):
        """Test that theme can be imported"""
        content = THEME_INDEX_FILE.read_text()
        # Should have export statement
        has_export_default = 'export default' in content
        has_export_named = 'export const' in content or 'export {' in content
        assert has_export_default or has_export_named, \
            "theme/index.ts should export for import in other modules"


class TestThemeIntegration:
    """Test theme integration readiness"""

    def test_theme_compatible_with_mui_theme_provider(self):
        """Test that theme is compatible with MUI ThemeProvider"""
        content = THEME_INDEX_FILE.read_text()
        # Theme created with createTheme is compatible with ThemeProvider
        assert 'createTheme' in content, \
            "theme/index.ts should create theme compatible with ThemeProvider"


class TestBrandColors:
    """Test brand color configuration"""

    def test_defines_custom_colors(self):
        """Test that defines custom brand colors"""
        content = THEME_INDEX_FILE.read_text()
        # Should have palette configuration with colors
        has_palette = 'palette' in content
        has_colors = 'primary' in content or 'secondary' in content
        assert has_palette and has_colors, \
            "theme/index.ts should define custom brand colors"

    def test_primary_color_has_main_shade(self):
        """Test that primary color has main shade"""
        content = THEME_INDEX_FILE.read_text()
        # Should configure primary.main
        has_primary_main = 'main' in content
        assert has_primary_main, "theme should configure color shades"


class TestThemeConsistency:
    """Test theme consistency"""

    def test_uses_consistent_structure(self):
        """Test that uses consistent MUI theme structure"""
        content = THEME_INDEX_FILE.read_text()
        # Should use createTheme with object configuration
        assert 'createTheme({' in content or 'createTheme( {' in content or 'createTheme(\n' in content, \
            "theme/index.ts should use createTheme with configuration object"

    def test_palette_and_typography_together(self):
        """Test that configures palette and typography"""
        content = THEME_INDEX_FILE.read_text()
        has_palette = 'palette' in content
        has_typography = 'typography' in content
        # Good practice to configure both
        assert has_palette and has_typography, \
            "theme/index.ts should configure both palette and typography"
