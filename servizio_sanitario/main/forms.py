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
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        to_field_name="CSSN",
        error_messages={
            'required': 'È obbligatorio selezionare un paziente.',
            'invalid_choice': 'Il paziente selezionato non è valido.',
        }
    )

    # --- CAMPO OSPEDALE MODIFICATO ---
    codOspedale = forms.ModelChoiceField(
        queryset=models.Ospedale.objects.all().order_by('nome'),
        label="Ospedale",
        empty_label=None,  # Rimuove l'opzione vuota "-------"
        widget=forms.Select(attrs={'class': 'form-select'}),
        error_messages={
            'required': 'È obbligatorio selezionare un ospedale.',
            'invalid_choice': 'L\'ospedale selezionato non è valido.',
        }
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
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'es. 7'
        }),
        error_messages={
            'required': 'La durata del ricovero è obbligatoria.',
            'min_value': 'La durata deve essere di almeno 1 giorno.',
            'max_value': 'La durata massima non può superare i 60 giorni.',
            'invalid': 'Inserisci un numero valido per la durata.'
        }
    )

    data_ingresso = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        error_messages={
            'required': 'La data di ingresso è obbligatoria.',
            'invalid': 'Inserisci un formato di data valido (GG/MM/AAAA).'
        }
    )

    costo = forms.DecimalField(
        max_digits=7,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'es. 1500.00'
        }),
        error_messages={
            'required': 'Il costo del ricovero è obbligatorio.',
            'invalid': 'Inserisci un valore numerico valido per il costo.',
            'max_digits': 'Il costo è troppo elevato (massimo 7 cifre).',
        }
    )

    motivo = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'es. Controllo post-operatorio'
        }),
        error_messages={
            'required': 'Il motivo del ricovero è obbligatorio.'
        }
    )

    class Meta:
        model = models.Ricovero
        fields = ['CSSN', 'codOspedale', 'data_ingresso', 'durata', 'stato', 'motivo', 'costo']
        widgets = {
            'stato': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.is_edit_mode = kwargs.pop('is_edit_mode', False)
        super().__init__(*args, **kwargs)

        pazienti_ricoverati_ids = models.Ricovero.objects.filter(stato=0).values_list('CSSN_id', flat=True)
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
    # --- CAMPO OSPEDALE MODIFICATO ---
    codOspedale = forms.ModelChoiceField(
        queryset=models.Ospedale.objects.all().order_by('nome'),
        label="Nuovo Ospedale di Destinazione",
        empty_label=None,  # Rimuove l'opzione vuota "-------"
        widget=forms.Select(attrs={'class': 'form-select'}),
        error_messages={
            'required': 'È obbligatorio selezionare un ospedale di destinazione.'
        }
    )

    class Meta:
        model = models.Ricovero
        fields = ['codOspedale']

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
            'required': 'La data e ora del decesso sono obbligatorie.',
            'invalid': 'Formato data e ora non valido. Usa AAAA-MM-GGTHH:MM.'
        }
    )
    causadecesso = forms.CharField(
        label="Causa del Decesso",
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3,
            'placeholder': 'es. Arresto cardiaco'
        }),
        required=False,
        max_length=500
    )

    class Meta:
        model = models.Cittadino
        fields = ['dataoradecesso', 'causadecesso']

    def __init__(self, *args, **kwargs):
        # Accetta il ricovero passato dalla vista
        self.ricovero = kwargs.pop('ricovero', None)
        super().__init__(*args, **kwargs)

    def clean_dataoradecesso(self):
        data_ora_input = self.cleaned_data.get('dataoradecesso')
        if not data_ora_input: return data_ora_input
        
        now_aware = timezone.now()
        if data_ora_input > now_aware:
            raise ValidationError("La data e ora del decesso non può essere nel futuro.")
        
        # NUOVO: Controllo sulla data del ricovero
        if self.ricovero and data_ora_input.date() < self.ricovero.data_ingresso:
            raise ValidationError(f"La data del decesso non può essere precedente alla data del ricovero ({self.ricovero.data_ingresso.strftime('%d/%m/%Y')}).")
            
        return data_ora_input

class PasswordForm(forms.Form):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Inserisci la password di amministrazione'
        }),
        error_messages={
            'required': 'Il campo password è obbligatorio.'
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
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'es. Mario'}),
            'cognome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'es. Rossi'}),
            'città': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_citta', 'placeholder': 'es. Roma'}),
            'via': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_indirizzo', 'placeholder': 'es. Via Garibaldi, 10'}),
            'CSSN': forms.TextInput(attrs={
                'class': 'form-control', 
                'style': 'text-transform:uppercase',
                'placeholder': 'es. RSSMRA80A01H501Z'
            }),
        }
        error_messages = {
            'nome': {'required': 'Il nome è obbligatorio.'},
            'cognome': {'required': 'Il cognome è obbligatorio.'},
            'data_nascita': {
                'required': 'La data di nascita è obbligatoria.',
                'invalid': 'Inserisci una data di nascita valida.',
            },
            'città': {'required': 'Il luogo di nascita è obbligatorio.'},
            'via': {'required': 'L\'indirizzo è obbligatorio.'},
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
                self.add_error('CSSN', "Formato Codice Fiscale non valido. Il formato corretto è 16 caratteri alfanumerici (es. RSSMRA80A01H501Z).")
            elif models.Cittadino.objects.filter(CSSN=cssn).exists():
                self.add_error('CSSN', "Un paziente con questo Codice Fiscale esiste già.")
        
        cleaned_data['CSSN'] = cssn
        return cleaned_data