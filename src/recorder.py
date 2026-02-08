# src/recorder.py

import sounddevice as sd
import numpy as np
import soundfile as sf

FS = 16000
CHANNELS = 1

recording = []
is_recording = False


# =================================
# Find loopback / stereo mix device
# =================================
def _get_loopback_device():
    devices = sd.query_devices()

    for i, dev in enumerate(devices):
        name = dev["name"].lower()

        # works on Windows/Mac
        if "loopback" in name or "stereo mix" in name:
            print(f"✅ Using system audio device: {dev['name']}")
            return i

    print("⚠️ Loopback not found, using default mic only")
    return None


# =================================
# Callback
# =================================
def _callback(indata, frames, time, status):
    if is_recording:
        recording.append(indata.copy())


# =================================
# Start recording
# =================================
def start_recording():
    global is_recording, recording

    recording = []
    is_recording = True

    device = _get_loopback_device()   # 🔥 NEW

    stream = sd.InputStream(
        samplerate=FS,
        channels=CHANNELS,
        device=device,                # 🔥 SYSTEM AUDIO HERE
        callback=_callback
    )

    stream.start()

    print("🎙 Recording started...")
    return stream


# =================================
# Stop recording
# =================================
def stop_recording(stream, filename="uploads/meeting.wav"):
    global is_recording

    is_recording = False

    stream.stop()
    stream.close()

    audio = np.concatenate(recording, axis=0)

    sf.write(filename, audio, FS)   # 🔥 better than scipy write

    print(f"✅ Recording saved to {filename}")

    return filename
