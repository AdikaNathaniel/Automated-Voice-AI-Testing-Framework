"""Audio profile processing utilities for simulated acoustic conditions."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class AudioProfileProcessingResult:
    """Container for processed audio bytes and effect metadata."""

    audio_bytes: bytes
    metadata: Dict[str, Any]


class AudioProfileProcessor:
    """Apply lightweight, deterministic audio profile effects."""

    def apply_profile(
        self,
        audio_bytes: bytes,
        profile_name: str,
        profile_config: Dict[str, Any]
    ) -> AudioProfileProcessingResult:
        snr = profile_config.get("snr_db")
        noise = profile_config.get("background_noise") or "silence"
        effect_id = hashlib.sha256(
            (profile_name + str(snr) + noise).encode("utf-8")
        ).hexdigest()[:16]

        processed_audio = self._inject_noise(audio_bytes, profile_name, snr, noise)

        metadata = {
            "profile_name": profile_name,
            "snr_db": snr,
            "noise_type": noise,
            "effect_id": effect_id,
            "bytes_modified": int(processed_audio != audio_bytes),
        }

        return AudioProfileProcessingResult(audio_bytes=processed_audio, metadata=metadata)

    def _inject_noise(
        self,
        audio_bytes: bytes,
        profile_name: str,
        snr_db: Any,
        noise_type: str,
    ) -> bytes:
        if profile_name == "clean" or (snr_db is not None and snr_db >= 24):
            return audio_bytes

        seed_material = f"{profile_name}:{noise_type}:{snr_db or ''}"
        seed = int(hashlib.sha256(seed_material.encode("utf-8")).hexdigest()[:8], 16)
        rng = random.Random(seed)

        noise_strength = self._noise_strength(snr_db)
        mutated = bytearray(audio_bytes)
        for idx, value in enumerate(mutated):
            noise_value = rng.randint(0, noise_strength)
            mutated[idx] = value ^ (noise_value & 0xFF)
        return bytes(mutated)

    def _noise_strength(self, snr_db: Any) -> int:
        try:
            snr = float(snr_db)
        except (TypeError, ValueError):
            snr = 20.0

        if snr >= 24:
            return 0
        if snr >= 20:
            return 4
        return 12
