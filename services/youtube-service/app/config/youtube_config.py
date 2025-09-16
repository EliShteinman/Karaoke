import os
from dotenv import load_dotenv

# טוען משתנים מקובץ .env
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_SERVICE_NAME = os.getenv("YOUTUBE_API_SERVICE_NAME", "youtube")
YOUTUBE_API_VERSION = os.getenv("YOUTUBE_API_VERSION", "v3")
