from src.recorder import start_recording, stop_recording
import time

s = start_recording()
time.sleep(10)
stop_recording(s)
