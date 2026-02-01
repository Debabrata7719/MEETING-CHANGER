import subprocess
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
video_path = os.path.join(BASE_DIR, "data", "input", "meeting.mp4")
output_folder = os.path.join(BASE_DIR, "data", "intermediate")
clean_audio_name = "clean_meeting_audio.wav"


def convert_and_clean_audio(video_path, output_folder, clean_audio_name):

    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, clean_audio_name)

    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-ar", "16000",     # speech friendly
        "-ac", "1",         # mono
        "-af", "loudnorm,afftdn",  # clean + normalize
        output_path
    ]

    subprocess.run(command, check=True)

    print(f" Clean audio saved at: {output_path}")
    return output_path


if __name__ == "__main__":
    clean_audio = convert_and_clean_audio(video_path, output_folder, clean_audio_name)
