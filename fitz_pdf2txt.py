import sys
import fitz
doc = fitz.open(sys.argv[1])
text = ' '.join([page.get_text() for page in doc]).strip()
print(text) # use pipe
