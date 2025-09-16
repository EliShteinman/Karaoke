from shared.utils.logger import Logger
from .text_processor import clean_text

# Initialize logger at the module level
logger = Logger.get_logger(__name__)

def format_lrc_timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:05.2f}"

def create_lrc_file(segments, metadata, output_path):
    logger.debug(f"Creating LRC file at: {output_path}")
    try:
        lrc_content = []
        lrc_content.append(f"[ar:{metadata.get('artist', '')}]")
        lrc_content.append(f"[ti:{metadata.get('title', '')}]")
        lrc_content.append(f"[al:{metadata.get('album', '')}]")
        lrc_content.append(f"[by:Karaoke AI System]")
        lrc_content.append("")

        for seg in segments:
            start_time = format_lrc_timestamp(seg["start"])
            text = clean_text(seg["text"])
            lrc_content.append(f"[{start_time}]{text}")

        # Ensure the directory exists before writing
        # (This is a good practice, though in our case the downloader service should have created it)
        # import os
        # os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lrc_content))
        
        logger.debug(f"Successfully created LRC file: {output_path}")
        return output_path

    except IOError as e:
        logger.error(f"Failed to write LRC file to {output_path}. Error: {e}")
        # Re-raise the exception to let the consumer handle the failure
        raise
