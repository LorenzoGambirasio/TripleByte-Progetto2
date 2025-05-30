from django.shortcuts import render
from .models import Cittadino
from django.core.paginator import Paginator

def dashboard(request):
    return render(request, 'home.html')




def lista_cittadini(request):
    cittadini = Cittadino.objects.all()
    
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
        cittadini = cittadini.filter(città__icontains=luogo)  # ATTENTO: campo corretto è 'città'
    if indirizzo:
        cittadini = cittadini.filter(via__icontains=indirizzo)
    if cssn:
        cittadini = cittadini.filter(CSSN__icontains=cssn)
    if stato:
        cittadini = [c for c in cittadini if c.stato == stato]  # Per proprietà calcolate

    # Paginazione
    paginator = Paginator(cittadini, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Context
    context = {
        'filtro_template': 'filtri/filtro_cittadini.html',
        'page_obj': page_obj,
        'cittadini': page_obj.object_list,
    }

    return render(request, 'cittadini.html', context)

def lista_ospedali(request):
    return render(request, 'ospedali.html')

def lista_ricoveri(request):
    return render(request, 'ricoveri.html')

def lista_patologie(request):
    return render(request, 'patologie.html')
