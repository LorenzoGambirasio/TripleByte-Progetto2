from django.db import models

class Cittadino(models.Model):
    CSSN = models.CharField(max_length=16, primary_key=True)
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    data_nascita = models.DateField()
    città = models.CharField(max_length=100)
    via = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} {self.cognome}"

class Ospedale(models.Model):
    codice = models.CharField(max_length=10, primary_key=True)
    nome = models.CharField(max_length=100)
    città = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=100)
    CSSN_direttore = models.ForeignKey(Cittadino, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nome

class Ricovero(models.Model):
    codice_ricovero = models.CharField(max_length=10, primary_key=True)
    CSSN = models.ForeignKey(Cittadino, on_delete=models.CASCADE)
    codice_ospedale = models.ForeignKey(Ospedale, on_delete=models.CASCADE)
    data_ingresso = models.DateField()
    data_dimissione = models.DateField(null=True, blank=True)
    stato = models.IntegerField()  # 0 = attivo, 1 = trasferito, 2 = dimesso

    def __str__(self):
        return self.codice_ricovero

class Patologia(models.Model):
    codice = models.CharField(max_length=10, primary_key=True)
    descrizione = models.TextField()
    tipo = models.CharField(max_length=10)  # 'cronica' o 'mortale'

    def __str__(self):
        return self.descrizione

class PatologiaRicovero(models.Model):
    id = models.AutoField(primary_key=True)
    codice_ricovero = models.ForeignKey(Ricovero, on_delete=models.CASCADE)
    codice_patologia = models.ForeignKey(Patologia, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('codice_ricovero', 'codice_patologia')

    def __str__(self):
        return f"{self.codice_ricovero} - {self.codice_patologia}"
