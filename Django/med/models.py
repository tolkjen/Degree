from django.db import models

class ClassifierData(models.Model):
	name = models.CharField(max_length=64)
	date_started = models.DateTimeField()
	date_finished = models.DateTimeField()
	classifier_state = models.TextField()
	descrete_levels = models.PositiveIntegerField()

class ClassificationResults(models.Model):
	classifier_data = models.ForeignKey(ClassifierData)
	name = models.CharField(max_length=64)
	date_started = models.DateTimeField()
	date_finished = models.DateTimeField()
	result_rows = models.TextField()

class CrossValidation(models.Model):
	name = models.CharField(max_length=64)
	k_groups = models.PositiveIntegerField()
	result = models.FloatField()
	date = models.DateTimeField()
