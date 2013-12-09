# coding=utf-8

from django.shortcuts import render
from django.utils.cache import patch_cache_control

from views_validation import *
from views_training import *
from views_classification import *

# Decorators

class no_browser_cache(object):
	def __init__(self, func):
		self.func = func

	def __call__(self, *args):
		response = self.func(*args)
		response["Cache-Control"] = "no-cache, no-store, must-revalidate"
		return response

# Index page view

def index(request):
	return render(request, 'med/index.html')
