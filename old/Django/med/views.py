# coding=utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from med.forms import NewClassificationForm
from med.models import Classification

from utility.crossvalidator import KCrossValidator
from utility.datafile.sample import Sample
from utility.datafile.transform import NumberTransformHelper, StandardDeviationFilter
import utility.classifierhelper as classifierhelper


def index(request):
    return HttpResponseRedirect(reverse('med:classification_list', kwargs={'sortby': 'date'}))


def classification_new(request):
    return render(request, 'med/classification_new.html', {
        'classifier_type_names': classifierhelper.get_type_names(),
        'transform_type_names': NumberTransformHelper.get_type_names(),
        'form': NewClassificationForm()
    })


def classification_create(request):
    if request.method == 'POST':
        form = NewClassificationForm(request.POST, request.FILES)
        if form.is_valid():
            filepath = form.cleaned_data['uploaded_file'].temporary_file_path()
            try:
                classifier_type = classifierhelper.get_classifier_type(form.cleaned_data['classifier_name'])
                validator = KCrossValidator(classifier_type, form.cleaned_data['k_count'],
                                            form.cleaned_data['k_selection'])
                sample = Sample.fromFile(filepath)
                number_transform = NumberTransformHelper.create_transform(
                    form.cleaned_data['quant_method'], form.cleaned_data['quant_arg'])
                sample.transform_attributes(number_transform)
                score = validator.validate(sample.rows())

                classification = Classification.create(form, score, sample)
                classification.save()

            except Exception, e:
                return render(request, 'med/classification_new.html', {
                    'form': form,
                    'error': e,
                    'transform_type_names': NumberTransformHelper.get_type_names(),
                    'classifier_type_names': classifierhelper.get_type_names()
                })

            return HttpResponseRedirect(reverse('med:classification_list', kwargs={'sortby': 'date'}))

    else:
        form = NewClassificationForm()

    return render(request, 'med/classification_new.html', {
        'form': form,
        'transform_type_names': NumberTransformHelper.get_type_names(),
        'classifier_type_names': classifierhelper.get_type_names()
    })


def classification_list(request, sortby):
    sortby_items = {"date": "Wg daty wykonania", "name": "Wg nazwy klasyfikacji",
                    "validation_result": "Wg wyniku klasyfikacji"}

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
    positive_percentage = round(
        100.0 * float(classification.positive_count) / classification.row_count, 2)
    classification.validation_result = round(classification.validation_result, 4)

    k_selection_description = {"0": "Sąsiednie przedziały", "1": "Losowy"}
    if classification.k_selection in k_selection_description.keys():
        k_description = k_selection_description[classification.k_selection]
    else:
        k_description = "????"

    return render(request, 'med/classification_details.html',
                  dict(classification=classification, sortby=sortby, description=k_description,
                       positive_percentage=positive_percentage))