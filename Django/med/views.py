# coding=utf-8

from django.shortcuts import render
from django.utils.cache import patch_cache_control
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from med.forms import NewValidationForm, NewClassificationForm
from med.models import CrossValidation, Classification

from utility.crossvalidator import KCrossValidator
from utility.classifierhelper import ClassifierHelper
from utility.datafile.sample import Sample
from utility.datafile.transform import StringTransform, RangeNumberTransform

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
	return HttpResponseRedirect(reverse('med:classification_list', kwargs={'sortby': 'date'}))

def classification_new(request):
	type_names = ClassifierHelper.get_type_names()
	return render(request, 'med/classification_new.html', {'type_names': type_names})

def classification_create(request):
	if request.method == 'POST':
		form = NewClassificationForm(request.POST, request.FILES)
		if form.is_valid():
			filepath = form.cleaned_data['uploaded_file'].temporary_file_path()
			try:
				classifier_type = ClassifierHelper.get_classifier_type(form.cleaned_data['classifier_name'])
				validator = KCrossValidator(classifier_type, form.cleaned_data['k_count'], form.cleaned_data['k_selection'])
				sample = Sample.fromFile(filepath)
				sample.transform_attributes(StringTransform(), RangeNumberTransform(form.cleaned_data['subset_count']))
				score = validator.validate(sample.rows())

				positive_percentage = 100 * float(sample.positive_count()) / len(sample.rows())
				classification = Classification.create(form, score, len(sample.rows()), positive_percentage)
				classification.save()

			except Exception, e:
				return render(request, 'med/classification_new.html', 
					{'error': e, 'type_names': ClassifierHelper.get_type_names()})
			return HttpResponseRedirect(reverse('med:classification_list', kwargs={'sortby': 'date'}))
		else:
			return render(request, form.get_error_template(), {'form': form, 'error': form.get_error_message(), 
				'type_names': ClassifierHelper.get_type_names()})
	return render(request, form.get_error_template())

def classification_list(request, sortby):
	sortby_items = {"date": "Wg daty wykonania", "name": "Wg nazwy klasyfikacji", "validation_result": "Wg wyniku klasyfikacji"}

	if not sortby in sortby_items.keys():
		sortby = sortby.keys()[0]
	classifications = Classification.objects.order_by('-' + sortby)
	for item in classifications:
		item.validation_result = round(item.validation_result, 4)

	return render(request, 'med/classification_list.html', 
		{'classifications': classifications, 'sortby': sortby, 'sortby_items': sortby_items})

def classification_delete(request, id, sortby):
	classification = get_object_or_404(Classification, pk=id)
	classification.delete()
	return HttpResponseRedirect(reverse('med:classification_list', kwargs={'sortby': sortby}))

def classification_details(request, id, sortby):
	classification = get_object_or_404(Classification, pk=id)
	classification.positive_percentage = round(classification.positive_percentage, 2)
	classification.validation_result = round(classification.validation_result, 4)

	k_selection_description = {"0": "Sąsiednie przedziały", "1": "Losowy"}
	if classification.k_selection in k_selection_description.keys():
		k_description = k_selection_description[classification.k_selection]
	else:
		k_description = "????"

	return render(request, 'med/classification_details.html', 
		{'classification': classification, 'sortby': sortby, 'description': k_description})
