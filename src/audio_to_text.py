import whisper
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
audio_path = os.path.join(BASE_DIR, "data", "intermediate", "clean_meeting_audio.wav")
output_folder = os.path.join(BASE_DIR, "data", "intermediate")

os.makedirs(output_folder, exist_ok=True)

model = whisper.load_model("small")

# PASS THE AUDIO FILE FROM THE FOLDER
result = model.transcribe(audio_path)


output_file = os.path.join(output_folder, "transcript.txt")

segments = result["segments"]

with open(output_file, "w", encoding="utf-8") as f:
    for seg in segments:
        f.write(seg["text"].strip() + "\n")


print(f"Transcript saved at {output_file}")