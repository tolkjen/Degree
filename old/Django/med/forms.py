# coding=utf-8
from django import forms


class NewClassificationForm(forms.Form):
    name = forms.CharField(max_length=256)
    classifier_name = forms.CharField(max_length=256)
    quant_arg = forms.IntegerField()
    quant_method = forms.CharField(max_length=256)
    k_selection = forms.IntegerField()
    k_count = forms.IntegerField()
    uploaded_file = forms.FileField()
