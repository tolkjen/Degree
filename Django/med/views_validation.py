# coding=utf-8

from django.shortcuts import render

from med.forms import NewValidationForm

from classifier import SuperClassifier

from datafile.sample import Sample
from datafile.transform import StringTransform, RangeNumberTransform
from classification.crossvalidator import KCrossValidator, FakeClassifier

def validate_new(request):
	return render(request, 'med/validate_new.html')

def validate_post(request):
	if request.method == 'POST':
		form = NewValidationForm(request.POST, request.FILES)
		if form.is_valid():
			filepath = form.cleaned_data['uploaded_file'].temporary_file_path()
			group_count = form.cleaned_data['groups']

			try:
				sample = Sample.fromFile(filepath)
				sample.transform_attributes(StringTransform(), RangeNumberTransform(group_count))
			except Exception, e:
				return render(request, 'med/validate_new.html', {'error': e})

			validator = KCrossValidator(SuperClassifier(), group_count)
			score = validator.validate(sample.rows())
			return render(request, 'med/validate_result.html', {'result': score})
		else:
			error = 'Proszę wybrać liczbę podzbiorów uczących oraz wskazać plik z danymi.'
			return render(request, 'med/validate_new.html', {'form': form, 'error': error})

	return render(request, 'med/validate_new.html')
