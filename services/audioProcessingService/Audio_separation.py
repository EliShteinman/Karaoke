"""
Audio separation module for vocal removal using advanced algorithms.

This module provides vocal separation functionality using the Demucs library,
which uses machine learning models to separate vocals from instrumental music.
"""

import subprocess
import soundfile as sf
import numpy as np
import os
import shutil
import logging
import tempfile
from typing import Tuple, Optional
from pathlib import Path

from shared.utils.logger import Logger

logger = Logger.get_logger(__name__)


class AudioSeparationError(Exception):
    """Custom exception for audio separation errors"""
    pass


def separate_vocals(input_file: str, save_path: str, output_dir: str = "output") -> Tuple[str, str]:
    """
    Separate vocals from instrumental music using Demucs.

    This function uses the Demucs ML model to separate audio into vocals and accompaniment.
    The final output files have fixed names: vocals_removed.wav (accompaniment only).

    Args:
        input_file: Path to input audio file (wav)
        save_path: Directory where to save the final output files
        output_dir: Temporary directory for Demucs processing

    Returns:
        Tuple of (vocals_removed_path, vocals_path)

    Raises:
        AudioSeparationError: If separation fails
        FileNotFoundError: If input file doesn't exist
        OSError: If there are file system issues
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    logger.info(f"Starting vocal separation for: {input_file}")

    # Create temporary directory for Demucs processing
    temp_dir = tempfile.mkdtemp(prefix="demucs_")

    try:
        # Run Demucs separation
        logger.info("Running Demucs audio separation...")
        result = subprocess.run(
            ["demucs", input_file, "-o", temp_dir],
            check=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        logger.debug(f"Demucs output: {result.stdout}")

        # Demucs output structure
        model_name = "htdemucs"  # Default Demucs model
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        demucs_output_folder = os.path.join(temp_dir, model_name, base_name)

        if not os.path.exists(demucs_output_folder):
            raise AudioSeparationError(f"Demucs output folder not found: {demucs_output_folder}")

        # Read separated audio components
        logger.info("Reading separated audio components...")
        try:
            vocals_path = os.path.join(demucs_output_folder, "vocals.wav")
            drums_path = os.path.join(demucs_output_folder, "drums.wav")
            bass_path = os.path.join(demucs_output_folder, "bass.wav")
            other_path = os.path.join(demucs_output_folder, "other.wav")

            # Verify all required files exist
            for component_path, component_name in [
                (vocals_path, "vocals"), (drums_path, "drums"),
                (bass_path, "bass"), (other_path, "other")
            ]:
                if not os.path.exists(component_path):
                    raise AudioSeparationError(f"Demucs did not generate {component_name} component: {component_path}")

            # Read audio components
            vocals, sr = sf.read(vocals_path)
            drums, _ = sf.read(drums_path)
            bass, _ = sf.read(bass_path)
            other, _ = sf.read(other_path)

            logger.info(f"Successfully read audio components, sample rate: {sr}")

        except Exception as e:
            raise AudioSeparationError(f"Failed to read Demucs output files: {e}")

        # Combine instrumental components (everything except vocals)
        logger.info("Combining instrumental components...")
        accompaniment = drums + bass + other

        # Ensure output directory exists
        os.makedirs(save_path, exist_ok=True)

        # Save final output files with fixed names
        vocals_removed_path = os.path.join(save_path, "vocals_removed.wav")
        vocals_only_path = os.path.join(save_path, "vocals.wav")

        logger.info(f"Saving processed audio files to {save_path}")

        # Save accompaniment (vocals removed) as WAV
        sf.write(vocals_removed_path, accompaniment, sr)

        # Save vocals as WAV for potential future use
        sf.write(vocals_only_path, vocals, sr)

        # Verify output files were created and have reasonable sizes
        if not os.path.exists(vocals_removed_path):
            raise AudioSeparationError("Failed to create vocals_removed.wav file")

        if not os.path.exists(vocals_only_path):
            raise AudioSeparationError("Failed to create vocals.wav file")

        # Check file sizes
        input_size = os.path.getsize(input_file)
        output_size = os.path.getsize(vocals_removed_path)

        if output_size == 0:
            raise AudioSeparationError("Output file is empty")

        if output_size < (input_size * 0.05):  # Less than 5% seems too small
            logger.warning(f"Output file seems very small: {output_size} bytes vs input {input_size} bytes")

        logger.info(f"Audio separation completed successfully")
        logger.info(f"Output files: {vocals_removed_path}, {vocals_only_path}")

        return vocals_removed_path, vocals_only_path

    except subprocess.TimeoutExpired:
        raise AudioSeparationError("Demucs processing timed out (>10 minutes)")
    except subprocess.CalledProcessError as e:
        error_msg = f"Demucs failed with return code {e.returncode}"
        if e.stderr:
            error_msg += f": {e.stderr}"
        raise AudioSeparationError(error_msg)
    except Exception as e:
        raise AudioSeparationError(f"Unexpected error during vocal separation: {e}")
    finally:
        # Clean up temporary directory
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.debug(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")


def validate_audio_file(file_path: str) -> bool:
    """
    Validate that an audio file is readable and has expected properties.

    Args:
        file_path: Path to audio file

    Returns:
        bool: True if file is valid, False otherwise
    """
    try:
        if not os.path.exists(file_path):
            return False

        # Try to read file info
        info = sf.info(file_path)

        # Basic validation checks
        if info.frames == 0:
            logger.warning(f"Audio file has no frames: {file_path}")
            return False

        if info.samplerate < 8000 or info.samplerate > 192000:
            logger.warning(f"Unusual sample rate {info.samplerate} in file: {file_path}")

        if info.channels == 0:
            logger.warning(f"Audio file has no channels: {file_path}")
            return False

        logger.debug(f"Audio file validation passed: {file_path} - {info.frames} frames, {info.samplerate}Hz, {info.channels} channels")
        return True

    except Exception as e:
        logger.error(f"Audio file validation failed for {file_path}: {e}")
        return False