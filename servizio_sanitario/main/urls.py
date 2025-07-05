from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('cittadini/', views.lista_cittadini, name='cittadini'),
    path('ospedali/', views.lista_ospedali, name='ospedali'),
    path('ricoveri/', views.lista_ricoveri, name='lista_ricoveri'), 
    path('patologie/', views.lista_patologie, name='patologie'),
    path('modifica_ricovero/<str:pk>/', views.modifica_ricovero, name='modifica_ricovero'),
    path('elimina_ricovero/<str:pk>/', views.elimina_ricovero, name='elimina_ricovero'), 
    path('trasferisci_ricovero/<str:pk>/', views.trasferisci_ricovero, name='trasferisci_ricovero'),
    
    # NUOVI URL PER IL DECESSO
    path('dichiara_decesso/<str:pk>/', views.dichiara_decesso, name='dichiara_decesso'),
    path('verifica_password/', views.verifica_password, name='verifica_password'),
    path('modifica_causa_decesso/<str:pk>/', views.modifica_causa_decesso, name='modifica_causa_decesso'),

    path('verifica_paziente/', views.verifica_paziente, name='verifica_paziente'),
    path('cerca-patologie/', views.cerca_patologie, name='cerca_patologie'),
    path('aggiungi-nuovo-paziente/', views.aggiungi_nuovo_paziente, name='aggiungi_nuovo_paziente'),
]