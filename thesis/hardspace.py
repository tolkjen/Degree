import re
import sys

words = ['i', 'a', 'u', 'w']
for filename in sys.argv[1:]:
  with open(filename, 'r') as f:
    text = f.read()
  for word in words:
    text = re.sub(' '+word+' ', ' '+word+'~', text)
  with open(filename, 'w') as f:
    f.write(text)
