from django import forms

class NewClassifierDataForm(forms.Form):
    name = forms.CharField(max_length=64)
    uploaded_file  = forms.FileField()
    levels = forms.IntegerField()

class NewClassificationForm(forms.Form):
	name = forms.CharField(max_length=64)
	uploaded_file  = forms.FileField()
