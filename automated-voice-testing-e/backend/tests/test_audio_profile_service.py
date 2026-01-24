"""Tests for audio profile processing utilities."""

from services.audio_profile_service import AudioProfileProcessor


def test_clean_profile_returns_original_bytes():
    processor = AudioProfileProcessor()
    original_audio = b"\x00\x01\x02test-bytes"
    profile = {"snr_db": 25, "background_noise": None}

    result = processor.apply_profile(original_audio, "clean", profile)

    assert result.audio_bytes == original_audio
    assert result.metadata["profile_name"] == "clean"
    assert result.metadata["noise_type"] == "silence"
    assert result.metadata["snr_db"] == 25


def test_high_noise_profile_modifies_audio_and_records_metadata():
    processor = AudioProfileProcessor()
    original_audio = b"0123456789abcdef"
    profile = {"snr_db": 15, "background_noise": "highway_traffic"}

    result = processor.apply_profile(original_audio, "high_noise", profile)

    assert result.audio_bytes != original_audio
    assert len(result.audio_bytes) == len(original_audio)
    assert result.metadata["profile_name"] == "high_noise"
    assert result.metadata["noise_type"] == "highway_traffic"
    assert result.metadata["snr_db"] == 15
    assert "effect_id" in result.metadata
