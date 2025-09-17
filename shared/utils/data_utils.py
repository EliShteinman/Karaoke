"""
Data normalization utilities for the Karaoke project.

This module provides centralized data normalization functions for all services
to ensure consistent handling of Elasticsearch documents and other data structures.
"""
from typing import Dict, Any, Optional, Union


def normalize_elasticsearch_song_document(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert flat Elasticsearch data structure to nested structure.

    This function handles the conversion from Elasticsearch's flat field storage
    (e.g., 'file_paths.original', 'status.download') to nested objects that are
    easier to work with programmatically.

    Args:
        raw_data: Raw document data from Elasticsearch

    Returns:
        Normalized dictionary with nested structures for status, file_paths, and metadata

    Example:
        Input: {'file_paths.original': 'audio/vid/file.mp3', 'status.download': 'completed'}
        Output: {'file_paths': {'original': 'audio/vid/file.mp3'}, 'status': {'download': 'completed'}}
    """
    normalized = {}

    # Basic fields - copy directly
    basic_fields = [
        'video_id', 'title', 'artist', 'channel', 'duration',
        'thumbnail', 'search_text', 'created_at', 'updated_at'
    ]
    for field in basic_fields:
        if field in raw_data:
            normalized[field] = raw_data[field]

    # Handle status fields - convert flat to nested
    normalized['status'] = _normalize_status_fields(raw_data)

    # Handle file_paths fields - convert flat to nested
    normalized['file_paths'] = _normalize_file_paths_fields(raw_data)

    # Handle metadata fields - convert flat to nested
    normalized['metadata'] = _normalize_metadata_fields(raw_data)

    # Handle error field if present
    if 'error' in raw_data:
        normalized['error'] = raw_data['error']

    return normalized


def _normalize_status_fields(raw_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Normalize status fields from flat to nested structure.

    Handles both nested status objects and flat 'status.field' keys.
    """
    status = {}
    status_fields = ['overall', 'download', 'audio_processing', 'transcription']

    for status_field in status_fields:
        # Try nested structure first
        if 'status' in raw_data and isinstance(raw_data['status'], dict):
            status[status_field] = raw_data['status'].get(status_field, 'pending')
        # Try flat structure
        elif f'status.{status_field}' in raw_data:
            status[status_field] = raw_data[f'status.{status_field}']
        # Default value
        else:
            status[status_field] = 'pending'

    return status


def _normalize_file_paths_fields(raw_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Normalize file_paths fields from flat to nested structure.

    Handles both nested file_paths objects and flat 'file_paths.field' keys.
    """
    file_paths = {}
    path_types = ['original', 'vocals_removed', 'lyrics']

    for path_type in path_types:
        # Try flat structure first (this is the common format from repository)
        if f'file_paths.{path_type}' in raw_data:
            file_paths[path_type] = raw_data[f'file_paths.{path_type}']
        # Try nested structure as fallback
        elif 'file_paths' in raw_data and isinstance(raw_data['file_paths'], dict):
            if path_type in raw_data['file_paths']:
                file_paths[path_type] = raw_data['file_paths'][path_type]

    return file_paths


def _normalize_metadata_fields(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize metadata fields from flat to nested structure.

    Handles both nested metadata objects and flat 'metadata.field' keys.
    """
    metadata = {}

    # Try nested structure first
    if 'metadata' in raw_data and isinstance(raw_data['metadata'], dict):
        metadata = raw_data['metadata'].copy()

    # Look for flat metadata fields and merge them
    for key, value in raw_data.items():
        if key.startswith('metadata.'):
            metadata_key = key.replace('metadata.', '')
            metadata[metadata_key] = value

    return metadata


def get_nested_value(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Safely get a nested value from a dictionary using dot notation.

    Args:
        data: Dictionary to search in
        key_path: Dot-separated path (e.g., 'file_paths.original')
        default: Default value if key not found

    Returns:
        Value at the specified path or default

    Example:
        get_nested_value({'file_paths': {'original': 'path'}}, 'file_paths.original')
        Returns: 'path'
    """
    keys = key_path.split('.')
    current = data

    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def set_nested_value(data: Dict[str, Any], key_path: str, value: Any) -> None:
    """
    Set a nested value in a dictionary using dot notation.

    Args:
        data: Dictionary to modify
        key_path: Dot-separated path (e.g., 'file_paths.original')
        value: Value to set

    Example:
        set_nested_value(data, 'file_paths.original', 'new_path')
        Sets data['file_paths']['original'] = 'new_path'
    """
    keys = key_path.split('.')
    current = data

    # Navigate to the parent of the final key
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    # Set the final value
    current[keys[-1]] = value


def validate_song_document(doc: Dict[str, Any]) -> bool:
    """
    Validate that a song document has the required structure.

    Args:
        doc: Song document to validate

    Returns:
        True if document has valid structure
    """
    required_fields = ['video_id', 'title', 'status', 'file_paths']

    for field in required_fields:
        if field not in doc:
            return False

    # Validate nested structures
    if not isinstance(doc['status'], dict):
        return False

    if not isinstance(doc['file_paths'], dict):
        return False

    return True