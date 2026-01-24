"""
Audio Utilities (TASK-111)

This module provides utility functions for audio processing in the Voice AI Testing Framework.
These utilities support audio format conversion, noise injection, validation, and analysis.

Functions:
- convert_to_pcm: Convert audio to PCM format at specified sample rate
- add_noise: Add Gaussian noise to audio at specified SNR
- validate_audio_format: Check if audio data is in a valid format
- get_audio_duration: Get the duration of audio in seconds

Required libraries:
- soundfile: For reading/writing audio files
- numpy: For audio data manipulation
- io: For BytesIO operations

Example:
    >>> audio_bytes = load_audio_file("test.wav")
    >>> pcm_audio = convert_to_pcm(audio_bytes, target_rate=16000)
    >>> duration = get_audio_duration(pcm_audio)
    >>> print(f"Audio duration: {duration} seconds")
"""

import io
import numpy as np
import soundfile as sf
import logging

logger = logging.getLogger(__name__)


class AudioUtils:
    """
    Service class for audio utility operations.

    Provides audio format conversion, noise injection, validation, and analysis.

    Example:
        >>> utils = AudioUtils()
        >>> pcm_audio = utils.convert_to_pcm(audio_bytes)
    """

    def __init__(self):
        """Initialize the audio utilities service."""
        pass

    def convert_to_pcm(self, audio_bytes: bytes, target_rate: int = 16000) -> bytes:
        """Convert audio to PCM format at specified sample rate."""
        return convert_to_pcm(audio_bytes, target_rate)

    def add_noise(self, audio_bytes: bytes, snr_db: float) -> bytes:
        """Add Gaussian noise to audio at specified SNR."""
        return add_noise(audio_bytes, snr_db)

    def validate_audio_format(self, audio_bytes: bytes) -> bool:
        """Check if audio data is in a valid format."""
        return validate_audio_format(audio_bytes)

    def get_audio_duration(self, audio_bytes: bytes) -> float:
        """Get the duration of audio in seconds."""
        return get_audio_duration(audio_bytes)


def convert_to_pcm(audio_bytes: bytes, target_rate: int = 16000, raw: bool = False) -> bytes:
    """
    Convert audio to PCM format at specified sample rate.

    This function takes audio data in any format (including MP3, WAV, FLAC, OGG)
    and converts it to PCM format at the target sample rate. Uses pydub for MP3
    support since soundfile doesn't natively support MP3.

    Args:
        audio_bytes: Raw audio data in bytes (any supported format)
        target_rate: Target sample rate in Hz (default: 16000)
                    Common rates: 8000, 16000, 22050, 44100, 48000
        raw: If True, return raw PCM samples (16-bit little-endian, no headers).
             If False, return WAV format with headers. Default: False.
             Use raw=True for streaming APIs like Houndify that expect raw samples.

    Returns:
        bytes: Audio data in PCM format at target sample rate
               - If raw=False: WAV format with headers
               - If raw=True: Raw 16-bit little-endian PCM samples (no headers)

    Raises:
        ValueError: If audio_bytes is empty or invalid
        RuntimeError: If audio conversion fails

    Example:
        >>> with open("audio.mp3", "rb") as f:
        ...     audio_data = f.read()
        >>> pcm_audio = convert_to_pcm(audio_data, target_rate=16000)
        >>> # pcm_audio is now 16kHz PCM WAV format
        >>>
        >>> # For Houndify streaming (raw PCM samples):
        >>> raw_pcm = convert_to_pcm(audio_data, target_rate=16000, raw=True)
    """
    if not audio_bytes:
        raise ValueError("audio_bytes cannot be empty")

    # First, try to detect if it's MP3 (starts with ID3 tag or 0xFF 0xFB sync word)
    is_mp3 = (
        audio_bytes[:3] == b'ID3' or  # ID3 tag
        (len(audio_bytes) > 1 and audio_bytes[0] == 0xFF and (audio_bytes[1] & 0xE0) == 0xE0)  # MPEG sync
    )

    if is_mp3:
        # Use pydub for MP3 conversion
        try:
            from pydub import AudioSegment

            logger.debug("Detected MP3 format, using pydub for conversion")

            # Load MP3 from bytes
            audio_buffer = io.BytesIO(audio_bytes)
            audio = AudioSegment.from_mp3(audio_buffer)

            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)

            # Resample to target rate
            audio = audio.set_frame_rate(target_rate)

            # Set sample width to 16-bit
            audio = audio.set_sample_width(2)

            if raw:
                # Return raw PCM samples (no headers)
                result = audio.raw_data
                logger.debug(f"Converted MP3 to raw PCM: {len(result)} bytes at {target_rate}Hz")
            else:
                # Export as WAV with headers
                output_buffer = io.BytesIO()
                audio.export(output_buffer, format='wav')
                output_buffer.seek(0)
                result = output_buffer.read()
                logger.debug(f"Converted MP3 to PCM WAV: {len(result)} bytes at {target_rate}Hz")

            return result

        except ImportError:
            logger.warning("pydub not available, falling back to soundfile")
        except Exception as e:
            logger.warning(f"pydub conversion failed: {e}, falling back to soundfile")

    # Use soundfile for non-MP3 formats (WAV, FLAC, OGG, etc.)
    try:
        # Read audio from bytes
        audio_buffer = io.BytesIO(audio_bytes)
        audio_data, original_rate = sf.read(audio_buffer, dtype='float32')

        logger.debug(f"Read audio: {len(audio_data)} samples at {original_rate}Hz")

        # Resample if necessary
        if original_rate != target_rate:
            # Calculate resampling ratio
            ratio = target_rate / original_rate
            new_length = int(len(audio_data) * ratio)

            # Simple linear interpolation resampling
            # For production, consider using scipy.signal.resample or librosa
            old_indices = np.linspace(0, len(audio_data) - 1, len(audio_data))
            new_indices = np.linspace(0, len(audio_data) - 1, new_length)
            audio_data = np.interp(new_indices, old_indices, audio_data)

            logger.debug(f"Resampled from {original_rate}Hz to {target_rate}Hz")

        # Ensure audio is in the correct range [-1, 1]
        audio_data = np.clip(audio_data, -1.0, 1.0)

        if raw:
            # Convert to 16-bit integers and return raw bytes
            pcm_samples = (audio_data * 32767).astype(np.int16)
            result = pcm_samples.tobytes()
            logger.debug(f"Converted to raw PCM: {len(result)} bytes")
        else:
            # Write to WAV format in memory
            output_buffer = io.BytesIO()
            sf.write(output_buffer, audio_data, target_rate, format='WAV', subtype='PCM_16')
            output_buffer.seek(0)
            result = output_buffer.read()
            logger.debug(f"Converted to PCM WAV: {len(result)} bytes")

        return result

    except Exception as e:
        logger.error(f"Error converting audio to PCM: {e}")
        raise RuntimeError(f"Failed to convert audio to PCM: {str(e)}") from e


def add_noise(audio_bytes: bytes, snr_db: float) -> bytes:
    """
    Add Gaussian white noise to audio at specified Signal-to-Noise Ratio.

    This function adds random noise to audio data to simulate real-world
    conditions and test voice AI robustness. The SNR (Signal-to-Noise Ratio)
    controls how much noise is added - higher SNR means less noise.

    Args:
        audio_bytes: Raw audio data in bytes (WAV, FLAC, etc.)
        snr_db: Signal-to-Noise Ratio in decibels
               Higher values = less noise (cleaner audio)
               Typical values:
               - 30+ dB: Very clean audio
               - 20-30 dB: Clean audio with minimal noise
               - 10-20 dB: Moderate noise
               - 0-10 dB: Heavy noise
               - <0 dB: Noise dominates signal

    Returns:
        bytes: Audio data with added noise in WAV format

    Raises:
        ValueError: If audio_bytes is empty or invalid
        RuntimeError: If noise addition fails

    Example:
        >>> audio = load_audio("clean_voice.wav")
        >>> noisy_audio = add_noise(audio, snr_db=15.0)
        >>> # noisy_audio now has moderate background noise
    """
    if not audio_bytes:
        raise ValueError("audio_bytes cannot be empty")

    try:
        # Read audio from bytes
        audio_buffer = io.BytesIO(audio_bytes)
        audio_data, sample_rate = sf.read(audio_buffer, dtype='float32')

        logger.debug(f"Adding noise to audio: SNR={snr_db}dB, {len(audio_data)} samples")

        # Calculate signal power
        signal_power = np.mean(audio_data ** 2)

        # Calculate noise power based on desired SNR
        # SNR_dB = 10 * log10(signal_power / noise_power)
        # noise_power = signal_power / (10 ** (SNR_dB / 10))
        snr_linear = 10 ** (snr_db / 10)
        noise_power = signal_power / snr_linear

        # Generate Gaussian white noise
        noise = np.random.normal(0, np.sqrt(noise_power), len(audio_data))

        # Add noise to signal
        noisy_audio = audio_data + noise

        # Ensure audio is in the correct range [-1, 1]
        # Clip to prevent overflow
        noisy_audio = np.clip(noisy_audio, -1.0, 1.0)

        # Write to WAV format in memory
        output_buffer = io.BytesIO()
        sf.write(output_buffer, noisy_audio.astype(np.float32), sample_rate,
                format='WAV', subtype='PCM_16')

        # Get the bytes
        output_buffer.seek(0)
        result = output_buffer.read()

        logger.debug(f"Added noise: {len(result)} bytes output")
        return result

    except Exception as e:
        logger.error(f"Error adding noise to audio: {e}")
        raise RuntimeError(f"Failed to add noise to audio: {str(e)}") from e


def validate_audio_format(audio_bytes: bytes) -> bool:
    """
    Validate that audio data is in a supported format and can be read.

    This function attempts to read audio data using soundfile to determine
    if it's in a valid, supported audio format. It doesn't validate the
    content quality, only that the format can be parsed.

    Supported formats include:
    - WAV (all subtypes)
    - FLAC
    - OGG/Vorbis
    - And other formats supported by libsndfile

    Args:
        audio_bytes: Raw audio data in bytes to validate

    Returns:
        bool: True if audio format is valid and readable, False otherwise

    Example:
        >>> valid_audio = load_file("speech.wav")
        >>> is_valid = validate_audio_format(valid_audio)
        >>> print(is_valid)  # True
        >>>
        >>> invalid_data = b"This is not audio"
        >>> is_valid = validate_audio_format(invalid_data)
        >>> print(is_valid)  # False
    """
    if not audio_bytes:
        logger.debug("Validation failed: empty audio_bytes")
        return False

    try:
        # Try to read audio using soundfile
        audio_buffer = io.BytesIO(audio_bytes)
        audio_data, sample_rate = sf.read(audio_buffer)

        # Basic sanity checks
        if len(audio_data) == 0:
            logger.debug("Validation failed: no audio data")
            return False

        if sample_rate <= 0:
            logger.debug(f"Validation failed: invalid sample rate {sample_rate}")
            return False

        logger.debug(f"Validation passed: {len(audio_data)} samples at {sample_rate}Hz")
        return True

    except Exception as e:
        # Any exception means the format is invalid or unsupported
        logger.debug(f"Validation failed: {type(e).__name__}: {e}")
        return False


def get_audio_duration(audio_bytes: bytes) -> float:
    """
    Get the duration of audio in seconds.

    This function reads audio data and calculates its duration based on
    the number of samples and sample rate. This is useful for validating
    test audio meets minimum/maximum duration requirements.

    Args:
        audio_bytes: Raw audio data in bytes (WAV, FLAC, etc.)

    Returns:
        float: Duration of audio in seconds (e.g., 1.5 for 1.5 seconds)

    Raises:
        ValueError: If audio_bytes is empty or invalid
        RuntimeError: If duration calculation fails

    Example:
        >>> audio = load_audio("test.wav")
        >>> duration = get_audio_duration(audio)
        >>> print(f"Duration: {duration:.2f} seconds")
        Duration: 2.34 seconds
        >>>
        >>> if duration < 1.0:
        ...     print("Audio too short for testing")
    """
    if not audio_bytes:
        raise ValueError("audio_bytes cannot be empty")

    try:
        # Read audio from bytes
        audio_buffer = io.BytesIO(audio_bytes)
        audio_data, sample_rate = sf.read(audio_buffer)

        # Calculate duration: number_of_samples / sample_rate
        duration = len(audio_data) / sample_rate

        logger.debug(f"Audio duration: {duration:.3f} seconds ({len(audio_data)} samples at {sample_rate}Hz)")

        return float(duration)

    except Exception as e:
        logger.error(f"Error calculating audio duration: {e}")
        raise RuntimeError(f"Failed to get audio duration: {str(e)}") from e


def audio_bytes_to_numpy(audio_bytes: bytes, target_rate: int = 16000) -> np.ndarray:
    """
    Convert audio bytes to numpy array for processing.

    This function reads audio data from bytes and returns it as a numpy array
    suitable for signal processing operations like noise injection.

    Args:
        audio_bytes: Raw audio data in bytes (WAV, FLAC, MP3, etc.)
        target_rate: Target sample rate in Hz (default: 16000)

    Returns:
        np.ndarray: Audio data as float32 numpy array normalized to [-1, 1]

    Raises:
        ValueError: If audio_bytes is empty or invalid
        RuntimeError: If conversion fails

    Example:
        >>> audio = load_audio("test.wav")
        >>> audio_numpy = audio_bytes_to_numpy(audio)
        >>> print(f"Shape: {audio_numpy.shape}")
    """
    if not audio_bytes:
        raise ValueError("audio_bytes cannot be empty")

    try:
        # Check if MP3
        is_mp3 = (
            audio_bytes[:3] == b'ID3' or
            (len(audio_bytes) > 1 and audio_bytes[0] == 0xFF and (audio_bytes[1] & 0xE0) == 0xE0)
        )

        if is_mp3:
            try:
                from pydub import AudioSegment

                audio_buffer = io.BytesIO(audio_bytes)
                audio = AudioSegment.from_mp3(audio_buffer)

                # Convert to mono if stereo
                if audio.channels > 1:
                    audio = audio.set_channels(1)

                # Resample to target rate
                audio = audio.set_frame_rate(target_rate)

                # Get raw samples and convert to numpy
                samples = np.frombuffer(audio.raw_data, dtype=np.int16)
                audio_data = samples.astype(np.float32) / 32768.0

                logger.debug(f"Converted MP3 to numpy: {len(audio_data)} samples")
                return audio_data

            except ImportError:
                logger.warning("pydub not available, falling back to soundfile")
            except Exception as e:
                logger.warning(f"pydub conversion failed: {e}, falling back to soundfile")

        # Use soundfile for non-MP3 formats
        audio_buffer = io.BytesIO(audio_bytes)
        audio_data, original_rate = sf.read(audio_buffer, dtype='float32')

        # Resample if necessary
        if original_rate != target_rate:
            ratio = target_rate / original_rate
            new_length = int(len(audio_data) * ratio)
            old_indices = np.linspace(0, len(audio_data) - 1, len(audio_data))
            new_indices = np.linspace(0, len(audio_data) - 1, new_length)
            audio_data = np.interp(new_indices, old_indices, audio_data)

        logger.debug(f"Converted to numpy: {len(audio_data)} samples at {target_rate}Hz")
        return audio_data.astype(np.float32)

    except Exception as e:
        logger.error(f"Error converting audio to numpy: {e}")
        raise RuntimeError(f"Failed to convert audio to numpy: {str(e)}") from e


def numpy_to_audio_bytes(
    audio_data: np.ndarray,
    output_format: str = "wav",
    sample_rate: int = 16000
) -> bytes:
    """
    Convert numpy audio array back to audio bytes.

    This function takes processed audio data as a numpy array and converts
    it back to audio bytes in the specified format.

    Args:
        audio_data: Audio data as numpy array (float32, normalized to [-1, 1])
        output_format: Output format ('wav', 'mp3', 'flac', 'ogg'). Default: 'wav'
        sample_rate: Sample rate in Hz (default: 16000)

    Returns:
        bytes: Audio data in the specified format

    Raises:
        ValueError: If audio_data is empty or invalid
        RuntimeError: If conversion fails

    Example:
        >>> audio_numpy = process_audio(audio_numpy)
        >>> audio_bytes = numpy_to_audio_bytes(audio_numpy, 'wav')
    """
    if audio_data is None or len(audio_data) == 0:
        raise ValueError("audio_data cannot be empty")

    try:
        # Ensure audio is in the correct range [-1, 1]
        audio_data = np.clip(audio_data, -1.0, 1.0).astype(np.float32)

        if output_format.lower() == 'mp3':
            try:
                from pydub import AudioSegment

                # Convert to 16-bit PCM
                pcm_samples = (audio_data * 32767).astype(np.int16)

                # Create AudioSegment from raw data
                audio_segment = AudioSegment(
                    data=pcm_samples.tobytes(),
                    sample_width=2,
                    frame_rate=sample_rate,
                    channels=1
                )

                # Export as MP3
                output_buffer = io.BytesIO()
                audio_segment.export(output_buffer, format='mp3')
                output_buffer.seek(0)
                result = output_buffer.read()

                logger.debug(f"Converted numpy to MP3: {len(result)} bytes")
                return result

            except ImportError:
                logger.warning("pydub not available, falling back to WAV format")
                output_format = 'wav'

        # Use soundfile for other formats
        format_map = {
            'wav': ('WAV', 'PCM_16'),
            'flac': ('FLAC', None),
            'ogg': ('OGG', 'VORBIS'),
        }

        sf_format, subtype = format_map.get(output_format.lower(), ('WAV', 'PCM_16'))

        output_buffer = io.BytesIO()
        if subtype:
            sf.write(output_buffer, audio_data, sample_rate, format=sf_format, subtype=subtype)
        else:
            sf.write(output_buffer, audio_data, sample_rate, format=sf_format)

        output_buffer.seek(0)
        result = output_buffer.read()

        logger.debug(f"Converted numpy to {output_format}: {len(result)} bytes")
        return result

    except Exception as e:
        logger.error(f"Error converting numpy to audio bytes: {e}")
        raise RuntimeError(f"Failed to convert numpy to audio bytes: {str(e)}") from e
