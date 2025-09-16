"""
Pydantic models for the Transcription Service
"""
from datetime import datetime
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class TranscriptionSegment(BaseModel):
    """Single transcription segment with timing information"""
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Transcribed text for this segment")


class TranscriptionResult(BaseModel):
    """Complete transcription result"""
    segments: List[TranscriptionSegment] = Field(..., description="List of transcription segments")
    full_text: str = Field(..., description="Complete transcribed text")


class ProcessingMetadata(BaseModel):
    """Metadata about the transcription processing"""
    processing_time: float = Field(..., description="Processing time in seconds")
    confidence_score: float = Field(..., description="Overall confidence score")
    language_detected: str = Field(..., description="Detected language code")
    language_probability: float = Field(..., description="Language detection confidence")
    word_count: int = Field(..., description="Total number of words")
    line_count: int = Field(..., description="Total number of lines/segments")
    model_used: str = Field(..., description="Speech-to-text model used")
    duration_seconds: float = Field(..., description="Audio duration in seconds")


class TranscriptionOutput(BaseModel):
    """Complete transcription service output"""
    transcription_result: TranscriptionResult
    processing_metadata: ProcessingMetadata


class LRCMetadata(BaseModel):
    """Metadata for LRC file generation"""
    artist: str = Field(default="", description="Song artist")
    title: str = Field(default="", description="Song title")
    album: str = Field(default="", description="Album name")


class KafkaRequestMessage(BaseModel):
    """Incoming Kafka message structure"""
    video_id: str = Field(..., description="YouTube video ID", min_length=11, max_length=11)
    action: str = Field(default="transcribe", description="Action to perform")


class KafkaDoneMessage(BaseModel):
    """Outgoing Kafka success message structure"""
    video_id: str = Field(..., description="YouTube video ID")
    status: str = Field(default="transcription_done", description="Processing status")
    language: str = Field(..., description="Detected language")
    confidence: float = Field(..., description="Overall confidence score")
    word_count: int = Field(..., description="Total word count")
    line_count: int = Field(..., description="Total line count")
    processing_time: float = Field(..., description="Processing time in seconds")
    model_used: str = Field(..., description="Model used for transcription")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")
    timestamp: str = Field(..., description="Processing completion timestamp")


class ErrorDetails(BaseModel):
    """Error details structure"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    service: str = Field(default="transcription_service", description="Service name")
    timestamp: str = Field(..., description="Error timestamp")
    trace: Optional[str] = Field(None, description="Error traceback")


class KafkaFailedMessage(BaseModel):
    """Outgoing Kafka failure message structure"""
    video_id: str = Field(..., description="YouTube video ID")
    status: str = Field(default="failed", description="Processing status")
    error: ErrorDetails = Field(..., description="Error details")


class ElasticsearchSongDocument(BaseModel):
    """Song document structure as expected from Elasticsearch"""
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Song title")
    artist: str = Field(..., description="Song artist")
    album: Optional[str] = Field(None, description="Album name")
    file_paths: Dict[str, str] = Field(..., description="File paths dictionary")
    status: str = Field(..., description="Processing status")


class ElasticsearchUpdateRequest(BaseModel):
    """Elasticsearch document update request"""
    doc: Dict[str, Union[str, Dict, float, int]] = Field(..., description="Document update fields")