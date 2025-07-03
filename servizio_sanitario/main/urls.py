# main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('cittadini/', views.lista_cittadini, name='cittadini'),
    path('ospedali/', views.lista_ospedali, name='ospedali'),
    path('ricoveri/', views.lista_ricoveri, name='lista_ricoveri'), # Nota: `ricoveri` e `lista_ricoveri` possono essere la stessa view. L'importante è che la view `lista_ricoveri` gestisca anche il POST per l'aggiunta.
    path('patologie/', views.lista_patologie, name='patologie'),
    path('modifica_ricovero/<str:pk>/', views.modifica_ricovero, name='modifica_ricovero'),
    path('elimina_ricovero/<str:pk>/', views.elimina_ricovero, name='elimina_ricovero'), # Questa riga è cruciale
    path('trasferisci_ricovero/<str:pk>/', views.trasferisci_ricovero, name='trasferisci_ricovero'),
    path('dichiara_decesso/<str:pk>/', views.dichiara_decesso, name='dichiara_decesso'),
    path('verifica_paziente/', views.verifica_paziente, name='verifica_paziente'),
]