from faster_whisper import WhisperModel

class SpeechToTextService:
    def __init__(self, model_name="base", device="cpu"):
        # אפשרויות: tiny / base / small / medium / large
        self.model = WhisperModel(model_name, device=device)

    def transcribe_audio(self, audio_path: str):
        segments, info = self.model.transcribe(audio_path)

        results = []
        for seg in segments:
            results.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip()
            })

        return {
            "segments": results,
            "language": info.language,
            "duration": info.duration
        }
