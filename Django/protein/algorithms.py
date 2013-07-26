# coding=utf-8

import string
from libcodon import get_codons
	
def translate_uploaded_file(uploaded_file):
	data = ''.join(uploaded_file.read().split()).lower()
	
	if len(data) % 3 != 0:
		raise Exception, 'Długość sekwencji niepodzielna przez 3!'
	
	return get_codons(data)
