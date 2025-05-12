import os
import sys
import glob
import time
import fitz # PyMuPDF
import torch
from gtts import gTTS
from tqdm import tqdm


### setup

# start timer
T0 = time.time()
print(f"[Elapsed time: {time.time()-T0:.3f}s]")

# hyperparameters
OUTPUT_ROOT = '.'


### functions

# type: (str, str, str) -> None
def gtts_txt_to_mp3(text, filename="output.mp3", lang='en'):
	tts = gTTS(text=text, lang=lang)
	tts.save(filename)

# type: (str) -> None
def txt2mp3(path):
	with open(path, 'r') as f:
		print(f"Process: \"{path}\"")
		gtts_txt_to_mp3(f.read(), filename=path+'.mp3')
		print(f"Saved to: \"{filename}\"\a")

# type: (str, str) -> None
def txt2mp3_explore_directory(directory, pattern):
	print(f"In directory \"{directory}\"")
	
	# narrate mp3s
	assert pattern.split('.')[-1] == 'txt', f"Error: \"{pattern}\" did not pass txt check (33)"
	txt_paths = glob.glob(os.path.join(directory, pattern))
	for path in txt_paths:
		txt2mp3(path)
	
	# expand folders
	for path in os.listdir(directory):
		sub_path = os.path.join(directory, path)
		if os.path.isdir(sub_path):
			txt2mp3_explore_directory(sub_path, pattern)


### main

if __name__ == '__main__':
	assert len(sys.argv) >= 3, f"Usage: python3 {os.path.basename(__file__)} <directory> <pattern>"
	txt2mp3_explore_directory(sys.argv[1], sys.argv[2])
