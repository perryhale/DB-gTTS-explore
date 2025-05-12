import os
import sys
import glob
import time
import fitz # PyMuPDF
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


### setup

# start timer
T0 = time.time()
print(f"[Elapsed time: {time.time()-T0:.3f}s]")

# hyperparameters
MODEL = 'sshleifer/distilbart-cnn-12-6'
MAX_TOKENS = 1024 # model dependent
BATCH_SIZE = 1 # hardware dependent
SUMMARY_DEPTH = 2 # use dependent
SUMMARY_MAX = 512 # use dependent
SUMMARY_MIN = 32 # use dependent
OUTPUT_ROOT = '.' # untested


### functions

# type: (str) -> str
def extract_txt_from_pdf(pdf_path):
	
	# join all pages of text with space characters
	doc = fitz.open(pdf_path)
	text = ' '.join([page.get_text() for page in doc]).strip()
	
	return text

# type: (str, AutoTokenizer, int) -> list[str]
def split_txt(text, tokenizer, max_tokens=MAX_TOKENS):
	
	# tokenize, slice by max_tokens, detokenize
	input_ids = tokenizer(text, return_tensors='pt', truncation=False)['input_ids'][0]
	text_chunks = [input_ids[i:i+max_tokens] for i in range(0, len(input_ids), max_tokens)]
	text_chunks = [tokenizer.decode(chunk_ids, skip_special_tokens=True) for chunk_ids in text_chunks]
	
	return text_chunks

# type: (list[str], AutoTokenizer, AutoModelForSeq2SeqLM, int) -> str
def summarize_txt_chunks(text_chunks, tokenizer, model, batch_size=BATCH_SIZE):
	
	# initialise
	summaries = []
	device = model.device
	
	# decode summaries
	for i in tqdm(range(0, len(text_chunks), batch_size)):
		
		# batch
		batch_chunks = text_chunks[i:i+batch_size]
		
		# tokenize input
		inputs = tokenizer(batch_chunks, return_tensors='pt', padding=True, truncation=True)
		input_ids = inputs['input_ids'].to(device)
		attention_mask = inputs['attention_mask'].to(device)
		
		# generate summary
		summary_ids = model.generate(
			input_ids,
			attention_mask=attention_mask,
			max_length=SUMMARY_MAX,
			min_length=SUMMARY_MIN,
			do_sample=False,
		)
		
		# detokenize output
		batch_summaries = tokenizer.batch_decode(summary_ids, skip_special_tokens=True)
		summaries.extend(batch_summaries)
	
	# finalise summary
	summary = '\n'.join(summaries)
	
	return summary

# type: (str, AutoTokenizer, AutoModelForSeq2SeqLM) -> str
def summarize_txt(text, tokenizer, model):
	text_chunks = split_txt(text, tokenizer)
	summary = summarize_txt_chunks(text_chunks, tokenizer, model)
	return summary

# type: (str, str) -> None
def save_txt(text, output_path):
	try:
		with open(output_path, 'w', encoding='utf-8') as f:
			f.write(text)
		print(f"Text saved to: {output_path}")
	except Exception as e:
		print(f"Error writing to file: \"{output_path}\"]")
		print(e)

# type: (str, AutoTokenizer, AutoModelForSeq2SeqLM, int, str) -> None
def summarize_pdf_glob(pattern, tokenizer, model, max_depth=SUMMARY_DEPTH, output_root=OUTPUT_ROOT):
	
	# read paths from glob
	pdf_paths = glob.glob(pattern)
	print(f"Found paths: {pdf_paths}")
	
	# process files
	for path in pdf_paths:
		
		# trace
		print(f"Processing: \"{path}\"")
		if not os.path.isfile(path):
			print(f"Skipping non-file: \"{path}\"")
			continue
		
		# extract text
		text = extract_txt_from_pdf(path)#[:1024] ###! debug
		
		# iterate summarization
		summary = text
		for i in range(max_depth):
			
			# summarize and format
			summary = summarize_txt(summary, tokenizer, model)
			summary_formatted = summary.strip().replace(' .','.').replace('\n ','\n')
			
			# trace
			print(f"\n=== SUMMARY ===")
			print(f"path=\"{path}\", depth={i+1}\n")
			print(summary_formatted)
			save_txt(summary_formatted, f"{output_root}/{path.replace('.pdf', '')}.sd{i+1}.txt")
			print(f"[Elapsed time: {time.time()-T0:.3f}s]")

# type: (str, AutoTokenizer, AutoModelForSeq2SeqLM) -> None
def explore_directory(directory, tokenizer, model):
	
	# sumarize pdfs
	print(f"[In directory {directory}]")
	summarize_pdf_glob(os.path.join(directory, '*.pdf'), tokenizer, model)
	
	# expand folders
	for filename in os.listdir(directory):
		sub_path = os.path.join(directory, filename)
		if os.path.isdir(sub_path):
			explore_directory(sub_path, tokenizer, model)


### main

if __name__ == '__main__':
	tokenizer = AutoTokenizer.from_pretrained(MODEL)
	model = AutoModelForSeq2SeqLM.from_pretrained(MODEL).to('cuda' if torch.cuda.is_available() else 'cpu')
	explore_directory('.' if len(sys.argv) < 2 else sys.argv[1], tokenizer, model)
