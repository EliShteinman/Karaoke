import subprocess
import soundfile as sf
import numpy as np
import os
import shutil




def separate_vocals(input_file, save_path, output_dir="output"):
    """
    מפריד ווקאל מכלי נגינה בעזרת demucs.

    :param input_file: קובץ קלט (mp3/wav)
    :param output_dir: תיקיית פלט זמנית של demucs
    :param save_path: אם הוגדר -> לשמור לשם (vocals & accompaniment)
    """
    # להריץ את Demucs
    subprocess.run(["demucs", input_file, "-o", output_dir], check=True)

    # נתיב שבו Demucs שומר את הקבצים
    model_name = "htdemucs"  # אפשר לשנות ל-mdx_extra_q
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    folder = os.path.join(output_dir, model_name, base_name)

    # לקרוא את הקבצים (WAV בלבד)
    vocals, sr = sf.read(os.path.join(folder, "vocals.wav"))
    drums, _ = sf.read(os.path.join(folder, "drums.wav"))
    bass, _ = sf.read(os.path.join(folder, "bass.wav"))
    other, _ = sf.read(os.path.join(folder, "other.wav"))

    accompaniment = drums + bass + other
    # למחוק את התיקייה אחרי הקריאה
    shutil.rmtree(folder, ignore_errors=True)

    # לשמור
    vocals_path = os.path.join(save_path, "vocals.wav")
    accomp_path = os.path.join(save_path, "accompaniment.wav")

    sf.write(vocals_path, vocals, sr)
    sf.write(accomp_path, accompaniment, sr)
    print(f"הקבצים נשמרו:\n{vocals_path}\n{accomp_path}")