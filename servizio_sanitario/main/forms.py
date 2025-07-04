from django import forms
from . import models
from django.core.exceptions import ValidationError
from datetime import date, timedelta, datetime # Mantieni datetime per DateField e altri usi se necessario
from django.utils import timezone # REINTRODUCI E USA PER DATETIME AWARE
import pytz # Potrebbe servire per make_aware se il fuso orario non è UTC


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
    dataoradecesso = forms.DateTimeField( # NOME SENZA UNDERSCORE
        label="Data e Ora del Decesso",
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        error_messages={
            'required': 'Inserisci la data e ora del decesso.',
            'invalid': 'Formato data e ora non valido. Assicurati che sia completo (AAAA-MM-GGTHH:MM).'
        }
    )
    causadecesso = forms.CharField( # NOME SENZA UNDERSCORE
        label="Causa del Decesso",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        max_length=500
    )

    class Meta:
        model = models.Cittadino
        fields = ['dataoradecesso', 'causadecesso']

    def clean_data_ora_decesso(self):
        data_ora_input = self.cleaned_data['data_ora_decesso']
        
        if not data_ora_input:
            return data_ora_input
        
        # Se data_ora_input è naive, rendilo aware usando il fuso orario corrente del progetto
        # e poi convertilo a UTC per il confronto.
        if timezone.is_naive(data_ora_input):
            # Interpreta il naive datetime come se fosse nel fuso orario di default di Django (settings.TIME_ZONE)
            try:
                # Usa get_default_timezone() per un timezone robusto, specialmente con USE_TZ=True
                data_ora_aware = timezone.make_aware(data_ora_input, timezone.get_default_timezone())
            except Exception as e:
                raise ValidationError(f"Errore nella conversione del fuso orario: {e}")
        else:
            data_ora_aware = data_ora_input # Già aware
        
        # Ottieni l'ora attuale dal server, che sarà già aware (perché USE_TZ=True)
        now_aware = timezone.now()
        
        # Confronteremo due datetime aware. Aggiungi un piccolo margine di tolleranza.
        # Questo è per compensare latenze di rete o differenze minime.
        now_plus_tolerance = now_aware + timedelta(seconds=2)
        
        if data_ora_aware > now_plus_tolerance:
            raise ValidationError("La data e ora del decesso non può essere nel futuro.")
        
        return data_ora_aware


# PasswordForm
class PasswordForm(forms.Form):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Inserisci la password.'
        }
    )