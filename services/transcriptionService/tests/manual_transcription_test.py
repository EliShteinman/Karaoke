#!/usr/bin/env python3
"""
Manual Transcription Quality Test Script

This script allows you to test transcription quality manually by specifying
hardcoded input and output paths. Perfect for testing specific audio files
and evaluating transcription results.

Usage:
1. Edit the paths in the CONFIG section below
2. Run: python manual_transcription_test.py
3. Check the output LRC file for quality assessment
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to Python path to import from the service
sys.path.append(str(Path(__file__).parent.parent))

from services.transcriptionService.app.services.speech_to_text import SpeechToTextService
from services.transcriptionService.app.services.lrc_generator import create_lrc_file
from services.transcriptionService.app.models import LRCMetadata

# =====================================
# CONFIG - Edit these paths as needed
# =====================================

# Input audio file path (must exist)
INPUT_AUDIO_PATH = "/Users/lyhwstynmn/פרוייקטים/python/Karaoke/data/audio/rgSvk335zis/vocals.wav"

# Output directory for test results
OUTPUT_DIR = "/Users/lyhwstynmn/פרוייקטים/python/Karaoke/services/transcriptionService/tests/output"

# Output LRC file name (will be created in OUTPUT_DIR)
OUTPUT_LRC_FILE = "test_transcription.lrc"

# Test name/description for logging
TEST_NAME = "Hebrew Music Test - Manual Quality Check"

# =====================================
# Test Script
# =====================================

def setup_output_directory():
    """Create output directory if it doesn't exist"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"✅ Output directory ready: {OUTPUT_DIR}")

def verify_input_file():
    """Verify that input audio file exists"""
    if not os.path.exists(INPUT_AUDIO_PATH):
        print(f"❌ Error: Input file not found: {INPUT_AUDIO_PATH}")
        print("Please edit the INPUT_AUDIO_PATH in this script to point to your audio file.")
        return False

    file_size = os.path.getsize(INPUT_AUDIO_PATH) / (1024 * 1024)  # MB
    print(f"✅ Input file found: {INPUT_AUDIO_PATH}")
    print(f"   File size: {file_size:.1f} MB")
    return True

def run_transcription_test():
    """Run the transcription test"""
    print(f"\n🎯 Starting test: {TEST_NAME}")
    print("=" * 60)

    # Initialize services
    print("🔄 Initializing Speech-to-Text service...")
    try:
        stt_service = SpeechToTextService()
        print("✅ SpeechToTextService initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize SpeechToTextService: {e}")
        return False

    print("🔄 Preparing LRC generation...")
    print("✅ LRC generation function ready")

    # Run transcription
    print(f"\n🎤 Starting transcription of: {os.path.basename(INPUT_AUDIO_PATH)}")
    start_time = time.time()

    try:
        transcription_output = stt_service.transcribe_audio(INPUT_AUDIO_PATH)
        transcription_time = time.time() - start_time

        print(f"✅ Transcription completed in {transcription_time:.2f} seconds")
        print(f"   Confidence score: {transcription_output.processing_metadata.confidence_score:.3f}")
        print(f"   Language detected: {transcription_output.processing_metadata.language_detected}")
        print(f"   Word count: {transcription_output.processing_metadata.word_count}")
        print(f"   Segments: {transcription_output.processing_metadata.line_count}")

    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        return False

    # Generate LRC file
    print("\n📝 Generating LRC file...")
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_LRC_FILE)

    try:
        # Create metadata for the LRC file
        metadata = LRCMetadata(
            artist="Test Artist",
            title=f"Test Song - {os.path.basename(INPUT_AUDIO_PATH)}",
            album="Manual Test"
        )

        # For testing, we need to create a proper path that the LRC generator expects
        # Format: /shared/audio/{video_id}/lyrics.lrc
        test_video_id = "manual_test"
        lrc_path = f"/shared/audio/{test_video_id}/lyrics.lrc"

        actual_path = create_lrc_file(
            transcription_output.transcription_result.segments,
            metadata,
            lrc_path
        )

        # Copy the file to our desired output location for review
        import shutil
        shutil.copy2(actual_path, output_path)

        print(f"✅ LRC file generated: {output_path}")
        print(f"   (Source file: {actual_path})")

    except Exception as e:
        print(f"❌ LRC generation failed: {e}")
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        return False

    # Display results summary
    print("\n" + "=" * 60)
    print("📊 TRANSCRIPTION RESULTS SUMMARY")
    print("=" * 60)

    print(f"📁 Input file: {INPUT_AUDIO_PATH}")
    print(f"📁 Output file: {output_path}")
    print(f"⏱️  Processing time: {transcription_time:.2f} seconds")
    print(f"🎯 Confidence score: {transcription_output.processing_metadata.confidence_score:.3f}")
    print(f"🌍 Language detected: {transcription_output.processing_metadata.language_detected}")
    print(f"📊 Statistics:")
    print(f"   - Words: {transcription_output.processing_metadata.word_count}")
    print(f"   - Segments: {transcription_output.processing_metadata.line_count}")
    print(f"   - Duration: {transcription_output.processing_metadata.duration_seconds:.1f} seconds")

    # Show first few lines of transcription
    print(f"\n📜 First 3 segments preview:")
    segments = transcription_output.transcription_result.segments[:3]
    for i, segment in enumerate(segments, 1):
        print(f"   {i}. [{segment.start:.1f}s - {segment.end:.1f}s] {segment.text}")

    if len(transcription_output.transcription_result.segments) > 3:
        remaining = len(transcription_output.transcription_result.segments) - 3
        print(f"   ... and {remaining} more segments")

    print(f"\n✅ Test completed successfully!")
    print(f"👀 Review the full transcription in: {output_path}")

    return True

def main():
    """Main test execution"""
    print("🧪 Manual Transcription Quality Test")
    print("=" * 60)

    # Setup
    setup_output_directory()

    # Verify input
    if not verify_input_file():
        return 1

    # Run test
    success = run_transcription_test()

    if success:
        print("\n🎉 Test completed successfully!")
        print("💡 Next steps:")
        print("   1. Open the output LRC file to review transcription quality")
        print("   2. Check for Hebrew text encoding (should be proper Unicode)")
        print("   3. Verify timing accuracy of segments")
        print("   4. Assess overall transcription quality")
        return 0
    else:
        print("\n❌ Test failed!")
        return 1

if __name__ == "__main__":
    exit(main())