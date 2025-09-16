import os

def cleanup_file(path: str):
    if os.path.exists(path):
        os.remove(path)
