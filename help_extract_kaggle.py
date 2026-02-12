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
    audio_file = os.path.abspath(filepath)
    result = asr_model.transcribe(audio_file)

    result_aligned = whisperx.align(
        result["segments"],
        align_model,
        metadata,
        audio_file,
        device
    )

    for word_info in result_aligned['word_segments']:
        if not word_info['word'].startswith("help"):
            continue
        newpath = f"help_dataset/{filepath[2:]}"
        os.makedirs(os.path.dirname(newpath), exist_ok=True)
        old_audio = AudioSegment.from_wav(os.path.abspath(filepath))

        start_ms = int(find_start_energy(old_audio, word_info['start']) * 1000)
        end_ms = int(word_info['end'] * 1000)

        word_audio = old_audio[start_ms:end_ms]

        # Save to file
        word_audio.export(os.path.abspath(newpath), format="wav")

def keep_help_recordings(filepath):
    spl = filepath.split("_")
    # EmotionNumber_ SentenceNumber_Gender _Synthetic/Natural_SpeakerNumber
    # Keep: 04 – This place is on fire. Please send help.
    return spl[2] == "04"

custom_print("Reading help_dataset.csv")

folder_path = "./CUSTOM_DATASET"
all_files = glob.glob(folder_path + "/**/*", recursive=True)
all_files = [f for f in all_files if os.path.isfile(f)]
all_files = list(filter(keep_help_recordings, all_files))

custom_print(str(f"Starting to Process {len(all_files)} files"))
i = 0
for file in all_files:
    if i % 3 == 0:
        custom_print(f"Processing files: {i+1}/{len(all_files)}")
        #break
    recognize_audio(file)
    i += 1
