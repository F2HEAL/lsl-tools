import numpy as np
import time
from pylsl import StreamInfo, StreamOutlet, local_clock

# -------------------------------------------------------
# CONFIGURATION (SynAmps-like)
# -------------------------------------------------------
n_channels = 32
sfreq = 1000  # Hz (SynAmps default)
chunk_size = 10
stream_name = "SynAmpsRT"
stream_type = "EEG"
manufacturer = "Compumedics Neuroscan"
model = "SynAmps RT"

# Typical 32-channel SynAmps / 10-20 naming
channel_labels = [
    "Fp1","Fp2","F3","F4","C3","C4","P3","P4",
    "O1","O2","F7","F8","T7","T8","P7","P8",
    "Fz","Cz","Pz","Oz","FC1","FC2","CP1","CP2",
    "FC5","FC6","CP5","CP6","TP9","TP10","POz","Iz"
]

# -------------------------------------------------------
# CREATE LSL STREAMINFO WITH METADATA
# -------------------------------------------------------
info = StreamInfo(stream_name, stream_type, n_channels, sfreq, 'float32', "synamps1234")

# Add metadata (very SynAmps-like)
desc = info.desc()
desc.append_child_value("manufacturer", manufacturer)
desc.append_child_value("model", model)

# Channel descriptors
ch = desc.append_child("channels")
for name in channel_labels:
    c = ch.append_child("channel")
    c.append_child_value("label", name)
    c.append_child_value("unit", "microvolts")
    c.append_child_value("type", "EEG")

# -------------------------------------------------------
# CREATE OUTLET
# -------------------------------------------------------
outlet = StreamOutlet(info, chunk_size)

print(">>> Synthetic 32-ch SynAmps LSL stream is LIVE...")
print(">>> Name :", stream_name)
print(">>> Type :", stream_type)
print(">>> Fs   :", sfreq)
print(">>> Use any LSL viewer (LabRecorder, MNE-LSL, etc.) to see it.\n")

# -------------------------------------------------------
# LIVE LOOP — STREAM EEG CHUNKS
# -------------------------------------------------------
t = 0.0
dt = 1.0 / sfreq

while True:
    # Generate synthetic EEG
    timepoints = t + np.arange(chunk_size) * dt
    t += chunk_size * dt

    # Basic mixture of rhythms per channel
    eeg = []
    for ch_id in range(n_channels):
        alpha = 20 * np.sin(2 * np.pi * 10 * timepoints)       # 10 Hz alpha
        beta  = 10 * np.sin(2 * np.pi * 20 * timepoints)       # 20 Hz beta
        noise = np.random.normal(0, 5, chunk_size)             # ~5 µV noise
        signal = alpha + beta + noise
        eeg.append(signal)

    # Shape to [chunk_size × channels]
    chunk = np.array(eeg).T.astype('float32')

    outlet.push_chunk(chunk.tolist(), timestamp=local_clock())

    time.sleep(chunk_size / sfreq)
