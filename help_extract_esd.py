import logging

logging.getLogger("whisperx.asr").setLevel(logging.ERROR)
logging.getLogger("whisperx.vads").setLevel(logging.ERROR)
logging.getLogger("whisperx").setLevel(logging.ERROR)
logging.getLogger("pyannote").setLevel(logging.ERROR)
logging.getLogger("pytorch_lightning").setLevel(logging.ERROR)
logging.getLogger("lightning").setLevel(logging.ERROR)
logging.getLogger("torch").setLevel(logging.ERROR)

import torch
import whisperx
import numpy as np
import pprint
import os
import glob
from pydub import AudioSegment
import pandas as pd
import time
import subprocess
from custom_print import *

model_name = "small"
device = "cpu"

no_help = []

custom_print("Loading whisperx model...")

asr_model = whisperx.load_model(model_name, device=device, compute_type="int8")

custom_print("Loading align model...")

align_model, metadata = whisperx.load_align_model(language_code="en", device=device)

custom_print("Loaded all models.")

from audio_util import find_start_energy

def recognize_audio(filepath):
    filepath_original = filepath.replace("\\", "/")
    filepath = filepath_original.replace("./dataset/esd", "./Emotion Speech Dataset")

    audio_file = os.path.abspath(filepath)
    result = asr_model.transcribe(audio_file)

    result_aligned = whisperx.align(
        result["segments"],
        align_model,
        metadata,
        audio_file,
        device
    )

    has_exported = False
    help_count = 1
    for word_info in result_aligned['word_segments']:
        if not word_info['word'].startswith("help"):
            continue

        newpath = filepath_original.replace("./dataset/esd", "help_dataset/esd").replace(".wav", f"_{help_count}.wav")

        help_count += 1

        os.makedirs(os.path.dirname(newpath), exist_ok=True)
        old_audio = AudioSegment.from_wav(os.path.abspath(filepath))

        start_ms = int(find_start_energy(old_audio, word_info['start']) * 1000)
        end_ms = int(word_info['end'] * 1000)

        word_audio = old_audio[start_ms:end_ms]

        # Save to file
        word_audio.export(os.path.abspath(newpath), format="wav")
        has_exported = True

    if not has_exported:
        print(f"Warning: {filepath} has not exported 'help' wav sample.")
        no_help.append(filepath)

custom_print("Reading help_dataset.csv")

data_paths = pd.read_csv('help_dataset.csv')
data_paths = data_paths[data_paths['Dataset'] == 'ESD']
data_paths = data_paths["Filepath"].tolist()

custom_print(str(f"Starting to Process {len(data_paths)} files"))

i = 0
for file in data_paths:
    if i % 3 == 0:
        custom_print(f"Processing files: {i+1}/{len(data_paths)}")
        #break
    recognize_audio(file)
    i += 1

with open("esd_missing_help.log", "w", encoding="utf-8") as f:
    for file in no_help:
        f.write(str(file))
        f.write("\n")