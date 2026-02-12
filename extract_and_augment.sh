#!/bin/bash

start=$(date +%s)

echo Extracting from kaggle dataset 
python3 help_extract_kaggle.py
echo Extracting from meld dataset
python3 help_extract_meld.py
echo Extracting from esd dataset
python3 help_extract_esd.py
echo Starting to augment dataset
python3 augmentation.py

end=$(date +%s)
echo "Elapsed: $((end - start)) seconds" > extract_and_augment_time.log
