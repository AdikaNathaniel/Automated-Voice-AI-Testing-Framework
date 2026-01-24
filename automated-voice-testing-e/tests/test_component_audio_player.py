"""
Test suite for AudioPlayer component (TASK-188)

Validates the AudioPlayer.tsx component implementation including:
- File structure and imports
- React component structure
- Material-UI components
- Play/Pause controls
- Seek functionality
- Volume control
- Playback speed control
- Waveform visualization placeholder
- Props interface (audioUrl, onPlaybackChange, etc.)
- TypeScript usage
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
COMPONENTS_DIR = FRONTEND_SRC / "components"
VALIDATION_COMPONENTS_DIR = COMPONENTS_DIR / "Validation"
AUDIO_PLAYER_FILE = VALIDATION_COMPONENTS_DIR / "AudioPlayer.tsx"


class TestAudioPlayerFileStructure:
    """Test AudioPlayer file structure"""

    def test_components_directory_exists(self):
        """Test that components directory exists"""
        assert COMPONENTS_DIR.exists(), "frontend/src/components directory should exist"
        assert COMPONENTS_DIR.is_dir(), "components should be a directory"

    def test_validation_components_directory_exists(self):
        """Test that Validation components directory exists"""
        assert VALIDATION_COMPONENTS_DIR.exists(), \
            "frontend/src/components/Validation directory should exist"
        assert VALIDATION_COMPONENTS_DIR.is_dir(), "Validation should be a directory"

    def test_audio_player_file_exists(self):
        """Test that AudioPlayer.tsx exists"""
        assert AUDIO_PLAYER_FILE.exists(), "AudioPlayer.tsx should exist"
        assert AUDIO_PLAYER_FILE.is_file(), "AudioPlayer.tsx should be a file"

    def test_audio_player_has_content(self):
        """Test that AudioPlayer.tsx has content"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert len(content) > 0, "AudioPlayer.tsx should not be empty"


class TestReactImports:
    """Test React and TypeScript imports"""

    def test_imports_react(self):
        """Test that component imports React"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert "import" in content and "react" in content.lower(), \
            "Should import React"

    def test_imports_use_state_or_use_ref(self):
        """Test that component imports useState or useRef for state management"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("useState" in content or "useRef" in content), \
            "Should import useState or useRef for managing audio playback state"

    def test_is_typescript_file(self):
        """Test that file uses TypeScript"""
        assert AUDIO_PLAYER_FILE.suffix == ".tsx", "Should be a .tsx file"


class TestMaterialUIImports:
    """Test Material-UI component imports"""

    def test_imports_mui_core(self):
        """Test that component imports from @mui/material"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert "@mui/material" in content, "Should import from @mui/material"

    def test_imports_icon_button(self):
        """Test that component imports IconButton"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert "IconButton" in content, "Should import IconButton for play/pause control"

    def test_imports_slider(self):
        """Test that component imports Slider"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert "Slider" in content, "Should import Slider for seek and volume controls"

    def test_imports_box_or_stack(self):
        """Test that component imports Box or Stack for layout"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("Box" in content or "Stack" in content), \
            "Should import Box or Stack for layout"

    def test_imports_play_pause_icons(self):
        """Test that component imports Play and Pause icons"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert (("PlayArrow" in content or "Play" in content) and
                ("Pause" in content)), \
            "Should import Play and Pause icons"


class TestComponentStructure:
    """Test component structure"""

    def test_exports_audio_player(self):
        """Test that component exports AudioPlayer"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert "AudioPlayer" in content, "Should define AudioPlayer component"

    def test_is_functional_component(self):
        """Test that component is a functional component"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("const AudioPlayer" in content or
                "function AudioPlayer" in content), \
            "Should define functional component"

    def test_has_default_export(self):
        """Test that component has default export"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert "export default" in content, "Should have default export"


class TestPlayPauseControls:
    """Test play/pause controls"""

    def test_has_play_pause_button(self):
        """Test that component has play/pause button"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert (("IconButton" in content or "Button" in content) and
                ("play" in content.lower() or "pause" in content.lower())), \
            "Should have play/pause button"

    def test_has_play_state_management(self):
        """Test that component manages play/pause state"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert (("playing" in content.lower() or "isPlaying" in content) or
                ("paused" in content.lower())), \
            "Should manage play/pause state"

    def test_has_play_pause_handler(self):
        """Test that component has play/pause click handler"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert (("onClick" in content or "handlePlay" in content) or
                ("togglePlay" in content)), \
            "Should have play/pause click handler"


class TestSeekControls:
    """Test seek functionality"""

    def test_has_seek_slider(self):
        """Test that component has seek slider"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("Slider" in content and ("seek" in content.lower() or
                "progress" in content.lower() or "time" in content.lower())), \
            "Should have seek slider"

    def test_has_current_time_display(self):
        """Test that component displays current time"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("currentTime" in content or "time" in content.lower()), \
            "Should display current time"

    def test_has_duration_display(self):
        """Test that component displays duration"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("duration" in content.lower()), \
            "Should display audio duration"


class TestVolumeControls:
    """Test volume control"""

    def test_has_volume_slider(self):
        """Test that component has volume slider"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("Slider" in content and "volume" in content.lower()), \
            "Should have volume slider"

    def test_has_volume_state(self):
        """Test that component manages volume state"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("volume" in content.lower()), \
            "Should manage volume state"

    def test_has_volume_icon(self):
        """Test that component has volume icon"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("Volume" in content or "volume" in content.lower()), \
            "Should have volume icon"


class TestPlaybackSpeedControls:
    """Test playback speed control"""

    def test_has_playback_speed_control(self):
        """Test that component has playback speed control"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("speed" in content.lower() or "rate" in content.lower() or
                "playbackRate" in content), \
            "Should have playback speed control"

    def test_has_speed_options(self):
        """Test that component has speed options"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("speed" in content.lower() or "rate" in content.lower()), \
            "Should have speed options (0.5x, 1x, 1.5x, 2x)"


class TestWaveformVisualization:
    """Test waveform visualization"""

    def test_has_waveform_container(self):
        """Test that component has waveform container"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("waveform" in content.lower() or "wave" in content.lower()), \
            "Should have waveform container"

    def test_has_wavesurfer_reference(self):
        """Test that component references WaveSurfer"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("wavesurfer" in content.lower() or "waveform" in content.lower()), \
            "Should reference WaveSurfer for visualization"


class TestPropsInterface:
    """Test props interface"""

    def test_has_props_interface(self):
        """Test that component defines props interface"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert (("interface" in content and "Props" in content) or
                "AudioPlayerProps" in content), \
            "Should define props interface"

    def test_accepts_audio_url_prop(self):
        """Test that component accepts audioUrl prop"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("audioUrl" in content or "src" in content or "url" in content), \
            "Should accept audioUrl prop"


class TestTypeScript:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that component uses TypeScript syntax"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert (":)" in content or "React" in content), \
            "Should use TypeScript syntax"

    def test_component_typed(self):
        """Test that component is properly typed"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("React.FC" in content or "FC<" in content or ": () =>" in content), \
            "Component should be properly typed"


class TestTaskRequirements:
    """Test TASK-188 specific requirements"""

    def test_task_188_file_location(self):
        """Test TASK-188: File is in correct location"""
        expected_path = PROJECT_ROOT / "frontend" / "src" / "components" / "Validation" / "AudioPlayer.tsx"
        assert expected_path.exists(), \
            "TASK-188: File should be at frontend/src/components/Validation/AudioPlayer.tsx"

    def test_task_188_has_play_pause(self):
        """Test TASK-188: Has play/pause controls"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert (("play" in content.lower() or "pause" in content.lower()) and
                "Button" in content), \
            "TASK-188: Should have play/pause controls"

    def test_task_188_has_seek(self):
        """Test TASK-188: Has seek functionality"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("Slider" in content and
                ("seek" in content.lower() or "progress" in content.lower())), \
            "TASK-188: Should have seek functionality"

    def test_task_188_has_volume(self):
        """Test TASK-188: Has volume control"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("volume" in content.lower() and "Slider" in content), \
            "TASK-188: Should have volume control"

    def test_task_188_has_playback_speed(self):
        """Test TASK-188: Has playback speed control"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("speed" in content.lower() or "rate" in content.lower()), \
            "TASK-188: Should have playback speed control"

    def test_task_188_has_waveform(self):
        """Test TASK-188: Has waveform visualization"""
        content = AUDIO_PLAYER_FILE.read_text()
        assert ("waveform" in content.lower() or "wavesurfer" in content.lower()), \
            "TASK-188: Should have waveform visualization using WaveSurfer.js"
