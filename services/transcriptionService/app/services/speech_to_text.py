import time
from typing import Dict, Any, Optional

import numpy as np
from faster_whisper import WhisperModel

from shared.utils.logger import Logger

# Import config and models
from ..services.config import TranscriptionServiceConfig
from ..models import TranscriptionOutput, TranscriptionResult, ProcessingMetadata, TranscriptionSegment

class SpeechToTextService:
    def __init__(self) -> None:
        self.logger = Logger.get_logger(__name__)
        self.config = TranscriptionServiceConfig()

        self.model_name: str = self.config.stt_model_name
        self.model: Optional[WhisperModel] = None
        
        try:
            self.logger.info(f"Loading Speech-to-Text model: {self.config.stt_model_name} (device: {self.config.stt_device}, compute: {self.config.stt_compute_type})")
            self.model = WhisperModel(
                self.config.stt_model_name, 
                device=self.config.stt_device, 
                compute_type=self.config.stt_compute_type
            )
            self.logger.info("Speech-to-Text model loaded successfully.")
        except Exception as e:
            self.logger.critical(f"Failed to load Speech-to-Text model '{self.model_name}'. Error: {e}")
            raise

    def transcribe_audio(self, audio_path: str) -> TranscriptionOutput:
        if not self.model:
            self.logger.error("SpeechToTextService is not properly initialized; model is not loaded.")
            raise RuntimeError("SpeechToTextService is not properly initialized; model is not loaded.")

        transcription_params: Dict[str, Any] = {
            "language": None,
            "beam_size": 5,
            "word_timestamps": True,
            "vad_filter": True,
            "vad_parameters": {
                "threshold": 0.5,
                "min_speech_duration_ms": 250,
                "max_speech_duration_s": 30,
                "min_silence_duration_ms": 2000,
                "speech_pad_ms": 400
            }
        }

        start_time = time.time()
        
        try:
            self.logger.debug(f"Starting transcription for: {audio_path}")
            segments_iterator, info = self.model.transcribe(audio_path, **transcription_params)

            segments = []
            word_count = 0
            all_word_probabilities = []

            for seg in segments_iterator:
                segment = TranscriptionSegment(start=seg.start, end=seg.end, text=seg.text.strip())
                segments.append(segment)
                if seg.words:
                    word_count += len(seg.words)
                    all_word_probabilities.extend([word.probability for word in seg.words])

            processing_time = time.time() - start_time
            self.logger.debug(f"Transcription completed in {processing_time:.2f} seconds.")

            confidence_score = float(np.mean(all_word_probabilities)) if all_word_probabilities else 0.0

            transcription_result = TranscriptionResult(segments=segments, full_text=" ".join([s.text for s in segments]))
            processing_metadata = ProcessingMetadata(
                processing_time=round(processing_time, 2),
                confidence_score=round(confidence_score, 4),
                language_detected=info.language,
                language_probability=info.language_probability,
                word_count=word_count,
                line_count=len(segments),
                model_used=self.model_name,
                duration_seconds=info.duration
            )

            return TranscriptionOutput(transcription_result=transcription_result, processing_metadata=processing_metadata)
        except Exception as e:
            self.logger.error(f"An error occurred during audio transcription for file {audio_path}. Error: {e}")
            raise
