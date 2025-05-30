from django.db import models

class Cittadino(models.Model):
    CSSN = models.CharField(max_length=16, primary_key=True, db_column='CSSN')
    nome = models.CharField(max_length=100, db_column='nome')
    cognome = models.CharField(max_length=100, db_column='cognome')
    data_nascita = models.DateField(db_column='dataNascita')
    città = models.CharField(max_length=100, db_column='luogoNascita')
    via = models.CharField(max_length=100, db_column='indirizzo')
    deceduto = models.IntegerField(db_column='deceduto')  # 0 = domiciliato, 1 = deceduto

    
    class Meta:
        db_table = 'main_cittadino'
        managed = False

    def __str__(self):
        return f"{self.nome} {self.cognome}"
    
    @property
    def stato(self):
        if self.deceduto == 1:
            return 'Deceduto'
        from .models import Ricovero
        return 'Ricoverato' if Ricovero.objects.filter(CSSN=self.CSSN, stato=0).exists() else 'Domicilio'



class Ospedale(models.Model):
    codice = models.CharField(max_length=10, primary_key=True, db_column='codOspedale')
    nome = models.CharField(max_length=100, db_column='nome')
    città = models.CharField(max_length=100, db_column='città')
    indirizzo = models.CharField(max_length=100, db_column='indirizzo')
    CSSN_direttore = models.ForeignKey(Cittadino, on_delete=models.SET_NULL, null=True, db_column='CSSN_direttore')

    class Meta:
        db_table = 'main_ospedale'
        managed = False

    def __str__(self):
        return self.nome


class Ricovero(models.Model):
    codice_ricovero = models.CharField(max_length=10, primary_key=True, db_column='codRicovero')
    CSSN = models.ForeignKey(Cittadino, on_delete=models.CASCADE, db_column='CSSN_id')
    codice_ospedale = models.ForeignKey(Ospedale, on_delete=models.CASCADE, db_column='codOspedale_id')
    data_ingresso = models.DateField(db_column='dataIngresso')
    data_dimissione = models.DateField(null=True, blank=True, db_column='dataDimissione')
    stato = models.IntegerField(db_column='stato')

    class Meta:
        db_table = 'main_ricovero'
        managed = False

    def __str__(self):
        return self.codice_ricovero


class Patologia(models.Model):
    codice = models.CharField(max_length=10, primary_key=True, db_column='codice')
    descrizione = models.TextField(db_column='descrizione')
    tipo = models.CharField(max_length=10, db_column='tipo')

    class Meta:
        db_table = 'main_patologia'
        managed = False

    def __str__(self):
        return self.descrizione


class PatologiaCronica(models.Model):
    codice = models.CharField(max_length=10, primary_key=True, db_column='codice')
    descrizione = models.TextField(db_column='descrizione')

    class Meta:
        db_table = 'main_patologiacronica'
        managed = False

    def __str__(self):
        return self.descrizione


class PatologiaMortale(models.Model):
    codice = models.CharField(max_length=10, primary_key=True, db_column='codice')
    descrizione = models.TextField(db_column='descrizione')

    class Meta:
        db_table = 'main_patologiamortale'
        managed = False

    def __str__(self):
        return self.descrizione


class PatologiaRicovero(models.Model):
    codice_ospedale = models.ForeignKey(
        Ospedale, on_delete=models.CASCADE, db_column='codOspedale_id',
        related_name='patologie_ricovero_ospedale'
    )
    codice_ricovero = models.ForeignKey(
        Ricovero, on_delete=models.CASCADE, db_column='codRicovero',
        related_name='patologie_ricovero_ricovero'
    )
    codice_patologia = models.ForeignKey(
        Patologia, on_delete=models.CASCADE, db_column='codPatologia',
        related_name='patologie_ricovero_patologia'
    )

    class Meta:
        db_table = 'main_patologiaricovero'
        managed = False
        constraints = [
            models.UniqueConstraint(
                fields=['codice_ospedale', 'codice_ricovero', 'codice_patologia'],
                name='main_patologiaricovero_pk'
            )
        ]

    def __str__(self):
        return f"{self.codice_ricovero} - {self.codice_patologia}"
