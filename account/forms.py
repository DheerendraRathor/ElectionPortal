from django import forms


class VoterLoginForm(forms.Form):
    username = forms.CharField(max_length=64, min_length=1)
    password = forms.CharField(widget=forms.PasswordInput())