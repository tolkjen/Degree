from django import forms

class NewValidationForm(forms.Form):
	name = forms.CharField(max_length=64)
	uploaded_file  = forms.FileField()
	k_groups = forms.IntegerField()
	classifier = forms.CharField(max_length=32)
