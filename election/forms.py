from django import forms
from .models import Election, Voter


class NonSuperuserElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        exclude = ['creator']


class NonSuperUserVoterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if not request:
            raise ValueError('Request parameter missing')
        super().__init__(*args, **kwargs)
        if request.user.is_superuser:
            return
        self.fields['election'].queryset = Election.objects.filter(creator=request.user)

    class Meta:
        model = Voter
        fields = '__all__'
