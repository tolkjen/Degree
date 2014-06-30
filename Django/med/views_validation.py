# coding=utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from med.forms import NewValidationForm
from med.models import CrossValidation

from utility.crossvalidator import KCrossValidator
from utility.classifier import NaiveClassifier, TreeClassifier, KNNClassifier
from utility.datafile.sample import Sample
from utility.datafile.transform import StringTransform, RangeNumberTransform

def post_method(form_type):
	def wrapper(func):
		def inner(request):
			if request.method == 'POST':
				form = form_type(request.POST, request.FILES)
				if form.is_valid():
					return func(request, form)
				else:
					return render(request, form.get_error_template(), 
						{'form': form, 'error': form.get_error_message()})
			return render(request, form.get_error_template())
		return inner
	return wrapper

def validate_new(request):
	return render(request, 'med/validate_new.html')

@post_method(NewValidationForm)
def validate_post(request, form):
	filepath = form.cleaned_data['uploaded_file'].temporary_file_path()
	group_count = form.cleaned_data['k_groups']

	classifier_mapping = {
		'bayes': NaiveClassifier, 
		'tree': TreeClassifier, 
		'knn': KNNClassifier
	}
	classifier_type = classifier_mapping[ form.cleaned_data['classifier'] ]

	try:
		validator = KCrossValidator(classifier_type, group_count)
		sample = Sample.fromFile(filepath)
		sample.transform_attributes(StringTransform(), RangeNumberTransform(group_count))
		score = validator.validate(sample.rows())

		cross_validation = CrossValidation.create(form, score)
		cross_validation.save()
	except Exception, e:
		return render(request, 'med/validate_new.html', {'error': e})

	return HttpResponseRedirect(reverse('med:validate_list'))

def validate_list(request):
	def change_classifier_name(validation):
		mapping = {
			'tree': 'Drzewo decyzyjne', 
			'bayes': 'Naiwny Bayesowski',
			'knn': 'Najbliższy sąsiad'
		}
		validation.classifier = mapping[ validation.classifier ]
		return validation

	validations = CrossValidation.objects.order_by('-date')
	return render(request, 'med/validate_list.html', 
		{'validations': map(change_classifier_name, validations)}
	)

def validate_delete(request, id):
	validation = get_object_or_404(CrossValidation, pk=id)
	validation.delete()
	return HttpResponseRedirect(reverse('med:validate_list'))
