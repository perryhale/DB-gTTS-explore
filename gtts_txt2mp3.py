import sys
from gtts import gTTS


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

### main

if __name__ == '__main__':
	txt2mp3(sys.argv[1])
