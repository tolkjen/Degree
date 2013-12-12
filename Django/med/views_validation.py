# coding=utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from datetime import datetime

from med.forms import NewValidationForm
from med.models import CrossValidation

from classifier import NaiveClassifier, TreeClassifier, KNNClassifier

from datafile.sample import Sample
from datafile.transform import StringTransform, RangeNumberTransform
from classification.crossvalidator import KCrossValidator

def validate_new(request):
	return render(request, 'med/validate_new.html')

def validate_post(request):
	if request.method == 'POST':
		form = NewValidationForm(request.POST, request.FILES)
		if form.is_valid():
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

				cross_valid = create_cross_validation(form, score)
				cross_valid.save()
			except Exception, e:
				return render(request, 'med/validate_new.html', {'error': e})

			return HttpResponseRedirect(reverse('med:validate_list'))
		else:
			error = 'Proszę uzupełnić nazwę, wybrać liczbę podzbiorów uczących oraz wskazać plik z danymi.'
			return render(request, 'med/validate_new.html', {'form': form, 'error': error})

	return render(request, 'med/validate_new.html')

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

def create_cross_validation(form, result):
	return CrossValidation(
		name = form.cleaned_data['name'],
		k_groups = form.cleaned_data['k_groups'],
		result = result,
		date = datetime.now(),
		classifier = form.cleaned_data['classifier']
	)