import os
import sys
import time
import glob
from gtts import gTTS


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

# type: (str, str) -> None
def txt2mp3(path, output_root=OUTPUT_ROOT):
	with open(path, 'r') as f:
		print(f"Process: \"{path}\"")
		out_path = os.path.join(output_root, f'{path}.mp3')
		gtts_txt_to_mp3(f.read(), filename=out_path)
		print(f"Saved to: \"{out_path}\"\a")
		print(f"[Elapsed time: {time.time()-T0:.3f}s]")

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
