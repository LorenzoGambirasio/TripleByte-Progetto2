from django.shortcuts import render
from .models import Cittadino

def dashboard(request):
    return render(request, 'home.html')


def lista_cittadini(request):
    return render(request, 'cittadini.html')


def lista_ospedali(request):
    return render(request, 'ospedali.html')

def lista_ricoveri(request):
    return render(request, 'ricoveri.html')

def lista_patologie(request):
    return render(request, 'patologie.html')
