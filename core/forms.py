from typing import override
from urllib import request
from django import  forms
from .models import Application

class CustomerApplicationForm(forms.ModelForm):

    amount = forms.IntegerField(label="Amount")
    duration_months = forms.IntegerField(label="Duration")
    application_type = forms.ChoiceField(label="Application Type", choices=[("loan", "Loan")])

    class Meta:
        model = Application
        fields = ['user', 'amount', 'duration_months', 'application_type',]
        widgets = {'user': forms.HiddenInput()}
        
    

class ProviderApplicationForm(forms.ModelForm):
    amount = forms.IntegerField(label="Amount")
    duration_months = forms.IntegerField(label="Duration")
    application_type = forms.ChoiceField(label="Application Type", choices=[("deposit", "Deposit")])

    class Meta:
        model = Application
        fields = ['user', 'amount', 'duration_months', 'application_type']
        widgets = {'user': forms.HiddenInput()}

class ApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = Application
        exclude = ('created_at', 'reviewed_at')
        widgets = {'reviewed_by': forms.HiddenInput()}