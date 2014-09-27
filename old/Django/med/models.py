from django.db import models
from datetime import datetime
import pytz


class Classification(models.Model):
    name = models.CharField(max_length=256)
    classifier_name = models.CharField(max_length=256)
    quant_method = models.CharField(max_length=256)
    quant_arg = models.PositiveIntegerField()
    k_selection = models.CharField(max_length=256)
    k_count = models.PositiveIntegerField()
    date = models.DateTimeField()
    validation_result = models.FloatField()
    file_name = models.CharField(max_length=256)
    row_count = models.PositiveIntegerField()
    positive_count = models.PositiveIntegerField()

    @staticmethod
    def create(form, validation_result, sample):
        return Classification(
            name=form.cleaned_data['name'],
            classifier_name=form.cleaned_data['classifier_name'],
            quant_method=form.cleaned_data['quant_method'],
            quant_arg=form.cleaned_data['quant_arg'],
            k_selection=form.cleaned_data['k_selection'],
            k_count=form.cleaned_data['k_count'],
            date=datetime.utcnow().replace(tzinfo=pytz.utc),
            validation_result=validation_result,
            file_name=form.cleaned_data['uploaded_file'].name,
            row_count=len(sample.rows()),
            positive_count=sample.positive_count()
        )