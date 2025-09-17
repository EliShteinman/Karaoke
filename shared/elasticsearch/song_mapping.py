"""
Elasticsearch mapping for the songs index in HebKaraoke project
"""

SONGS_INDEX_MAPPING = {
    "properties": {
        "title": {
            "type": "text",
            "analyzer": "standard",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "artist": {
            "type": "text",
            "analyzer": "standard",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "channel": {
            "type": "keyword"
        },
        "duration": {
            "type": "integer"
        },
        "thumbnail": {
            "type": "keyword",
            "index": False
        },
        "status": {
            "properties": {
                "overall": {
                    "type": "keyword"
                },
                "download": {
                    "type": "keyword"
                },
                "audio_processing": {
                    "type": "keyword"
                },
                "transcription": {
                    "type": "keyword"
                }
            }
        },
        "created_at": {
            "type": "date",
            "format": "strict_date_optional_time||epoch_millis"
        },
        "updated_at": {
            "type": "date",
            "format": "strict_date_optional_time||epoch_millis"
        },
        "file_paths": {
            "properties": {
                "original": {
                    "type": "keyword",
                    "index": False
                },
                "vocals_removed": {
                    "type": "keyword",
                    "index": False
                },
                "lyrics": {
                    "type": "keyword",
                    "index": False
                }
            }
        },
        "metadata": {
            "properties": {
                "original_size": {
                    "type": "long"
                },
                "total_processing_time": {
                    "type": "float"
                },
                "quality_scores": {
                    "properties": {
                        "audio_processing": {
                            "type": "float"
                        },
                        "transcription": {
                            "type": "float"
                        }
                    }
                }
            }
        },
        "search_text": {
            "type": "text",
            "analyzer": "standard"
        },
        "error": {
            "properties": {
                "code": {
                    "type": "keyword"
                },
                "message": {
                    "type": "text"
                },
                "timestamp": {
                    "type": "date",
                    "format": "strict_date_optional_time||epoch_millis"
                },
                "service": {
                    "type": "keyword"
                }
            }
        }
    }
}


SONGS_INDEX_SETTINGS = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
        "analyzer": {
            "hebrew_text": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["lowercase", "asciifolding"]
            }
        }
    }
}