import os
import random
import numpy as np
import glob
import time
from pydub import AudioSegment

INPUT_DIR = "help_dataset"
OUTPUT_DIR = "help_dataset_aug"
NUM_AUG = 12

os.makedirs(OUTPUT_DIR, exist_ok=True)

def time_stretch(audio, rate=1.0):
    return audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * rate)
    }).set_frame_rate(audio.frame_rate)


def pitch_shift(audio, semitones):
    new_rate = int(audio.frame_rate * (2.0 ** (semitones / 12)))
    return audio._spawn(audio.raw_data, overrides={"frame_rate": new_rate}).set_frame_rate(audio.frame_rate)

def add_noise(audio, noise_level=0.005):
    samples = np.array(audio.get_array_of_samples())

    noise = np.random.randn(len(samples))
    augmented = samples + noise_level * np.max(samples) * noise

    augmented = augmented.astype(samples.dtype)

    return audio._spawn(augmented.tobytes())

all_files = glob.glob(INPUT_DIR + "/**/*", recursive=True)
all_files = [f for f in all_files if os.path.isfile(f)]

print(f"len(all_files): {len(all_files)}")

start_ns = time.time_ns()

print(f"Current time ns: {start_ns}")

i = 0

total_files = len(all_files)

for fname in all_files:
    if not fname.endswith(".wav"):
        continue

    audio = AudioSegment.from_wav(fname)

    base = os.path.splitext(fname)[0].replace("/", "_")

    variants = [
        lambda a: pitch_shift(a, +2),
        lambda a: pitch_shift(a, -2),
        lambda a: time_stretch(a, 0.9),
        lambda a: time_stretch(a, 1.1),
        lambda a: add_noise(a, 0.003),
        lambda a: add_noise(a, 0.008),
        lambda a: add_noise(pitch_shift(a, +2), 0.005),
        lambda a: add_noise(pitch_shift(a, -2), 0.005),
        lambda a: add_noise(time_stretch(a, 0.9), 0.005),
        lambda a: add_noise(time_stretch(a, 1.1), 0.005),
        lambda a: add_noise(time_stretch(pitch_shift(a, +1), 0.95), 0.004),
        lambda a: add_noise(
            time_stretch(
                pitch_shift(a, random.uniform(-2, 2)),
                random.uniform(0.9, 1.1)
            ),
            random.uniform(0.003, 0.01)
        ),
    ]

    for i, aug_fn in enumerate(variants, start=1):
        aug = aug_fn(audio).fade_in(200)
        out_name = f"{base}_aug{i}.wav"
        aug.export(os.path.join(OUTPUT_DIR, out_name), format="wav")
	    #print(f"Augmented: {fname}")

    i += 1
    if i % 10 == 0:
    	print(f"Processing {i}/{total_files}")

end_ns = time.time_ns()

print(f"End time in ns: {end_ns}")
print(f"ns difference: {end_ns - start_ns}")
