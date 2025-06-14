from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('cittadini/', views.lista_cittadini, name='cittadini'),
    path('ospedali/', views.lista_ospedali, name='ospedali'),
    path('ricoveri/', views.lista_ricoveri, name='ricoveri'),
    path('patologie/', views.lista_patologie, name='patologie'),
    path('ricoveri/aggiungi/', views.aggiungi_ricovero, name='aggiungi_ricovero'),
    path('ricoveri/modifica/<str:pk>/', views.modifica_ricovero, name='modifica_ricovero'),
    path('ricoveri/elimina/<str:pk>/', views.elimina_ricovero, name='elimina_ricovero'),
    path('ricoveri/decesso/<str:pk>/', views.dichiara_decesso, name='inserisci_decesso'),
    path('ricoveri/trasferisci/<str:pk>/', views.trasferisci_ricovero, name='trasferisci_ricovero'),
    path('ajax/verifica_paziente/', views.verifica_paziente, name='verifica_paziente'),

]
