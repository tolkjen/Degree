from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse

from forms import UploadFileForm
from algorithms import translate_uploaded_file

import random
import os.path

def index(request):
	return HttpResponse('Hello to skeleton site')
	
def upload(request):
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			try:
				data = translate_uploaded_file(request.FILES['uploaded_file'])
			except Exception, e:
				return render(request, 'protein/upload.html', { 'form': form, 'error' : e })
			return render(request, 'protein/results.html', { 'data': data })
	else:
		form = UploadFileForm()
		
	return render(request, 'protein/upload.html', { 'form': form })
