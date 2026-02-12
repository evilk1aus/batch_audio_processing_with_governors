import pandas as pd

print("Extracting speech dataset that contain the word 'help'...")

data = pd.read_csv('speech_dataset.csv', low_memory=False)
data = data[data['Text'].str.contains("help", case=False, na=False)]
data.to_csv("help_dataset.csv", index=False)

print("Extracted!")
