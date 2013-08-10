# coding=utf-8

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.cache import patch_cache_control

from datetime import datetime

from med.models import TrainData, ClassificationResults
from med.forms import NewTrainDataForm, NewClassificationForm

import classifier

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

# Trained classifiers views

@no_browser_cache
def trained_list(request):
	trained = TrainData.objects.all()
	if 'trained_list_error' in request.session:
		error = request.session['trained_list_error']
		del request.session['trained_list_error']
		return render(request, 'med/trained_list.html', {'trained': trained, 'error': error})
	print "trained list size: %d" % len(trained)
	return render(request, 'med/trained_list.html', {'trained': trained})

def trained_list_new(request):
	if request.method == 'POST':
		form = NewTrainDataForm(request.POST, request.FILES)
		if form.is_valid():
			try:
				traindata = create_train_data(form)
				traindata.save()
				return HttpResponseRedirect(reverse('med:trained_list'))
			except Exception, e:
				return render(request, 'med/trained_list_new.html', {'form': form, 'error': e})
		else:
			error = "Proszę wybrać nazwę oraz plik z danymi uczącymi!"
			return render(request, 'med/trained_list_new.html', {'form': form, 'error': error})
	return render(request, 'med/trained_list_new.html')

def trained_list_delete(request, id):
	classifications = ClassificationResults.objects.filter(train_data__id=id)
	if len(classifications) > 0:
		error = "Przed usunięciem wybranego klasyfikatora należy usunąć wszystkie wyniki klasyfikacji z nim związane."
		request.session['trained_list_error'] = error
	else:
		trained = get_object_or_404(TrainData, pk=id)
		trained.delete()
	return HttpResponseRedirect(reverse('med:trained_list'))

# Classification results views

@no_browser_cache
def cls_list(request):
	results = ClassificationResults.objects.all()
	print "cls_list: %d" % len(results)
	return render(request, 'med/cls_list.html', {'cls_list': results})

@no_browser_cache
def cls_list_new(request):
	trained = TrainData.objects.all()
	print "cls_list_new: %d" % len(trained)
	return render(request, 'med/cls_list_new.html', {'trained': trained})

def cls_list_new_form(request, id):
	model = get_object_or_404(TrainData, pk=id)

	if request.method == 'POST':
		form = NewClassificationForm(request.POST, request.FILES)
		if form.is_valid():
			try:
				classification = create_classfication(form, model)
				classification.save()
				return HttpResponseRedirect(reverse('med:cls_list'))
			except Exception, e:
				return render(request, 'med/cls_list_new_form.html', {'model': model, 'id': id, 'error': e})
		else:
			error = "Proszę wybrać nazwę oraz plik z danymi do klasyfikacji!"
			return render(request, 'med/cls_list_new_form.html', {'model': model, 'id': id, 'error': error})
	else:
		request.session['train_data_id'] = id

	return render(request, 'med/cls_list_new_form.html', {'model': model, 'id': id})

def cls_list_preview(request, id):
	classification = get_object_or_404(ClassificationResults, pk=id)
	rows = get_classification_rows(classification)
	return render(request, 'med/cls_list_preview.html', {
		'results': classification,
		'rows' : rows,
	})

def cls_list_delete(request, id):
	classification = get_object_or_404(ClassificationResults, pk=id)
	classification.delete()
	return HttpResponseRedirect(reverse('med:cls_list'))

# Helper methods

def get_classification_rows(classification):
	example_data = classifier.TrainingDataVector()
	example_data.deserialize(classification.result_rows.encode('iso8859_2', 'ignore'))
	return example_data.to_list()

def create_classfication(form, data):
	train_data = data
	name = form.cleaned_data['name']
	date_started = datetime.now()
	date_finished = datetime.now()

	reader = classifier.TemporaryReader()
	filepath = form.cleaned_data['uploaded_file'].temporary_file_path()
	test_data = reader.readTestData(filepath)

	nc = classifier.NaiveClassifier()
	encoded_state = data.classifier_state.encode('iso8859_2', 'ignore')
	nc.deserialize(encoded_state)
	result_rows = nc.getCategories(test_data).serialize()

	return ClassificationResults(
		name=name,
		date_started=date_started,
		date_finished=date_finished,
		result_rows=result_rows,
		train_data=train_data
	)

def create_train_data(form):
	name = form.cleaned_data['name']
	date_started = datetime.now()
	date_finished = datetime.now()

	reader = classifier.TemporaryReader()
	filepath = form.cleaned_data['uploaded_file'].temporary_file_path()
	training_data = reader.readTrainingData(filepath)

	nc = classifier.NaiveClassifier()
	nc.train(training_data)
	state = nc.serialize()

	return TrainData(
		name=name, 
		date_started=date_started, 
		date_finished=date_finished, 
		classifier_state=state
	)
