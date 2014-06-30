# coding=utf-8

from django import forms

class NewValidationForm(forms.Form):
	name = forms.CharField(max_length=64)
	uploaded_file  = forms.FileField()
	k_groups = forms.IntegerField()
	domain_subgroups = forms.IntegerField()
	classifier = forms.CharField(max_length=32)

	@staticmethod
	def get_error_message():
		return 'Proszę uzupełnić nazwę, wybrać liczbę podzbiorów uczących oraz wskazać plik z danymi.'

	@staticmethod
	def get_error_template():
		return 'med/validate_new.html'
