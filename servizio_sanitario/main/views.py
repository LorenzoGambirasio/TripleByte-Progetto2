from django.shortcuts import render, get_object_or_404
from . import models
from django.core.paginator import Paginator
from .forms import RicoveroForm, NuovoPazienteForm, TrasferimentoForm, DecessoForm, PasswordForm 
from django.db import transaction
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Max, Q
from django.views.decorators.http import require_POST, require_http_methods
import json

ADMIN_PASSWORD = 'admin'

def dashboard(request):
    oggi = timezone.now()
    una_settimana_fa = oggi - timedelta(days=7)

    statistiche = {
        'labels': ['Attivi', 'Trasferiti', 'Dimessi', 'Deceduti'],
        'data': [
            models.Ricovero.objects.filter(stato=0, data_ingresso__gte=una_settimana_fa).count(),
            models.Ricovero.objects.filter(stato=1, data_ingresso__gte=una_settimana_fa).count(),
            models.Ricovero.objects.filter(stato=2, data_ingresso__gte=una_settimana_fa).count(),
            models.Ricovero.objects.filter(stato=3, data_ingresso__gte=una_settimana_fa).count(),
        ]
    }

    top_ospedali_qs = (
        models.Ricovero.objects
        .values('codOspedale__nome')
        .annotate(numero=Count('codRicovero'))
        .order_by('-numero')[:5]
    )

    top_ospedali = {
        'labels': [x['codOspedale__nome'] for x in top_ospedali_qs],
        'data': [x['numero'] for x in top_ospedali_qs]
    }

    return render(request, 'home.html', {
        'statistiche_json': json.dumps(statistiche),
        'top_ospedali_json': json.dumps(top_ospedali),
    })

def lista_cittadini(request):
    cittadini_base = models.Cittadino.objects.annotate(numero_ricoveri_cittadino=Count('ricovero')).all()

    nome_filtro = request.GET.get('nome', '').strip()
    cognome_filtro = request.GET.get('cognome', '').strip()
    luogo_nascita_filtro = request.GET.get('luogo', '').strip()
    indirizzo_filtro = request.GET.get('indirizzo', '').strip()
    cssn_filtro = request.GET.get('cssn', '').strip()
    stato_filtro = request.GET.get('stato', '').strip()

    if nome_filtro:
        cittadini_base = cittadini_base.filter(nome__icontains=nome_filtro)
    if cognome_filtro:
        cittadini_base = cittadini_base.filter(cognome__icontains=cognome_filtro)
    if luogo_nascita_filtro:
        cittadini_base = cittadini_base.filter(città__icontains=luogo_nascita_filtro)
    if indirizzo_filtro:
        cittadini_base = cittadini_base.filter(via__icontains=indirizzo_filtro)
    if cssn_filtro:
        cittadini_base = cittadini_base.filter(CSSN__icontains=cssn_filtro)
    
    cittadini_list = []
    for c in cittadini_base:
        cittadini_list.append({
            'CSSN': c.CSSN,
            'nome': c.nome,
            'cognome': c.cognome,
            'data_nascita': c.data_nascita,
            'città': c.città,
            'via': c.via,
            'deceduto': c.deceduto,
            'stato_display': c.stato,
            'numero_ricoveri': c.numero_ricoveri_cittadino,
        })

    if stato_filtro:
        cittadini_list = [c for c in cittadini_list if c['stato_display'] == stato_filtro]

    statistiche_cittadini = {
        'totali': models.Cittadino.objects.count(),
        'domicilio': models.Cittadino.objects.filter(deceduto=0).exclude(ricovero__stato=0).count(),
        'ricoverati': models.Ricovero.objects.filter(stato=0).count(),
        'deceduti': models.Cittadino.objects.filter(deceduto=1).count(),
    }

    colonne_larghezze = {
        'CSSN': '18%', 'nome_cognome': '18%', 'data_nascita': '12%',
        'città': '13%', 'via': '15%', 'stato': '10%', 'ricoveri': '8%',
    }
    columns = [
        ('CSSN', 'CSSN'), ('nome_cognome', 'Nome e Cognome'),
        ('data_nascita', 'Data di Nascita'), ('città', 'Città'),
        ('via', 'Indirizzo'), ('stato', 'Stato'), ('ricoveri', 'Ricoveri'),
    ]
    current_sort = request.GET.get('sort', 'cognome')
    current_order = request.GET.get('order', 'asc')
    reverse_order = current_order == 'desc'
    sort_key = 'stato_display' if current_sort == 'stato' else 'numero_ricoveri' if current_sort == 'ricoveri' else 'cognome'
    if current_sort == 'nome_cognome':
        cittadini_list.sort(key=lambda x: (x['cognome'], x['nome']), reverse=reverse_order)
    else:
        cittadini_list.sort(key=lambda x: (x.get(sort_key) is None, x.get(sort_key, '')), reverse=reverse_order)
        
    per_page = request.GET.get('per_page', 20)
    try: per_page = int(per_page)
    except ValueError: per_page = 20
    paginator = Paginator(cittadini_list, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        'page_obj': page_obj, 'colonne_larghezze': colonne_larghezze, 'columns': columns,
        'current_sort': current_sort, 'current_order': current_order, 'etichetta': 'cittadini',
        'filtro_template': 'filtri/filtro_cittadini.html', 'statistiche_cittadini': statistiche_cittadini,
    }
    return render(request, 'cittadini.html', context)


def lista_ospedali(request):
    ospedali_base = models.Ospedale.objects.select_related('CSSN_direttore').annotate(
        numero_ricoveri_ospedale=Count('ricovero')
    ).all()

    nome_filtro = request.GET.get('nome', '').strip()
    citta_filtro = request.GET.get('città', '').strip()
    direttore_filtro = request.GET.get('direttore', '').strip()

    if nome_filtro:
        ospedali_base = ospedali_base.filter(nome__icontains=nome_filtro)
    if citta_filtro:
        ospedali_base = ospedali_base.filter(città__icontains=citta_filtro)
    if direttore_filtro:
        ospedali_base = ospedali_base.filter(
            Q(CSSN_direttore__nome__icontains=direttore_filtro) |
            Q(CSSN_direttore__cognome__icontains=direttore_filtro)
        )
    
    statistiche_ospedali = {
        'totali': models.Ospedale.objects.count(),
        'con_direttore': models.Ospedale.objects.filter(CSSN_direttore__isnull=False).count(),
        'totale_ricoveri_globale': models.Ricovero.objects.count(),
    }
    
    colonne_larghezze = {
        'nome': '22%', 'città': '22%', 'indirizzo': '22%', 'direttore': '22%', 'ricoveri': '12%',
    }
    columns = [
        ('nome', 'Nome Ospedale'), ('città', 'Città'), ('indirizzo', 'Indirizzo'),
        ('direttore', 'Direttore Sanitario'), ('ricoveri', 'Ricoveri'),
    ]
    current_sort = request.GET.get('sort', 'nome')
    current_order = request.GET.get('order', 'asc')
    sort_mapping = {
        'nome': 'nome', 'città': 'città', 'indirizzo': 'indirizzo',
        'direttore': 'CSSN_direttore__cognome', 'ricoveri': 'numero_ricoveri_ospedale',
    }
    sort_field = sort_mapping.get(current_sort, 'nome')
    if current_order == 'desc':
        ospedali_base = ospedali_base.order_by(f'-{sort_field}')
    else:
        ospedali_base = ospedali_base.order_by(sort_field)
    per_page = request.GET.get('per_page', 20)
    try: per_page = int(per_page)
    except ValueError: per_page = 20
    paginator = Paginator(ospedali_base, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        'page_obj': page_obj, 'ospedali': page_obj.object_list, 'columns': columns,
        'colonne_larghezze': colonne_larghezze, 'current_sort': current_sort,
        'current_order': current_order, 'etichetta': 'ospedali',
        'filtro_template': 'filtri/filtro_ospedali.html',
        'statistiche_ospedali': statistiche_ospedali,
    }
    return render(request, 'ospedali.html', context)

def lista_patologie(request):
    # Annotate le patologie con il conteggio dei ricoveri
    patologie_base = models.Patologia.objects.annotate(
        numero_ricoveri_patologia=Count('ricoveri')
    ).all()

    # LOGICA FILTRI
    nome_filtro = request.GET.get('nome', '').strip()
    criticita_filtro = request.GET.get('criticita', '').strip()
    tipologia_filtro = request.GET.get('tipologia', '').strip()

    if nome_filtro:
        patologie_base = patologie_base.filter(nome__icontains=nome_filtro)
    if criticita_filtro:
        try:
            patologie_base = patologie_base.filter(criticita=int(criticita_filtro))
        except ValueError:
            pass

    # Applica i filtri di tipologia
    if tipologia_filtro:
        if tipologia_filtro == "Cronica":
            patologie_base = patologie_base.filter(patologiacronica__isnull=False).distinct()
        elif tipologia_filtro == "Mortale":
            patologie_base = patologie_base.filter(patologiamortale__isnull=False).distinct()
        elif tipologia_filtro == "Nessuna":
            patologie_base = patologie_base.exclude(patologiacronica__isnull=False).exclude(patologiamortale__isnull=False).distinct()
        elif tipologia_filtro == "Cronica e Mortale":
            patologie_base = patologie_base.filter(patologiacronica__isnull=False, patologiamortale__isnull=False).distinct()

    # Pre-processa le patologie per aggiungere il campo 'tipologia' e 'numero_ricoveri'
    patologie_processate = []
    for p in patologie_base:
        tipi = []
        is_cronica = models.PatologiaCronica.objects.filter(cod=p.cod).exists()
        is_mortale = models.PatologiaMortale.objects.filter(cod=p.cod).exists()

        if is_cronica: tipi.append("Cronica")
        if is_mortale: tipi.append("Mortale")

        tipo_display = " e ".join(tipi) if tipi else "Nessuna"
        
        patologie_processate.append({
            'codice': p.cod,
            'nome': p.nome,
            'criticita': p.criticita,
            'tipologia': tipo_display,
            'numero_ricoveri': p.numero_ricoveri_patologia,
        })

    # Calcolo delle statistiche per i riquadri
    statistiche_patologie = {
        'totali': models.Patologia.objects.count(),
        'croniche': models.PatologiaCronica.objects.count(),
        'mortali': models.PatologiaMortale.objects.count(),
    }

    # LOGICA DI ORDINAMENTO (ordina la lista in memoria)
    current_sort = request.GET.get('sort', 'nome')
    current_order = request.GET.get('order', 'asc')

    if current_sort == 'nome':
        patologie_processate.sort(key=lambda x: x['nome'], reverse=(current_order == 'desc'))
    elif current_sort == 'criticita':
        patologie_processate.sort(key=lambda x: x['criticita'], reverse=(current_order == 'desc'))
    elif current_sort == 'tipologia':
        patologie_processate.sort(key=lambda x: x['tipologia'], reverse=(current_order == 'desc'))
    elif current_sort == 'numero_ricoveri':
        patologie_processate.sort(key=lambda x: x['numero_ricoveri'], reverse=(current_order == 'desc'))

    # Gestione righe per pagina
    per_page = request.GET.get('per_page', 20)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 20

    paginator = Paginator(patologie_processate, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        'page_obj': page_obj,
        'patologie': page_obj.object_list,
        'range_criticita': range(1, 11),
        'current_sort': current_sort,
        'current_order': current_order,
        'etichetta': 'patologie',
        'filtro_template': 'filtri/filtro_patologie.html',
        'statistiche_patologie': statistiche_patologie,
    }
    return render(request, "patologie.html", context)

def genera_nuovo_codice_ricovero():
    ultimo = models.Ricovero.objects.order_by('codRicovero').last()
    if not ultimo: return "R0001"
    try:
        numero = int(ultimo.codRicovero[1:]) + 1
    except (ValueError, TypeError):
        return "R0001"
    return f"R{numero:04d}"


def lista_ricoveri(request):
    if request.method == 'POST':
        form = RicoveroForm(request.POST)
        if form.is_valid():
            ricovero = form.save(commit=False)
            ricovero.codRicovero = genera_nuovo_codice_ricovero()
            ricovero.save()
            
            patologie_selezionate_cods = form.cleaned_data.get('patologie')
            models.PatologiaRicovero.objects.filter(codRicovero=ricovero).delete()
            
            if patologie_selezionate_cods:
                for patologia_obj in patologie_selezionate_cods:
                    models.PatologiaRicovero.objects.create(
                        codRicovero=ricovero,
                        codOspedale=ricovero.codOspedale,
                        codPatologia=patologia_obj
                    )

            return JsonResponse({"success": True})
        else:
            errors = [error for field, field_errors in form.errors.items() for error in field_errors]
            return JsonResponse({"success": False, "errors": errors})

    # Logica GET
    form = RicoveroForm()
    
    # ***** INIZIO MODIFICA *****
    # Calcola le statistiche SUL TOTALE, prima di applicare i filtri.
    ricoveri_base = models.Ricovero.objects.all()
    statistiche = {
        'totali': ricoveri_base.count(),
        'attivi': ricoveri_base.filter(stato=0).count(),
        'trasferiti': ricoveri_base.filter(stato=1).count(),
        'dimessi': ricoveri_base.filter(stato=2).count(),
        'deceduti': ricoveri_base.filter(stato=3).count()
    }

    # Applica i filtri al queryset che verrà mostrato nella tabella
    ricoveri_filtrati = ricoveri_base.select_related('CSSN', 'codOspedale').prefetch_related('patologie')
    # ***** FINE MODIFICA *****

    # --- LOGICA DEI FILTRI (invariata) ---
    cssn_from_url = request.GET.get('cssn', '').strip()
    ospedale_from_url = request.GET.get('ospedale_cod', '').strip()
    nome_patologia_from_url = request.GET.get('nome_patologia', '').strip()

    cssn_from_form = request.GET.get('cssn_form', '').strip()
    nome_from_form = request.GET.get('nome', '').strip()
    cognome_from_form = request.GET.get('cognome', '').strip()
    ospedale_from_form = request.GET.get('ospedale', '').strip()
    stato_from_form = request.GET.get('stato', '').strip()
    data_da_from_form = request.GET.get('data_da', '').strip()
    data_a_from_form = request.GET.get('data_a', '').strip()
    motivo_from_form = request.GET.get('motivo', '').strip()
    nome_patologia_list_from_form = request.GET.getlist('nome_patologia')

    final_cssn_filter = cssn_from_url if cssn_from_url else cssn_from_form
    final_nome_filter = nome_from_form
    final_cognome_filter = cognome_from_form
    final_ospedale_filter = ospedale_from_url if ospedale_from_url else ospedale_from_form
    final_stato_filter = stato_from_form
    final_data_da_filter = data_da_from_form
    final_data_a_filter = data_a_from_form
    final_motivo_filter = motivo_from_form
    
    final_nome_patologia_filters = []
    if nome_patologia_from_url:
        final_nome_patologia_filters = [nome_patologia_from_url]
    elif nome_patologia_list_from_form:
        final_nome_patologia_filters = nome_patologia_list_from_form

    if final_cssn_filter: ricoveri_filtrati = ricoveri_filtrati.filter(CSSN__CSSN__icontains=final_cssn_filter)
    if final_nome_filter: ricoveri_filtrati = ricoveri_filtrati.filter(CSSN__nome__icontains=final_nome_filter)
    if final_cognome_filter: ricoveri_filtrati = ricoveri_filtrati.filter(CSSN__cognome__icontains=final_cognome_filter)
    if final_ospedale_filter: ricoveri_filtrati = ricoveri_filtrati.filter(codOspedale__codice=final_ospedale_filter)
    if final_stato_filter: ricoveri_filtrati = ricoveri_filtrati.filter(stato=final_stato_filter)
    if final_data_da_filter: ricoveri_filtrati = ricoveri_filtrati.filter(data_ingresso__gte=final_data_da_filter)
    if final_data_a_filter: ricoveri_filtrati = ricoveri_filtrati.filter(data_ingresso__lte=final_data_a_filter)
    if final_motivo_filter: ricoveri_filtrati = ricoveri_filtrati.filter(motivo__icontains=final_motivo_filter)
    
    if final_nome_patologia_filters:
        ricoveri_filtrati = ricoveri_filtrati.filter(patologie__nome__in=final_nome_patologia_filters).distinct()
    
    # --- Calcolo Statistiche RIMOSSO da qui ---
    
    # --- LOGICA ORDINAMENTO TABELLA RICOVERI ---
    current_sort = request.GET.get('sort', 'codRicovero')
    current_order = request.GET.get('order', 'desc')

    sort_mapping = {
        'ospedale': 'codOspedale__nome',
        'paziente': 'CSSN__cognome',
        'data_ingresso': 'data_ingresso',
        'durata': 'durata',
        'stato': 'stato',
        'costo': 'costo',
        'motivo': 'motivo',
        'patologie': 'patologie__criticita',
        'codRicovero': 'codRicovero',
    }

    sort_field = sort_mapping.get(current_sort, 'codRicovero')
    
    if current_order == 'desc':
        ricoveri_ordinati = ricoveri_filtrati.order_by(f'-{sort_field}')
    else:
        ricoveri_ordinati = ricoveri_filtrati.order_by(sort_field)
    
    # Gestione righe per pagina
    per_page = request.GET.get('per_page', 15)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 15

    paginator = Paginator(ricoveri_ordinati, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    ricoveri_con_dati = []
    for ricovero in page_obj.object_list:
        max_criticita = ricovero.patologie.aggregate(max_c=Max('criticita'))['max_c'] or 0
        ricoveri_con_dati.append({'ricovero': ricovero, 'max_criticita': max_criticita})

    context = {
        'form': form, 'page_obj': page_obj, 'ricoveri_items': ricoveri_con_dati,
        'ospedali': models.Ospedale.objects.all(), 
        'statistiche': statistiche, # Usa le statistiche calcolate all'inizio
        'patologie': models.Patologia.objects.all(), 'filtro_template': 'filtri/filtro_ricovero.html',
        'current_sort': current_sort,
        'current_order': current_order,
        # Passa i filtri attivi al template per pre-popolare il form
        'filtri_attivi': {
            'cssn': final_cssn_filter, 'nome': final_nome_filter, 'cognome': final_cognome_filter,
            'ospedale': final_ospedale_filter, 'stato': final_stato_filter, 'data_da': final_data_da_filter,
            'data_a': final_data_a_filter, 'motivo': final_motivo_filter,
            'nome_patologia': final_nome_patologia_filters,
        }
    }
    return render(request, "ricoveri/ricovero.html", context)


@transaction.atomic
def trasferisci_ricovero(request, pk):
    ricovero_originale = get_object_or_404(models.Ricovero, codRicovero=pk)
    if request.method == 'POST':
        form = TrasferimentoForm(request.POST, instance=ricovero_originale)
        if form.is_valid():
            nuovo_ospedale = form.cleaned_data['codOspedale']
            
            # --- CLONAZIONE DEL RICOVERO PER IL TRASFERIMENTO ---
            ricovero_nuovo = ricovero_originale
            ricovero_nuovo.pk = None # Stacca l'istanza dal database
            ricovero_nuovo._state.adding = True # Indica che è un nuovo oggetto

            ricovero_nuovo.codRicovero = genera_nuovo_codice_ricovero()
            ricovero_nuovo.codOspedale = nuovo_ospedale
            ricovero_nuovo.data_ingresso = timezone.now().date() # La data di ingresso per il nuovo ricovero è oggi
            ricovero_nuovo.stato = 0 # Il nuovo ricovero è "Attivo"
            ricovero_nuovo.save() # Salva il nuovo ricovero

            # Aggiorna lo stato del ricovero originale a "Trasferito"
            models.Ricovero.objects.filter(codRicovero=pk).update(stato=1)

            # Trasferisci le patologie al nuovo ricovero manualmente, dato il modello through
            # Prima, recupera le patologie del ricovero originale (prima che venga aggiornato lo stato)
            patologie_da_copiare = ricovero_originale.patologie.all() # Queryset di oggetti Patologia
            
            # Associa le patologie al nuovo ricovero tramite PatologiaRicovero
            for patologia_obj in patologie_da_copiare:
                models.PatologiaRicovero.objects.create(
                    codRicovero=ricovero_nuovo,
                    codOspedale=ricovero_nuovo.codOspedale, # Usa l'ospedale del nuovo ricovero
                    codPatologia=patologia_obj # L'oggetto Patologia
                )
            
            return JsonResponse({'success': True})
        else:
            errors = [error for field in form.errors.values() for error in field]
            return JsonResponse({"success": False, "errors": errors})
    return JsonResponse({'error': 'Metodo non valido'}, status=405)

@require_http_methods(["POST"])
def modifica_ricovero(request, pk):
    ricovero = get_object_or_404(models.Ricovero, pk=pk)
    
    data = request.POST.copy()
    
    # Assicurati che i valori non modificabili vengano passati al form
    # altrimenti il ModelForm penserà che manchino e genererà errori di validazione.
    if 'CSSN' not in data:
        data['CSSN'] = ricovero.CSSN.CSSN
    if 'codOspedale' not in data:
        data['codOspedale'] = ricovero.codOspedale.codice
    
    # Manteniamo questa riga per la validazione iniziale del form.
    # Il valore effettivo dello stato verrà ricalcolato dopo la validazione.
    data['stato'] = ricovero.stato 

    form = RicoveroForm(data, instance=ricovero)
    
    if form.is_valid():
        ricovero_salvato = form.save(commit=False)
        
        # --- LOGICA PER AGGIORNARE LO STATO IN BASE ALLA DURATA ---
        # Applica questa logica solo se lo stato attuale è Attivo (0) o Dimesso (2)
        if ricovero_salvato.stato in [0, 2]:
            today = timezone.now().date()
            
            # Calcola la data di fine prevista del ricovero con la nuova durata
            # Assicurati che ricovero_salvato.durata non sia None o 0 per evitare errori
            if ricovero_salvato.durata is not None and ricovero_salvato.durata > 0:
                data_fine_prevista = ricovero_salvato.data_ingresso + timedelta(days=ricovero_salvato.durata)
            else:
                # Se la durata non è valida, consideriamo il ricovero ancora attivo per default
                # o puoi decidere una logica diversa (es. errore, o stato indefinito)
                data_fine_prevista = today + timedelta(days=1) # Forza a essere nel futuro se durata non valida
            
            if data_fine_prevista <= today:
                ricovero_salvato.stato = 2  # Dimesso
            else:
                ricovero_salvato.stato = 0  # Attivo
        # --- FINE NUOVA LOGICA ---

        ricovero_salvato.save()
        
        # GESTIONE MANUALE DELLE PATOLOGIE (TABELLA THROUGH) PER LA MODIFICA
        patologie_selezionate_cods = form.cleaned_data.get('patologie') # Sono gli oggetti Patologia
        
        # Elimina tutte le relazioni esistenti per questo ricovero
        models.PatologiaRicovero.objects.filter(codRicovero=ricovero_salvato).delete()
        
        # Poi, crea nuove istanze di PatologiaRicovero per ogni patologia selezionata
        if patologie_selezionate_cods:
            for patologia_obj in patologie_selezionate_cods:
                models.PatologiaRicovero.objects.create(
                    codRicovero=ricovero_salvato,
                    codOspedale=ricovero_salvato.codOspedale, # Usa l'Ospedale del ricovero
                    codPatologia=patologia_obj # L'oggetto Patologia
                )
        # FINE GESTIONE MANUALE DELLE PATOLOGIE

        return JsonResponse({"success": True})
    else:
        errors = {field: form.errors[field] for field in form.errors if field != '__all__'}
        non_field_errors = form.non_field_errors()
        
        return JsonResponse({"success": False, "errors": errors, "non_field_errors": list(non_field_errors)}, status=400)


@require_POST
def elimina_ricovero(request, pk):
    ricovero = get_object_or_404(models.Ricovero, pk=pk)
    try:
        # Quando elimini un ricovero, devi eliminare prima le relazioni nella tabella "through"
        # dato che gestisci PatologiaRicovero manualmente.
        models.PatologiaRicovero.objects.filter(codRicovero=ricovero).delete()
        ricovero.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "errors": [str(e)]}, status=400)

# FUNZIONI PER IL DECESSO (DA IMPLEMENTARE CORRETTAMENTE)

@require_http_methods(["POST"]) # Questa vista accetta POST per la verifica password
def verifica_password(request):
    form = PasswordForm(request.POST)
    if form.is_valid():
        password_inserita = form.cleaned_data['password']
        if password_inserita == ADMIN_PASSWORD:
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": ["Password non corretta."]}, status=400)
    else:
        errors = {field: form.errors[field] for field in form.errors if field != '__all__'}
        non_field_errors = form.non_field_errors()
        return JsonResponse({"success": False, "errors": errors, "non_field_errors": list(non_field_errors)}, status=400)


@require_http_methods(["POST"]) # Accetta solo POST dal modale
@transaction.atomic
def dichiara_decesso(request, pk): # pk qui è il codRicovero che ha triggerato
    ricovero = get_object_or_404(models.Ricovero, codRicovero=pk)
    cittadino = ricovero.CSSN # Ottieni il cittadino associato al ricovero
    
    # Se il paziente è già deceduto, non permettere un nuovo decesso tramite questa funzione
    if cittadino.deceduto == 1:
        return JsonResponse({"success": False, "errors": ["Questo paziente è già stato dichiarato deceduto."]}, status=400)

    form = DecessoForm(request.POST, instance=cittadino) # DecessoForm agisce sull'istanza del Cittadino
    
    if form.is_valid():
        cittadino_salvato = form.save(commit=False) # Salva i campi del form (dataoradecesso, causadecesso) nel cittadino
        
        # Aggiorna lo stato del cittadino a "Deceduto"
        cittadino_salvato.deceduto = 1
        cittadino_salvato.save() # Salva le modifiche al cittadino
        
        # Aggiorna TUTTI i ricoveri attivi, trasferiti o dimessi di questo cittadino a stato 3 (Deceduto)
        # Questo garantisce che tutti i ricoveri del paziente mostrino lo stato corretto di decesso.
        models.Ricovero.objects.filter(CSSN=cittadino, stato__in=[0, 1, 2]).update(stato=3)

        return JsonResponse({"success": True})
    else:
        # Restituisci gli errori di validazione del form
        errors = {field: form.errors[field] for field in form.errors if field != '__all__'}
        non_field_errors = form.non_field_errors()
        return JsonResponse({"success": False, "errors": errors, "non_field_errors": list(non_field_errors)}, status=400)

@require_http_methods(["POST"])
@transaction.atomic
def modifica_causa_decesso(request, pk): # pk qui è il codRicovero, ma ci serve il CSSN del paziente
    ricovero = get_object_or_404(models.Ricovero, codRicovero=pk)
    cittadino = ricovero.CSSN

    # Assicurati che il paziente sia effettivamente deceduto per poter modificare la causa
    if cittadino.deceduto != 1:
        return JsonResponse({"success": False, "errors": ["Il paziente non è dichiarato deceduto."]}, status=400)

    form = DecessoForm(request.POST, instance=cittadino) # Il form agisce sull'istanza del Cittadino
    
    if form.is_valid():
        # Salva solo la causa del decesso e la data/ora se sono state modificate
        form.save() # Questo salverà i campi dataoradecesso e causadecesso sul cittadino
        return JsonResponse({"success": True})
    else:
        errors = {field: form.errors[field] for field in form.errors if field != '__all__'}
        non_field_errors = form.non_field_errors()
        return JsonResponse({"success": False, "errors": errors, "non_field_errors": list(non_field_errors)}, status=400)

def verifica_paziente(request):
    if request.method == "POST":
        cssn = request.POST.get('cssn', '').strip().upper()
        try:
            cittadino = models.Cittadino.objects.get(CSSN=cssn)
            if cittadino.deceduto == 1:
                return JsonResponse({'trovato': False, 'message': 'Paziente già dichiarato deceduto.'})
            
            return JsonResponse({'trovato': True, 'nome': f"{cittadino.nome} {cittadino.cognome}"})
        except models.Cittadino.DoesNotExist:
            return JsonResponse({'trovato': False, 'message': 'Paziente non trovato.'})
    return JsonResponse({'error': 'Metodo non consentito'}, status=400)

def verifica_paziente(request):
    if request.method == "POST":
        cssn = request.POST.get('cssn', '').strip().upper()
        try:
            cittadino = models.Cittadino.objects.get(CSSN=cssn)
            if cittadino.deceduto == 1:
                return JsonResponse({'trovato': False, 'message': 'Paziente già dichiarato deceduto.'})
            
            return JsonResponse({'trovato': True, 'nome': f"{cittadino.nome} {cittadino.cognome}"})
        except models.Cittadino.DoesNotExist:
            return JsonResponse({'trovato': False, 'message': 'Paziente non trovato.'})
    return JsonResponse({'error': 'Metodo non consentito'}, status=400)