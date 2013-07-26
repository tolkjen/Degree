from django.db import models

class TrainData(models.Model):
	name = models.CharField(max_length=64)
	date_started = models.DateTimeField()
	date_finished = models.DateTimeField()
	classifier_state = models.TextField()

class ClassificationResults(models.Model):
	train_data = models.ForeignKey(TrainData)
	name = models.CharField(max_length=64)
	date_started = models.DateTimeField()
	date_finished = models.DateTimeField()
	result_rows = models.TextField()
