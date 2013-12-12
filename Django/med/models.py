from django.db import models

class CrossValidation(models.Model):
	name = models.CharField(max_length=64)
	k_groups = models.PositiveIntegerField()
	result = models.FloatField()
	date = models.DateTimeField()
	classifier = models.CharField(max_length=32)
	