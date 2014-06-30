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