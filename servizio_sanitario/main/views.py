from django.shortcuts import render
from . import models
from django.core.paginator import Paginator

def dashboard(request):
    return render(request, 'home.html')




def lista_cittadini(request):
    cittadini = models.Cittadino.objects.all()

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
    sort_field = request.GET.get('sort', 'cognome')  # default
    sort_order = request.GET.get('order', 'asc')
    if sort_order == 'desc':
        sort_field = '-' + sort_field
    try:
        cittadini = cittadini.order_by(sort_field)
    except Exception:
        pass  # se sort_field non è valido, ignora

    # Paginazione
    paginator = Paginator(cittadini, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Colonne da visualizzare
    columns = [
        ('CSSN', 'CSSN'),
        ('nome', 'Nome'),
        ('cognome', 'Cognome'),
        ('data_nascita', 'Data di Nascita'),
        ('città', 'Luogo di Nascita'),
        ('via', 'Indirizzo'),
        ('stato', 'Stato'),
    ]

    context = {
        'filtro_template': 'filtri/filtro_cittadini.html',
        'page_obj': page_obj,
        'cittadini': page_obj.object_list,
        'current_sort': request.GET.get('sort', ''),
        'current_order': request.GET.get('order', ''),
        'columns': columns,
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
    }

    return render(request, 'ospedali.html', context)

def lista_ricoveri(request):
    return render(request, 'ricoveri.html')



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
    })
