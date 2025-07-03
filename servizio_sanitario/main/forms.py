from django import forms
from . import models
from django.core.exceptions import ValidationError
from datetime import date, timedelta, datetime # Importa datetime qui
# from django.utils import timezone # Rimuovi questo import se non lo usi più altrove


class RicoveroForm(forms.ModelForm):
    CSSN = forms.ModelChoiceField(
        queryset=models.Cittadino.objects.filter(deceduto=0).order_by('cognome', 'nome'),
        label="CSSN",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_cittadino'}),
        to_field_name="CSSN"
    )

    patologie = forms.ModelMultipleChoiceField(
        queryset=models.Patologia.objects.all(),
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
            'min_value': 'La durata deve be essere almeno 1 giorno.',
            'max_value': 'La durata massima è di 60 giorni.'
        }
    )

    data_ingresso = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        error_messages={
            'required': 'Inserisci la data di ingresso.',
            'invalid': 'Formato data non valido. Usa AAAA-MM-GGTHH:MM.'
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
        model = models.Ricovero
        fields = ['CSSN', 'codOspedale', 'data_ingresso', 'durata', 'stato', 'motivo', 'costo']
        widgets = {
            'codOspedale': forms.Select(attrs={'class': 'form-select'}),
            'stato': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['CSSN'].queryset = models.Cittadino.objects.filter(deceduto=0).order_by('cognome', 'nome')

        self.fields['CSSN'].label_from_instance = lambda obj: f"{obj.CSSN} - {obj.nome} {obj.cognome}"

        self.fields['CSSN'].widget.attrs.update({'id': 'id_cittadino'})
        self.fields['patologie'].widget.attrs.update({'id': 'id_patologie'})
        self.fields['codOspedale'].widget.attrs.update({'id': 'id_codOspedale'})

class NuovoPazienteForm(forms.ModelForm):
    class Meta:
        model = models.Cittadino
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
        cleaned_data = super().clean()
        
        nuovo_ospedale = cleaned_data.get("codOspedale")
        
        if self.instance:
            if nuovo_ospedale == self.instance.codOspedale:
                raise ValidationError(
                    "L'ospedale di destinazione non può essere lo stesso di quello attuale. Seleziona un ospedale diverso."
                )
        
        return cleaned_data

# DecessoForm (basato su Cittadino)
class DecessoForm(forms.ModelForm):
    data_ora_decesso = forms.DateTimeField(
        label="Data e Ora del Decesso",
        input_formats=['%Y-%m-%dT%H:%M'], 
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        error_messages={
            'required': 'Inserisci la data e ora del decesso.',
            'invalid': 'Formato data e ora non valido. Assicurati che sia completo (es.বারে-MM-DDTHH:MM).'
        }
    )
    causa_decesso = forms.CharField(
        label="Causa del Decesso",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False, 
        max_length=500
    )

    class Meta:
        model = models.Cittadino
        fields = ['data_ora_decesso', 'causa_decesso']

    def clean_data_ora_decesso(self):
        data_ora_input = self.cleaned_data['data_ora_decesso']
        
        if not data_ora_input:
            return data_ora_input
        
        # Ottieni l'ora attuale e tronca i secondi e i microsecondi
        now_truncated = datetime.now().replace(second=0, microsecond=0)
        
        # Confronteremo l'input con l'ora attuale troncata
        if data_ora_input > now_truncated:
            raise ValidationError("La data e ora del decesso non può essere nel futuro.")
        
        return data_ora_input


# PasswordForm
class PasswordForm(forms.Form):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Inserisci la password.'
        }
    )