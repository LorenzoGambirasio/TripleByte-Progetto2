from django.shortcuts import render, get_object_or_404, redirect
from . import models
from django.core.paginator import Paginator
from .forms import RicoveroForm, NuovoPazienteForm, TrasferimentoForm
from django.db import transaction
from django.http import JsonResponse
from datetime import date, timedelta
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Count

def dashboard(request):
    return render(request, 'home.html')


def lista_cittadini(request):
    cittadini = models.Cittadino.objects.annotate(numero_ricoveri=Count('ricovero'))

    # Filtri
    nome = request.GET.get('nome', '')
    cognome = request.GET.get('cognome', '')
    luogo = request.GET.get('luogo', '')
    indirizzo = request.GET.get('indirizzo', '')
    cssn = request.GET.get('cssn', '')
    stato = request.GET.get('stato', '')

    if nome:
        cittadini = cittadini.filter(nome__icontains=nome)
    if cognome:
        cittadini = cittadini.filter(cognome__icontains=cognome)
    if luogo:
        cittadini = cittadini.filter(città__icontains=luogo)
    if indirizzo:
        cittadini = cittadini.filter(via__icontains=indirizzo)
    if cssn:
        cittadini = cittadini.filter(CSSN__icontains=cssn)
    if stato:
        cittadini = [c for c in cittadini if c.stato == stato]

    # Ordinamento dinamico
    sort_field = request.GET.get('sort', 'cognome')
    sort_order = request.GET.get('order', 'asc')
    if sort_order == 'desc':
        sort_field = '-' + sort_field
    try:
        cittadini = cittadini.order_by(sort_field)
    except Exception:
        pass

    # Paginazione
    paginator = Paginator(cittadini, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Colonne da visualizzare (unifica Nome e Cognome!)
    columns = [
        ('CSSN', 'CSSN'),
        ('nome_cognome', 'Nome e Cognome'),
        ('data_nascita', 'Data di Nascita'),
        ('città', 'Luogo di Nascita'),
        ('via', 'Indirizzo'),
        ('stato', 'Stato'),
    ]
    
    colonne_larghezze = {
        'CSSN': '145px',
        'nome_cognome': '120px',
        'data_nascita': '105px',
        'città': '125px',
        'via': '105px',
        'stato': '73px',
        'ricoveri': '60px',
    }


    context = {
        'filtro_template': 'filtri/filtro_cittadini.html',
        'page_obj': page_obj,
        'cittadini': page_obj.object_list,
        'current_sort': request.GET.get('sort', ''),
        'current_order': request.GET.get('order', ''),
        'columns': columns,
        'colonne_larghezze': colonne_larghezze,
        'etichetta': 'cittadini'
    }

    return render(request, 'cittadini.html', context)

def lista_ospedali(request):
    ospedali = models.Ospedale.objects.select_related('CSSN_direttore').all()

    # Filtri base
    nome = request.GET.get('nome', '')
    citta = request.GET.get('citta', '')
    direttore = request.GET.get('direttore', '')

    if nome:
        ospedali = ospedali.filter(nome__icontains=nome)
    if citta:
        ospedali = ospedali.filter(città__icontains=citta)
    if direttore:
        ospedali = ospedali.filter(CSSN_direttore__cognome__icontains=direttore)

    # Ordinamento dinamico
    sort_field = request.GET.get('sort', 'nome')  # default
    sort_order = request.GET.get('order', 'asc')
    if sort_order == 'desc':
        sort_field = '-' + sort_field
    try:
        ospedali = ospedali.order_by(sort_field)
    except Exception:
        pass  # campo non valido

    # Paginazione
    paginator = Paginator(ospedali, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    columns = [
        ('nome', 'Nome'),
        ('città', 'Città'),
        ('indirizzo', 'Indirizzo'),
        ('CSSN_direttore__cognome', 'Direttore Sanitario'),
    ]

    context = {
        'filtro_template': 'filtri/filtro_ospedali.html',
        'ospedali': page_obj.object_list,
        'page_obj': page_obj,
        'current_sort': request.GET.get('sort', ''),
        'current_order': request.GET.get('order', ''),
        'columns': columns,
        'etichetta': 'ospedali'
    }

    return render(request, 'ospedali.html', context)

def lista_patologie(request):
    patologie_base = models.Patologia.objects.all()

    nome_query = request.GET.get('nome')
    criticita_query = request.GET.get('criticita')
    tipologia_query = request.GET.get('tipologia')

    if nome_query:
        patologie_base = patologie_base.filter(nome__icontains=nome_query)
    if criticita_query:
        patologie_base = patologie_base.filter(criticita=criticita_query)

    # Costruzione lista con tipologia
    patologie = []
    for p in patologie_base:
        tipi = []
        if models.PatologiaCronica.objects.filter(cod=p).exists():
            tipi.append("Cronica")
        if models.PatologiaMortale.objects.filter(cod=p).exists():
            tipi.append("Mortale")
        tipo = " e ".join(tipi) if tipi else "Nessuna"

        if not tipologia_query or tipologia_query in tipo:
            patologie.append({
                'codice': p.cod,
                'nome': p.nome,
                'criticita': p.criticita,
                'tipologia': tipo,
            })

    # Ordinamento
    sort = request.GET.get("sort", "nome")
    order = request.GET.get("order", "asc")

    reverse = order == "desc"
    try:
        patologie.sort(key=lambda x: x.get(sort, "").lower() if isinstance(x.get(sort), str) else x.get(sort), reverse=reverse)
    except Exception:
        pass  # fallback: no sort

    paginator = Paginator(patologie, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "patologie.html", {
        'page_obj': page_obj,
        'patologie': page_obj.object_list,
        'range_criticita': range(1, 11),
        'filtro_template': 'filtri/filtro_patologie.html',
        'current_sort': sort,
        'current_order': order,
        'etichetta': 'patologie'
    })

def genera_codice_ricovero():
    codici = models.Ricovero.objects.values_list('codRicovero', flat=True)
    max_num = 0

    for codice in codici:
        if codice.startswith("R") and codice[1:].isdigit():
            numero = int(codice[1:])
            if numero > max_num:
                max_num = numero

    nuovo_numero = max_num + 1
    return f"R{nuovo_numero}"

@transaction.atomic
def lista_ricoveri(request):
    form = RicoveroForm()
    successo = False

    if request.method == 'POST':
        form = RicoveroForm(request.POST)
        if form.is_valid():
            ricovero = form.save(commit=False)

            oggi = date.today()
            data_ingresso = ricovero.data_ingresso
            durata = ricovero.durata
            costo = ricovero.costo
            errori = []

            if data_ingresso > oggi:
                errori.append("La data di ingresso non può essere nel futuro.")
            elif data_ingresso < oggi - timedelta(days=30):
                errori.append("La data di ingresso non può essere più vecchia di un mese.")
            if durata < 1 or durata > 60:
                errori.append("La durata deve essere tra 1 e 60 giorni.")
            if costo < 0 or costo > 99999:
                errori.append("Il costo non può essere negativo o superiore a 99999 euro.")
            if not ricovero.motivo.strip():
                errori.append("Il motivo del ricovero è obbligatorio.")

            ricovero.stato = 2 if (oggi - data_ingresso).days > durata else 0

            if errori:
                return JsonResponse({"success": False, "errors": errori})
            else:
                ultimo = models.Ricovero.objects.order_by('-codRicovero').first()
                if ultimo:
                    numero = int(ultimo.codRicovero[1:])
                    nuovo_cod = f"R{numero + 1:0{len(ultimo.codRicovero) - 1}d}"
                else:
                    nuovo_cod = "R0001"
                ricovero.codRicovero = nuovo_cod
                ricovero.save()
                form.save_m2m()

                for p in form.cleaned_data['patologie']:
                    models.PatologiaRicovero.objects.create(
                        codRicovero=ricovero,
                        codOspedale=ricovero.codOspedale,
                        codPatologia=p
                    )

                return JsonResponse({"success": True})
        else:
            # Se form.is_valid() è False -> ritorna errori form Django
            errors = []
            for field, field_errors in form.errors.items():
                for err in field_errors:
                    errors.append(err)
            return JsonResponse({"success": False, "errors": errors})

    # logica GET
    ricoveri = models.Ricovero.objects.select_related('CSSN', 'codOspedale').prefetch_related('patologie').all()

    # Ordinamento dinamico
    sort = request.GET.get('sort', 'codRicovero')
    dir = request.GET.get('dir', 'asc')
    
    valid_columns = dict([
        ("codOspedale__nome", "Ospedale"),
        ("CSSN__cognome", "Paziente"),
        ("CSSN__CSSN", "CSSN"),
        ("data_ingresso", "Data Inizio"),
        ("durata", "Durata"),
        ("stato", "Stato"),
        ("motivo", "Motivo"),
        ("costo", "Costo (€)")
    ])
    
    
    if sort not in valid_columns or dir not in ['asc', 'desc']:
        ordering = ['-codRicovero']  # Ordinamento di default
        sort = None
        dir = None
    elif sort == 'CSSN__cognome':
        # Ordinamento combinato cognome + nome
        ordering = ['CSSN__cognome', 'CSSN__nome'] if dir == 'asc' else ['-CSSN__cognome', '-CSSN__nome']
    else:
        ordering = [sort] if dir == 'asc' else [f'-{sort}']




    # FILTRI
    cssn = request.GET.get('cssn', '').strip()
    nome = request.GET.get('nome', '').strip()
    cognome = request.GET.get('cognome', '').strip()
    ospedale = request.GET.get('ospedale', '').strip()
    stato = request.GET.get('stato', '').strip()
    data_da = request.GET.get('data_da', '').strip()
    data_a = request.GET.get('data_a', '').strip()
    motivo = request.GET.get('motivo', '').strip()
    patologia = request.GET.get('patologia', '').strip()
    deceduti = request.GET.get('deceduti', '')

    if cssn:
        ricoveri = ricoveri.filter(CSSN__CSSN__icontains=cssn)
    if nome:
        ricoveri = ricoveri.filter(CSSN__nome__icontains=nome)
    if cognome:
        ricoveri = ricoveri.filter(CSSN__cognome__icontains=cognome)
    if ospedale:
        ricoveri = ricoveri.filter(codOspedale__codice=ospedale)
    if stato:
        ricoveri = ricoveri.filter(stato=stato)
    if data_da:
        ricoveri = ricoveri.filter(data_ingresso__gte=data_da)
    if data_a:
        ricoveri = ricoveri.filter(data_ingresso__lte=data_a)
    if motivo:
        ricoveri = ricoveri.filter(motivo__icontains=motivo)
    if patologia:
        ricoveri = ricoveri.filter(patologie__cod=patologia)
    if deceduti:
        ricoveri = ricoveri.filter(dataDecesso__isnull=False)


    ricoveri = ricoveri.order_by(*ordering)
    
    #Paginazione
    paginator = Paginator(ricoveri, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    colonne_larghezze = {
    "codOspedale__nome": "120px",
    "CSSN__cognome": "100px",
    "CSSN__CSSN": "165px",
    "data_ingresso": "90px",
    "durata": "60px",
    "stato": "50px",
    "motivo": "100px",
    "costo": "80px",
    "patologie": "100px",
    }

    return render(request, "ricoveri/ricovero.html", {
        'form': form,
        'page_obj': page_obj,
        'ricoveri': page_obj.object_list,
        'ospedali': models.Ospedale.objects.all(),
        'patologie': models.Patologia.objects.all(),
        'successo': successo,
        'filtro_template': 'filtri/filtro_ricovero.html',
        'etichetta': 'ricoveri',
        'sort': sort,
        'dir': dir,
        'colonne_larghezze': colonne_larghezze,
        'colonne_ordinabili': {
            "codOspedale__nome": "Ospedale",
            "CSSN__cognome": "Paziente",
            "CSSN__CSSN": "CSSN",
            "data_ingresso": "Data Inizio",
            "durata": "Durata",
            "stato": "Stato",
            "motivo": "Motivo",
            "costo": "Costo (€)"
        }.items()
        
    })


@transaction.atomic
def modifica_ricovero(request, pk):
    # 1. Recupera l'oggetto ricovero da modificare o restituisce un errore 404 se non esiste.
    ricovero = get_object_or_404(models.Ricovero, codRicovero=pk)

    if request.method == 'POST':
        # 2. Se la richiesta è POST, popola il form con i dati inviati e l'istanza da modificare.
        form = RicoveroForm(request.POST, instance=ricovero)
        if form.is_valid():
            # 3. Salva il form. Django si occuperà di aggiornare sia l'oggetto Ricovero
            #    sia le relazioni Many-to-Many (le patologie).
            form.save()
            # 4. Reindirizza alla pagina dell'elenco con il nome corretto.
            return redirect('ricoveri')
    else:
        # 5. Se la richiesta è GET, crea un'istanza del form legata all'oggetto Ricovero.
        #    Django pre-compilerà automaticamente tutti i campi, incluse le patologie.
        form = RicoveroForm(instance=ricovero)

    # 6. Renderizza il template passando il form e l'oggetto ricovero.
    context = {
        'form': form,
        'ricovero': ricovero
    }
    return render(request, 'ricoveri/modifica_ricovero.html', context)

def elimina_ricovero(request, pk):
    ricovero = get_object_or_404(models.Ricovero, pk=pk)
    if request.method == 'POST':
        ricovero.delete()
        return redirect('ricoveri')
    return render(request, 'ricoveri/elimina_ricovero.html', {
        'ricovero': ricovero
    })
    
# Assicurati di avere questi import all'inizio del file views.py

 # Assicurati che questo form esista in forms.py


def genera_nuovo_codice_ricovero():
    # Assicurati che questa logica sia corretta per il tuo schema
    ultimo_ricovero = models.Ricovero.objects.order_by('-codRicovero').first()
    if ultimo_ricovero:
        numero = int(ultimo_ricovero.codRicovero[1:]) + 1
        return f"R{numero:04d}"
    return "R0001"

def trasferisci_ricovero(request, pk):
    ricovero_originale = get_object_or_404(models.Ricovero, codRicovero=pk)

    if request.method == 'POST':
        form = TrasferimentoForm(request.POST, instance=ricovero_originale)
        if form.is_valid():
            nuovo_ospedale = form.cleaned_data['codOspedale']
            
            try:
                with transaction.atomic():
                    patologie_da_copiare = list(ricovero_originale.patologie.all())

                    models.Ricovero.objects.filter(pk=ricovero_originale.pk).update(stato=1)

                    # Creazione del nuovo ricovero
                    ricovero_nuovo = models.Ricovero.objects.create(
                        codRicovero=genera_nuovo_codice_ricovero(),
                        CSSN=ricovero_originale.CSSN,
                        codOspedale=nuovo_ospedale,
                        data_ingresso=timezone.now().date(),
                        motivo=ricovero_originale.motivo,  # <-- MODIFICA QUI: Mantiene il motivo originale
                        costo=ricovero_originale.costo,
                        durata=ricovero_originale.durata,
                        stato=0
                    )

                    # Associazione delle patologie
                    if patologie_da_copiare:
                        nuovi_collegamenti = []
                        for patologia in patologie_da_copiare:
                            nuovi_collegamenti.append(
                                models.PatologiaRicovero(
                                    codRicovero=ricovero_nuovo,
                                    codOspedale=ricovero_nuovo.codOspedale,
                                    codPatologia=patologia
                                )
                            )
                        models.PatologiaRicovero.objects.bulk_create(nuovi_collegamenti)

                return redirect('ricoveri')

            except Exception as e:
                form.add_error(None, f"Si è verificato un errore durante il trasferimento: {e}")
    else:
        form = TrasferimentoForm(instance=ricovero_originale)

    context = {
        'form': form,
        'ricovero': ricovero_originale
    }
    return render(request, 'ricoveri/trasferisci_ricovero.html', context)



def dichiara_decesso(request, pk):
    ricovero = get_object_or_404(models.Ricovero, pk=pk)
    return render(request)

def verifica_paziente(request):
    if request.method == "POST":
        cssn = request.POST.get('cssn', '').strip().upper()
        try:
            cittadino = models.Cittadino.objects.get(CSSN=cssn)
            return JsonResponse({'trovato': True, 'nome': f"{cittadino.nome} {cittadino.cognome}"})
        except models.Cittadino.DoesNotExist:
            return JsonResponse({'trovato': False})
    return JsonResponse({'error': 'Metodo non consentito'}, status=400)
