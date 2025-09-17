from consumer import get_video_ids_from_kafka
from Elasticsearch import SongRepositoryWrapper
from Passwords import ES_HOST, ES_PORT, ES_SCHEME, ES_INDEX , TOPICS, GROUP_ID, BOOTSTRAP_SERVERS
from Audio_separation import separate_vocals
import os

if __name__ == "__main__":
    id_generator = get_video_ids_from_kafka(TOPICS, BOOTSTRAP_SERVERS, GROUP_ID)
    repo_wrapper = SongRepositoryWrapper(
        host=ES_HOST,
        port=ES_PORT,
        scheme=ES_SCHEME,
        index=ES_INDEX,
        async_mode=False
    )
    for vid_id in id_generator:
        audio_path = repo_wrapper.get_original_audio_path(vid_id)
        if audio_path:
            directory_path = os.path.dirname(vid_id)
            separate_vocals(audio_path, save_path=directory_path)


