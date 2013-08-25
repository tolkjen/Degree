# coding=utf-8

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.cache import patch_cache_control

from datetime import datetime

from med.models import ClassifierData, ClassificationResults
from med.forms import NewClassifierDataForm, NewClassificationForm

from classifier import TrainingDataVector
from classification import Classifier

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
	trained = ClassifierData.objects.all()
	if 'trained_list_error' in request.session:
		error = request.session['trained_list_error']
		del request.session['trained_list_error']
		return render(request, 'med/trained_list.html', {'trained': trained, 'error': error})
	print "trained list size: %d" % len(trained)
	return render(request, 'med/trained_list.html', {'trained': trained})

def trained_list_new(request):
	if request.method == 'POST':
		form = NewClassifierDataForm(request.POST, request.FILES)
		if form.is_valid():
			try:
				cls_data = create_classifier_data(form)
				cls_data.save()
				return HttpResponseRedirect(reverse('med:trained_list'))
			except Exception, e:
				return render(request, 'med/trained_list_new.html', {'form': form, 'error': e})
		else:
			error = "Proszę wybrać nazwę oraz plik z danymi uczącymi!"
			return render(request, 'med/trained_list_new.html', {'form': form, 'error': error})
	return render(request, 'med/trained_list_new.html')

def trained_list_delete(request, id):
	classifications = ClassificationResults.objects.filter(classifier_data__id=id)
	if len(classifications) > 0:
		error = "Przed usunięciem wybranego klasyfikatora należy usunąć wszystkie wyniki klasyfikacji z nim związane."
		request.session['trained_list_error'] = error
	else:
		trained = get_object_or_404(ClassifierData, pk=id)
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
	trained = ClassifierData.objects.all()
	print "cls_list_new: %d" % len(trained)
	return render(request, 'med/cls_list_new.html', {'trained': trained})

def cls_list_new_form(request, id):
	model = get_object_or_404(ClassifierData, pk=id)

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
		request.session['classifier_data_id'] = id

	return render(request, 'med/cls_list_new_form.html', {'model': model, 'id': id})

def cls_list_preview(request, id):
	classification = get_object_or_404(ClassificationResults, pk=id)
	rows = get_classification_rows(classification)

	return render(request, 'med/cls_list_preview.html', {
		'attributes' : ['Str', 'Dex', 'Int'],
		'category' : 'Class',
		'results': classification,
		'rows' : rows,
	})

def cls_list_delete(request, id):
	classification = get_object_or_404(ClassificationResults, pk=id)
	classification.delete()
	return HttpResponseRedirect(reverse('med:cls_list'))

# Helper methods

def get_classification_rows(classification):
	example_data = TrainingDataVector()
	example_data.deserialize(classification.result_rows.encode('iso8859_2', 'ignore'))
	return example_data.to_list()

def create_classfication(form, data):
	classifier_data = data
	name = form.cleaned_data['name']
	date_started = datetime.now()

	filepath = form.cleaned_data['uploaded_file'].temporary_file_path()
	encoded_state = data.classifier_state.encode('iso8859_2', 'ignore')

	cl = Classifier()
	cl.deserialize(encoded_state)
	result_rows = cl.get_categories(filepath).serialize()
	date_finished = datetime.now()

	return ClassificationResults(
		name=name,
		date_started=date_started,
		date_finished=date_finished,
		result_rows=result_rows,
		classifier_data=classifier_data
	)

def create_classifier_data(form):
	date_started = datetime.now()

	filepath = form.cleaned_data['uploaded_file'].temporary_file_path()
	levels = form.cleaned_data['levels']

	cl = Classifier(3)
	cl.train(filepath, levels)
	state = cl.serialize()

	return ClassifierData(
		name=form.cleaned_data['name'], 
		date_started=date_started, 
		date_finished=datetime.now(), 
		classifier_state=state,
		descrete_levels=levels
	)
