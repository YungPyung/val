"""Create a new 'amplitudes.npy' to replace the original

**The original file will be overwritten if no changes to out_path**

Edit:
'params_path' - your params.py path inside data directory
'out_path' (optional) - default is data directory
'batch_size' (optional) - change depending on available RAM

This may take a few minutes

"""

from phylib.io.model import load_model
import numpy as np
import os

# Load
params_path = ""
model = load_model(params_path)
n_spikes = model.n_spikes
spike_clusters = model.spike_clusters           # cluster id
clusters_channels = model.clusters_channels     # best channel id        

# Initialize
amps = np.zeros(n_spikes, dtype=np.float64)

# Batches
batch_size = 50000
all_ids = np.arange(n_spikes)
print(f"Processing {n_spikes} spikes in batches of {batch_size}")

# Best-channel peak to trough
for start in range(0, n_spikes, batch_size):
    end = min(start + batch_size, n_spikes)
    spike_ids = all_ids[start:end]                  

    # shape (spikes, samples, channels)
    wfs = model.get_waveforms(spike_ids)

    # find best channel and extract
    best_ch = clusters_channels[spike_clusters[spike_ids]]
    wf_best   = wfs[np.arange(len(spike_ids)), :, best_ch]

    # peak to trough
    p = wf_best.max(axis=1)                        
    t = wf_best.min(axis=1)                       
    amps_batch = p - t                                     

    # store
    amps[spike_ids] = amps_batch

    print(f"Processing {start}-{end} out of {n_spikes}")

# Save
out_dir = os.path.dirname(params_path)
out_path = os.path.join(out_dir, "amplitudes.npy")
np.save(out_path, amps)
print(f"Saved best-channel peak-to-trough to {out_path}")
