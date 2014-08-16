from django.db import models
from datetime import datetime
import pytz

class CrossValidation(models.Model):
	name = models.CharField(max_length=64)
	k_groups = models.PositiveIntegerField()
	domain_subgroups = models.PositiveIntegerField()
	result = models.FloatField()
	date = models.DateTimeField()
	classifier = models.CharField(max_length=32)
	
	@staticmethod
	def create(form, result):
		return CrossValidation(
			name = form.cleaned_data['name'],
			k_groups = form.cleaned_data['k_groups'],
			domain_subgroups = form.cleaned_data['domain_subgroups'],
			result = result,
			date = datetime.utcnow().replace(tzinfo = pytz.utc),
			classifier = form.cleaned_data['classifier']
		)

class Classification(models.Model):
	name = models.CharField(max_length=256)
	classifier_name = models.CharField(max_length=256)
	subset_count = models.PositiveIntegerField()
	k_selection = models.CharField(max_length=256)
	k_count = models.PositiveIntegerField()
	date = models.DateTimeField()
	validation_result = models.FloatField()
	file_name = models.CharField(max_length=256)
	row_count = models.PositiveIntegerField()
	positive_percentage = models.FloatField()

	@staticmethod
	def create(form, validation_result, row_count, positive_percentage):
		return Classification(
			name = form.cleaned_data['name'],
			classifier_name = form.cleaned_data['classifier_name'],
			subset_count = form.cleaned_data['quant_arg'],
			k_selection = form.cleaned_data['k_selection'],
			k_count = form.cleaned_data['k_count'],
			date = datetime.utcnow().replace(tzinfo = pytz.utc),
			validation_result = validation_result,
			file_name = form.cleaned_data['uploaded_file'].name,
			row_count = row_count,
			positive_percentage = positive_percentage
		)