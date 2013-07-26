from django import forms

class NewTrainDataForm(forms.Form):
    name = forms.CharField(max_length=64)
    uploaded_file  = forms.FileField()

class NewClassificationForm(forms.Form):
	name = forms.CharField(max_length=64)
	uploaded_file  = forms.FileField()
