from django import forms
from .models import Ricovero, Patologia, Cittadino
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from . import models

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

    durata = forms.IntegerField(
        min_value=1,
        max_value=60,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Inserisci la durata del ricovero.',
            'min_value': 'La durata deve essere almeno 1 giorno.',
            'max_value': 'La durata massima è di 60 giorni.'
        }
    )

    data_ingresso = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        error_messages={
            'required': 'Inserisci la data di ingresso.',
            'invalid': 'Formato data non valido. Usa gg/mm/aaaa.'
        }
    )

    costo = forms.DecimalField(
        max_digits=7,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Inserisci il costo del ricovero.',
            'invalid': 'Il costo deve essere un numero in euro.'
        }
    )

    motivo = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Inserisci il motivo del ricovero.'
        }
    )

    class Meta:
        model = Ricovero
        fields = ['CSSN', 'codOspedale', 'data_ingresso', 'durata', 'stato', 'motivo', 'costo']
        widgets = {
            'codOspedale': forms.Select(attrs={'class': 'form-select'}),
            'stato': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['CSSN'].label_from_instance = lambda obj: f"{obj.CSSN} - {obj.nome} {obj.cognome}"

        self.fields['CSSN'].widget.attrs.update({'id': 'id_cittadino'})
        self.fields['patologie'].widget.attrs.update({'id': 'id_patologie'})
        self.fields['codOspedale'].widget.attrs.update({'id': 'id_codOspedale'})

class NuovoPazienteForm(forms.ModelForm):
    class Meta:
        model = Cittadino
        fields = ['CSSN', 'nome', 'cognome', 'data_nascita', 'città', 'via']
        widgets = {
            'data_nascita': forms.DateInput(attrs={'type': 'date'})
        }
        
class TrasferimentoForm(forms.ModelForm):
    class Meta:
        model = models.Ricovero
        fields = ['codOspedale']
        labels = {
            'codOspedale': 'Nuovo Ospedale di Destinazione'
        }

    def clean(self):
        # Chiama prima la logica di pulizia del genitore
        cleaned_data = super().clean()
        
        # Recupera il nuovo ospedale selezionato nel form
        nuovo_ospedale = cleaned_data.get("codOspedale")
        
        # Controlla che l'istanza del ricovero esista (c'è sempre in un form di modifica)
        if self.instance:
            # Confronta il nuovo ospedale con quello attuale
            if nuovo_ospedale == self.instance.codOspedale:
                # Se sono uguali, solleva un errore di validazione
                raise ValidationError(
                    "L'ospedale di destinazione non può essere lo stesso di quello attuale. Seleziona un ospedale diverso."
                )
        
        return cleaned_data
