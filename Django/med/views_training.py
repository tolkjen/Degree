# coding=utf-8

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from med.forms import NewClassifierDataForm
from med.models import ClassifierData, ClassificationResults

def trained_list(request):
	trained = ClassifierData.objects.all()
	if 'trained_list_error' in request.session:
		error = request.session['trained_list_error']
		del request.session['trained_list_error']
		return render(request, 'med/trained_list.html', {'trained': trained, 'error': error})
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