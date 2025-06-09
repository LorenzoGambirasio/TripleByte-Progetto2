from django import forms
from .models import Ricovero, Patologia

class RicoveroForm(forms.ModelForm):
    patologie = forms.ModelMultipleChoiceField(
        queryset=Patologia.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Ricovero
        fields = ['CSSN', 'codOspedale', 'data_ingresso', 'durata', 'stato', 'motivo', 'costo']
        widgets = {
            'data_ingresso': forms.DateInput(attrs={'type': 'date'}),
        }
