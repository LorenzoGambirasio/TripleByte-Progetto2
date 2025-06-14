from django import forms
from .models import Ricovero, Patologia, Cittadino

class RicoveroForm(forms.ModelForm):
    CSSN = forms.ModelChoiceField(
        queryset=Cittadino.objects.all().order_by('cognome', 'nome'),
        label="CSSN",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_cittadino'}),
        to_field_name="CSSN"
    )

    patologie = forms.ModelMultipleChoiceField(
        queryset=Patologia.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2',
            'id': 'id_patologie',
            'style': 'width: 100%;'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Etichetta leggibile nel dropdown CSSN
        self.fields['CSSN'].label_from_instance = lambda obj: f"{obj.CSSN} - {obj.nome} {obj.cognome}"

    class Meta:
        model = Ricovero
        fields = ['CSSN', 'codOspedale', 'data_ingresso', 'durata', 'stato', 'motivo', 'costo']
        widgets = {
            'codOspedale': forms.Select(attrs={'class': 'form-select'}),
            'data_ingresso': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'durata': forms.NumberInput(attrs={'class': 'form-control'}),
            'stato': forms.NumberInput(attrs={'class': 'form-control'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'costo': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class NuovoPazienteForm(forms.ModelForm):
    class Meta:
        model = Cittadino
        fields = ['CSSN', 'nome', 'cognome', 'data_nascita', 'città', 'via']
        widgets = {
            'data_nascita': forms.DateInput(attrs={'type': 'date'})
        }