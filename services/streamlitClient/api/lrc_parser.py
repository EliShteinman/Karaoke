import re
from typing import List
from services.streamlitClient.config import StreamlitConfig
from services.streamlitClient.models import LrcLine

logger = StreamlitConfig.get_logger(__name__)


def parse_lrc(lrc_content: str) -> List[LrcLine]:
    """
    Parses a .lrc file content into a list of timed lyric lines.

    Args:
        lrc_content: Content of the LRC file as string

    Returns:
        List of LrcLine objects sorted by timestamp
    """
    logger.info(f"Starting LRC parsing. Content length: {len(lrc_content)}")
    lines = []

    try:
        # Regex to capture [mm:ss.xx] timestamps and the lyric text
        lrc_regex = re.compile(r"^\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)$")

        for i, line_text in enumerate(lrc_content.splitlines()):
            try:
                match = lrc_regex.match(line_text)
                if not match:
                    if line_text.strip():  # Log only if the line is not empty
                        logger.warning(f"LRC parsing: Line {i+1} does not match expected format: '{line_text}'")
                    continue

                minutes, seconds, centiseconds, text = match.groups()

                # Pad centiseconds if they are 2 digits (e.g., .12 -> .120)
                if len(centiseconds) == 2:
                    centiseconds += '0'

                total_seconds = int(minutes) * 60 + int(seconds) + int(centiseconds) / 1000.0

                # Create LrcLine using Pydantic model for validation
                lrc_line = LrcLine(timestamp=total_seconds, text=text.strip())
                lines.append(lrc_line)

            except Exception as e:
                logger.error(f"Error parsing LRC line {i+1}: '{line_text}' - {e}")
                continue

        sorted_lines = sorted(lines, key=lambda x: x.timestamp)
        logger.info(f"Finished LRC parsing. Found {len(sorted_lines)} valid lyric lines.")
        return sorted_lines

    except Exception as e:
        logger.error(f"Critical error during LRC parsing: {e}")
        return []


def find_current_line(current_time: float, lyrics: List[LrcLine]) -> dict:
    """
    Find the current active lyric line based on playback time.

    Args:
        current_time: Current playback time in seconds
        lyrics: List of LrcLine objects

    Returns:
        Dictionary with current line info and metadata
    """
    try:
        for i, line in enumerate(lyrics):
            # Calculate end time (next line's timestamp or current + 4 seconds default)
            end_time = lyrics[i + 1].timestamp if i + 1 < len(lyrics) else line.timestamp + 4

            if line.timestamp <= current_time < end_time:
                return {
                    'current_index': i,
                    'current_line': line,
                    'next_line': lyrics[i + 1] if i + 1 < len(lyrics) else None,
                    'progress': (current_time - line.timestamp) / (end_time - line.timestamp),
                    'end_time': end_time
                }

        return {
            'current_index': -1,
            'current_line': None,
            'next_line': None,
            'progress': 0.0,
            'end_time': 0.0
        }

    except Exception as e:
        logger.error(f"Error finding current lyric line: {e}")
        return {
            'current_index': -1,
            'current_line': None,
            'next_line': None,
            'progress': 0.0,
            'end_time': 0.0
        }
