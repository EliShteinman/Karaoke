"""
Test Configuration Examples

Copy this file to 'test_config.py' and modify the paths for your specific tests.
This file shows different test scenarios you can set up.
"""

# =====================================
# TEST CONFIGURATION EXAMPLES
# =====================================

# Example 1: Test with existing data file
TEST_CONFIG_EXAMPLE_1 = {
    "input_path": "/Users/lyhwstynmn/פרוייקטים/python/Karaoke/data/audio/1VrXceBBuc8/vocals.wav",
    "output_dir": "/Users/lyhwstynmn/פרוייקטים/python/Karaoke/services/transcriptionService/tests/output",
    "output_file": "rgSvk335zis_test.lrc",
    "test_name": "Hebrew Song Quality Test - rgSvk335zis",
    "description": "Testing Hebrew transcription quality on existing data file"
}

# Example 2: Test with custom audio file
TEST_CONFIG_EXAMPLE_2 = {
    "input_path": "/path/to/your/custom/audio.wav",
    "output_dir": "/Users/lyhwstynmn/פרוייקטים/python/Karaoke/services/transcriptionService/tests/output",
    "output_file": "custom_test.lrc",
    "test_name": "Custom Audio File Test",
    "description": "Testing transcription on custom audio file"
}

# Example 3: Hebrew music specific test
TEST_CONFIG_HEBREW_MUSIC = {
    "input_path": "/path/to/hebrew/music.wav",
    "output_dir": "/Users/lyhwstynmn/פרוייקטים/python/Karaoke/services/transcriptionService/tests/output",
    "output_file": "hebrew_music_quality_test.lrc",
    "test_name": "Hebrew Music Quality Assessment",
    "description": "Specific test for Hebrew music transcription accuracy"
}

# =====================================
# ACTIVE TEST CONFIG
# =====================================

# Change this to the config you want to use
ACTIVE_CONFIG = TEST_CONFIG_EXAMPLE_1

# =====================================
# USAGE INSTRUCTIONS
# =====================================

"""
To use this configuration:

1. Copy this file to 'test_config.py':
   cp test_config_example.py test_config.py

2. Edit test_config.py with your specific paths

3. Modify manual_transcription_test.py to import from test_config:
   from test_config import ACTIVE_CONFIG

   # Then use:
   INPUT_AUDIO_PATH = ACTIVE_CONFIG["input_path"]
   OUTPUT_DIR = ACTIVE_CONFIG["output_dir"]
   # etc.

4. Run your test:
   python manual_transcription_test.py
"""