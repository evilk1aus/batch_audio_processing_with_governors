import wget
import os
import sys
import tarfile
import zipfile
import shutil

ser_emergency_filename = "speech-emotion-recognition-for-emergency-calls"
affective_meld_filename = "MELD.Raw.tar.gz"

print(">>> Downloading and extracting datasets...")

def download_dataset(*args, **kwargs):
	if os.path.isfile(kwargs['filename']):
		print(f"{kwargs['prettyname']} dataset is already downloaded!")
		return kwargs['filename']

	print(f"{kwargs['prettyname']} dataset is not yet downloaded. Downloading...")

	for i in range(len(args)):
		link = args[i]
		try:
			result_filename = wget.download(link)
			break
		except:
			print(f"Error downloading link: {link}")
			if i < len(args) - 1:
				print("Trying different link...")
			else:
				print(f"Failed to download {kwargs['prettyname']} dataset.")
				sys.exit(-1)

	print(f"\n{kwargs['prettyname']} dataset downloaded: {result_filename}")
	return result_filename

def extract_dataset(**kwargs):
	if os.path.isdir(kwargs["folder_name"]):
		print(f"{kwargs["prettyname"]} dataset is already extracted...")
		return

	print(f"Extracting {kwargs["prettyname"]} dataset...")

	if "is_tar_gz" in kwargs and kwargs["is_tar_gz"]:
		with tarfile.open(kwargs["archive_file"]) as file:
			file.extraction_filter = (lambda x, path: x)
			file.extractall('.')
	else:
		with zipfile.ZipFile(kwargs["archive_file"], 'r') as file:
		    file.extractall(".")

	print(f"{kwargs["prettyname"]} dataset extracted successfully.")

def extract_meld_splits():
	data_info = [
		{ "file": "train.tar.gz", "folder": "train_splits" },
		{ "file": "test.tar.gz", "folder": "output_repeated_splits_test" },
	]
	for n in data_info:
		if not os.path.isdir(f"MELD.Raw/{n["folder"]}"):
			print(f"Extracting MELD.Raw/{n["folder"]}...")
			with tarfile.open(f"MELD.Raw/{n["file"]}") as file:
				file.extraction_filter = (lambda x, path: x)
				file.extractall('./MELD.Raw')
			print(f"Extracted MELD.Raw/{n["folder"]}!")
		else:
			print(f"MELD.Raw/{n["folder"]} already extracted!")

ser_emergency_filename = download_dataset(
				"https://www.kaggle.com/api/v1/datasets/download/anuvagoyal/speech-emotion-recognition-for-emergency-calls",
				prettyname="SER for Emergency Calls", filename="speech-emotion-recognition-for-emergency-calls")

affective_meld_filename = download_dataset(
				"https://huggingface.co/datasets/declare-lab/MELD/resolve/main/MELD.Raw.tar.gz",
				"https://web.eecs.umich.edu/~mihalcea/downloads/MELD.Raw.tar.gz",
				prettyname="Affective-MELD", filename="MELD.Raw.tar.gz")

# ESD Dataset from:
# https://drive.usercontent.google.com/download?id=1scuFwqh8s7KIYAfZW1Eu6088ZAK2SI-v&export=download&authuser=0
esd_filename = download_dataset(
				"https://drive.usercontent.google.com/download?id=1scuFwqh8s7KIYAfZW1Eu6088ZAK2SI-v&export=download&authuser=0&confirm=t&uuid=e18088a1-5fed-4b1a-aaf1-2f6cc4ea7aed&at=APcXIO0cH0vbC5xBNgPCwbbl256G%3A1770783282350",
				prettyname="Emotional Speech", filename="Emotional Speech Dataset (ESD).zip")

extract_dataset(prettyname="SER for Emergency Calls",
				folder_name="CUSTOM_DATASET", archive_file=ser_emergency_filename)
extract_dataset(prettyname="Emotional Speech",
				folder_name="Emotion Speech Dataset", archive_file=esd_filename)
extract_dataset(prettyname="Affective-MELD",
				folder_name="MELD.Raw", archive_file=affective_meld_filename, is_tar_gz=True)

if os.path.isdir("__MACOSX"):
	shutil.rmtree("__MACOSX")

extract_meld_splits()

# Download dataset transcription
if not os.path.isfile("speech_dataset.csv"):
	print("Downloading speech_dataset.csv...")
	wget.download("https://github.com/standing-o/Combined_Dataset_for_Speech_Emotion_Recognition/raw/refs/heads/master/speech_dataset.csv")
print("speech_dataset.csv downloaded!")

print("<<< Downloaded and extracted every dataset.")