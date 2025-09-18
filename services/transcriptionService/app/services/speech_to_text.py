import time
from typing import Dict, Any, Optional

import numpy as np
from faster_whisper import WhisperModel

from shared.utils.logger import Logger

# Import config and models
from services.transcriptionService.app.services.config import TranscriptionServiceConfig
from services.transcriptionService.app.models import TranscriptionOutput, TranscriptionResult, ProcessingMetadata, TranscriptionSegment, WordTimestamp

class SpeechToTextService:
    def __init__(self) -> None:
        self.config = TranscriptionServiceConfig()
        self.logger = Logger.get_logger(__name__)

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

        self.logger.info(f"Starting transcription process for audio file: {audio_path}")
        self.logger.debug(f"Model configuration: {self.model_name} (device: {self.config.stt_device}, compute: {self.config.stt_compute_type})")

        # Use Hebrew as preferred language for Israeli music content
        # Hebrew-optimized model should work better with explicit language setting
        preferred_language = "he"  # Hebrew language for better transcription

        transcription_params: Dict[str, Any] = {
            "language": preferred_language,  # Single language code or None for auto-detection
            "beam_size": 5,
            "word_timestamps": True,
            "vad_filter": True,
            "initial_prompt": "שיר בעברית עם מילים וכתוביות, מוסיקה עברית עם מילים",  # Hebrew prompt for better context
            "vad_parameters": {
                "threshold": 0.2,  # More aggressive threshold for music with vocals
                "min_speech_duration_ms": 100,  # Even shorter for brief musical phrases
                "max_speech_duration_s": 30,  # Shorter max for better line segmentation
                "min_silence_duration_ms": 500,  # Shorter silence gaps between lyrics
                "speech_pad_ms": 150  # Minimal padding for tighter vocal detection
            }
        }

        self.logger.debug(f"Transcription parameters: {transcription_params}")
        start_time = time.time()

        try:
            self.logger.debug(f"Initiating Whisper transcription for: {audio_path}")
            segments_iterator, info = self.model.transcribe(audio_path, **transcription_params)

            self.logger.info(f"Audio analysis complete. Detected language: {info.language} (confidence: {info.language_probability:.4f})")
            self.logger.debug(f"Audio duration: {info.duration:.2f} seconds")

            segments = []
            word_count = 0
            all_word_probabilities = []

            self.logger.debug("Processing transcription segments...")
            for i, seg in enumerate(segments_iterator):
                word_data = None
                if seg.words:
                    word_count += len(seg.words)
                    all_word_probabilities.extend([word.probability for word in seg.words])
                    word_data = [
                        WordTimestamp(word=w.word, start=w.start, end=w.end, probability=w.probability)
                        for w in seg.words
                    ]
                segment = TranscriptionSegment(
                    start=seg.start, end=seg.end, text=seg.text.strip(), words=word_data
                )
                segments.append(segment)

                if i % 10 == 0:  # Log every 10th segment to avoid spam
                    self.logger.debug(f"Processed segment {i + 1}: [{seg.start:.2f}s - {seg.end:.2f}s] '{seg.text.strip()[:50]}{'...' if len(seg.text.strip()) > 50 else ''}'")

            processing_time = time.time() - start_time
            confidence_score = float(np.mean(all_word_probabilities)) if all_word_probabilities else 0.0

            self.logger.info(f"Transcription completed successfully in {processing_time:.2f} seconds")
            self.logger.info(f"Results: {len(segments)} segments, {word_count} words, average confidence: {confidence_score:.4f}")

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

            self.logger.debug(f"Processing metadata: {processing_metadata.dict()}")
            return TranscriptionOutput(transcription_result=transcription_result, processing_metadata=processing_metadata)
        except Exception as e:
            self.logger.error(f"Transcription failed for file {audio_path}. Error: {e}")
            self.logger.debug(f"Transcription error traceback: {str(e)}")
            raise
