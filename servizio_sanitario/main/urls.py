from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('cittadini/', views.lista_cittadini, name='cittadini'),
    path('ospedali/', views.lista_ospedali, name='ospedali'),
    path('ricoveri/', views.lista_ricoveri, name='ricoveri'),
    path('patologie/', views.lista_patologie, name='patologie'),
    path('ricoveri/aggiungi/', views.crea_ricovero, name='crea_ricovero'),
    path('ricoveri/modifica/<str:pk>/', views.modifica_ricovero, name='modifica_ricovero'),
    path('ricoveri/elimina/<str:pk>/', views.elimina_ricovero, name='elimina_ricovero'),
]
