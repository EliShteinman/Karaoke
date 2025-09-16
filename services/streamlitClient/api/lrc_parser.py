import re
from dataclasses import dataclass
from shared.utils import Logger

logger = Logger.get_logger()

@dataclass
class LrcLine:
    timestamp: float
    text: str

def parse_lrc(lrc_content: str) -> list[LrcLine]:
    """Parses a .lrc file content into a list of timed lyric lines."""
    logger.info(f"Starting LRC parsing. Content length: {len(lrc_content)}")
    lines = []
    # Regex to capture [mm:ss.xx] timestamps and the lyric text
    lrc_regex = re.compile(r"^\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)$")

    for i, line_text in enumerate(lrc_content.splitlines()):
        match = lrc_regex.match(line_text)
        if not match:
            if line_text.strip(): # Log only if the line is not empty
                logger.warning(f"LRC parsing: Line {i+1} does not match expected format: '{line_text}'")
            continue

        minutes, seconds, centiseconds, text = match.groups()
        # Pad centiseconds if they are 2 digits (e.g., .12 -> .120)
        if len(centiseconds) == 2:
            centiseconds += '0'
        
        total_seconds = int(minutes) * 60 + int(seconds) + int(centiseconds) / 1000.0
        
        lines.append(LrcLine(timestamp=total_seconds, text=text.strip()))

    sorted_lines = sorted(lines, key=lambda x: x.timestamp)
    logger.info(f"Finished LRC parsing. Found {len(sorted_lines)} valid lyric lines.")
    return sorted_lines
