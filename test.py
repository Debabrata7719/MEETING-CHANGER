import sounddevice as sd

for i, d in enumerate(sd.query_devices()):
    print(i, d["name"], "inputs:", d["max_input_channels"])
