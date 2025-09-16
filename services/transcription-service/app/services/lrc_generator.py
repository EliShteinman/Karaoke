from .text_processor import clean_text

def format_lrc_timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:05.2f}"

def create_lrc_file(segments, metadata, output_path):
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

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lrc_content))

    return output_path
