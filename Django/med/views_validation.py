from django.shortcuts import render

from med.forms import NewValidationForm

from datafile.sample import Sample
from classification.crossvalidator import KCrossValidator, FakeClassifier

def validate_new(request):
	return render(request, 'med/validate_new.html')

def validate_post(request):
	if request.method == 'POST':
		form = NewValidationForm(request.POST, request.FILES)
		if form.is_valid():
			filepath = form.cleaned_data['uploaded_file'].temporary_file_path()
			group_count = form.cleaned_data['groups']

			sample = Sample.fromXls(filepath)
			validator = KCrossValidator(FakeClassifier(), group_count)
			score = validator.validate(sample.rows())
			return render(request, 'med/validate_result.html', {'result': score})

	return render(request, 'med/validate_new.html')
