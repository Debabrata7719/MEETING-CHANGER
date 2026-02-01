import whisper
import os

audio_path = "video_to_audio/clean_meeting_audio.wav"   # real audio file
output_folder = "audio_to_text"

os.makedirs(output_folder, exist_ok=True)

model = whisper.load_model("small")

# PASS THE AUDIO FILE FROM THE FOLDER
result = model.transcribe(audio_path)


output_file = os.path.join(output_folder, "Converted Audio To Text.txt")

segments = result["segments"]

with open(output_file, "w", encoding="utf-8") as f:
    for seg in segments:
        f.write(seg["text"].strip() + "\n")


print(f"Transcript saved at {output_file}")