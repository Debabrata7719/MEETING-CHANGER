# 🎙️ Meeting Changer – Video to Text

A simple Python project that converts a video into text automatically.

## What it does
Video (.mp4)
→ Audio (FFmpeg)
→ Text transcript (OpenAI Whisper)

Basically: **Video → Audio → Text**

## Tools used
- FFmpeg (audio extraction + cleaning)
- OpenAI Whisper (speech-to-text)
- Python

## How to run

1. Install packages
pip install -r requirements.txt

2. Convert video to audio
python video_to_audio/convert_video_to_audio.py

3. Convert audio to text
python audio_to_text/transcribe.py

## Output
audio_to_text/transcript.txt

## Purpose
Built to convert meeting/lecture recordings into searchable notes.
