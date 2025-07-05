import re
from django import forms
from . import models
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from django.utils import timezone



class RicoveroForm(forms.ModelForm):
    CSSN = forms.ModelChoiceField(
        queryset=models.Cittadino.objects.filter(deceduto=0).order_by('cognome', 'nome'),
        label="Paziente",
        # CORREZIONE: Impostiamo l'etichetta vuota a None per rimuovere i trattini
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
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
            'min_value': 'La durata deve essere almeno 1 giorno.',
            'max_value': 'La durata massima è di 60 giorni.'
        }
    )

    data_ingresso = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        error_messages={
            'required': 'Inserisci la data di ingresso.',
            'invalid': 'Formato data non valido.'
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
        self.is_edit_mode = kwargs.pop('is_edit_mode', False)
        super().__init__(*args, **kwargs)

        # 1. Trova i CSSN di tutti i pazienti che hanno già un ricovero attivo (stato=0)
        pazienti_ricoverati_ids = models.Ricovero.objects.filter(stato=0).values_list('CSSN_id', flat=True)

        # 2. Filtra i cittadini: escludi i deceduti E quelli con un ricovero attivo
        self.fields['CSSN'].queryset = models.Cittadino.objects.filter(
            deceduto=0
        ).exclude(
            CSSN__in=pazienti_ricoverati_ids
        ).order_by('cognome', 'nome')
        self.fields['CSSN'].label_from_instance = lambda obj: f"{obj.CSSN} - {obj.nome} {obj.cognome}"
        
        if self.is_edit_mode:
            self.fields['CSSN'].required = False

        self.fields['CSSN'].widget.attrs.update({'id': 'id_cittadino'})
        self.fields['patologie'].widget.attrs.update({'id': 'id_patologie'})
        self.fields['codOspedale'].widget.attrs.update({'id': 'id_codOspedale'})

    def clean_data_ingresso(self):
        data_inserita = self.cleaned_data.get('data_ingresso')
        if data_inserita and data_inserita > timezone.now().date():
            raise ValidationError("La data di ingresso non può essere nel futuro.", code='future_date')
        return data_inserita

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
        if self.instance and nuovo_ospedale == self.instance.codOspedale:
            raise ValidationError(
                "L'ospedale di destinazione non può essere lo stesso di quello attuale. Seleziona un ospedale diverso."
            )
        return cleaned_data


class DecessoForm(forms.ModelForm):
    dataoradecesso = forms.DateTimeField(
        label="Data e Ora del Decesso",
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        error_messages={
            'required': 'Inserisci la data e ora del decesso.',
            'invalid': 'Formato data e ora non valido. Assicurati che sia completo (AAAA-MM-GGTHH:MM).'
        }
    )
    causadecesso = forms.CharField(
        label="Causa del Decesso",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        max_length=500
    )

    class Meta:
        model = models.Cittadino
        fields = ['dataoradecesso', 'causadecesso']

    def clean_dataoradecesso(self):
        data_ora_input = self.cleaned_data.get('dataoradecesso')
        if not data_ora_input:
            return data_ora_input
        
        if timezone.is_naive(data_ora_input):
            try:
                data_ora_aware = timezone.make_aware(data_ora_input, timezone.get_default_timezone())
            except Exception as e:
                raise ValidationError(f"Errore nella conversione del fuso orario: {e}")
        else:
            data_ora_aware = data_ora_input
        
        now_aware = timezone.now()
        now_plus_tolerance = now_aware + timedelta(seconds=2)
        
        if data_ora_aware > now_plus_tolerance:
            raise ValidationError("La data e ora del decesso non può essere nel futuro.")
        
        return data_ora_aware


class PasswordForm(forms.Form):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Inserisci la password.'
        }
    )

class NuovoPazienteForm(forms.ModelForm):
    provenienza = forms.ChoiceField(
        choices=[('Italia', 'Italia'), ('Estero', 'Estero')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='Italia',
        label="Provenienza"
    )

    class Meta:
        model = models.Cittadino
        fields = ['CSSN', 'nome', 'cognome', 'data_nascita', 'città', 'via']
        widgets = {
            'data_nascita': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cognome': forms.TextInput(attrs={'class': 'form-control'}),
            'città': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_citta'}),
            'via': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_indirizzo'}),
            'CSSN': forms.TextInput(attrs={'class': 'form-control', 'style': 'text-transform:uppercase'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['CSSN'].required = False

    def clean(self):
        cleaned_data = super().clean()
        provenienza = self.data.get('provenienza')
        cssn = cleaned_data.get('CSSN', '').upper()

        if provenienza == 'Italia':
            if not cssn:
                self.add_error('CSSN', "Il Codice Fiscale è obbligatorio per i pazienti italiani.")
            elif not re.match(r'^[A-Z]{6}[0-9LMNPQRSTUV]{2}[A-Z]{1}[0-9LMNPQRSTUV]{2}[A-Z]{1}[0-9LMNPQRSTUV]{3}[A-Z]{1}$', cssn):
                self.add_error('CSSN', "Formato Codice Fiscale non valido.")
            elif models.Cittadino.objects.filter(CSSN=cssn).exists():
                self.add_error('CSSN', "Questo Codice Fiscale è già registrato nel sistema.")
        
        cleaned_data['CSSN'] = cssn
        return cleaned_data
