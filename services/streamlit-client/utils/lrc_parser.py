import re
from dataclasses import dataclass

@dataclass
class LrcLine:
    timestamp: float
    text: str

def parse_lrc(lrc_content: str) -> list[LrcLine]:
    """Parses a .lrc file content into a list of timed lyric lines."""
    lines = []
    # Regex to capture [mm:ss.xx] timestamps and the lyric text
    lrc_regex = re.compile(r"^\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)$")

    for line in lrc_content.splitlines():
        match = lrc_regex.match(line)
        if not match:
            continue

        minutes, seconds, centiseconds, text = match.groups()
        # Pad centiseconds if they are 2 digits (e.g., .12 -> .120)
        if len(centiseconds) == 2:
            centiseconds += '0'
        
        total_seconds = int(minutes) * 60 + int(seconds) + int(centiseconds) / 1000.0
        
        lines.append(LrcLine(timestamp=total_seconds, text=text.strip()))

    return sorted(lines, key=lambda x: x.timestamp)
