# src/recorder.py

import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

FS = 16000
CHANNELS = 1

recording = []
is_recording = False


def _callback(indata, frames, time, status):
    if is_recording:
        recording.append(indata.copy())


def start_recording():
    global is_recording, recording

    recording = []
    is_recording = True

    stream = sd.InputStream(
        samplerate=FS,
        channels=CHANNELS,
        callback=_callback
    )
    stream.start()

    return stream


def stop_recording(stream, filename="uploads/meeting.wav"):
    global is_recording

    is_recording = False
    stream.stop()
    stream.close()

    audio = np.concatenate(recording, axis=0)
    write(filename, FS, audio)

    return filename
