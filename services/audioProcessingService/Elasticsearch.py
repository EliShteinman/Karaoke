from shared.repositories.factory import RepositoryFactory


class SongRepositoryWrapper:
    def __init__(self, host, port, scheme, index, async_mode):
        """
        Initializes the SongRepository instance using the RepositoryFactory.
        """
        # The async_mode is set to False for synchronous operation
        self.song_repo = RepositoryFactory.create_song_repository_from_params(
            elasticsearch_host=host,
            elasticsearch_port=port,
            elasticsearch_scheme=scheme,
            songs_index=index,
            async_mode=False
        )
        print("SongRepository instance created in synchronous mode.")

    def get_original_audio_path(self, video_id: str) -> str | None:
        """
        Retrieves the original audio file path for a given video ID from Elasticsearch.

        Args:
            video_id (str): The unique identifier for the video/song.

        Returns:
            str: The file path if found, otherwise None.
        """
        try:
            # Retrieves the song document from Elasticsearch
            song_doc = self.song_repo.get_song_by_id(video_id)
            if song_doc and 'file_paths' in song_doc and 'original' in song_doc['file_paths']:
                # The path is in the 'file_paths.original' field
                return song_doc['file_paths']['original']
            else:
                print(f"File path not found for video ID: {video_id}")
                return None
        except Exception as e:
            print(f"Error retrieving song data for {video_id}: {e}")
            return None



