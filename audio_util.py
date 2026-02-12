import numpy as np

def find_start_energy(audio_seg, start_sec, max_back=0.15, threshold_ratio=0.08):
    sr = audio_seg.frame_rate

    # convert audio segment to numpy array
    samples = np.array(audio_seg.get_array_of_samples()).astype(np.float32)

    # normalize to -1 and 1
    samples /= np.iinfo(audio_seg.array_type).max

    start_sample = int(start_sec * sr)
    back_samples = int(max_back * sr)

    window = samples[max(0, start_sample - back_samples):start_sample]

    if len(window) == 0:
        return start_sec

    peak = np.max(np.abs(window))
    threshold = peak * threshold_ratio

    # Find first sample exceeding energy threshold
    for i, v in enumerate(window):
        if abs(v) > threshold:
            new_start_sample = start_sample - back_samples + i
            return max(0, new_start_sample / sr)

    return start_sec
