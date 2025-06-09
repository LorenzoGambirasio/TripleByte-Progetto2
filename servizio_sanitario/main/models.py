from django.db import models

class Cittadino(models.Model):
    CSSN = models.CharField(max_length=16, primary_key=True, db_column='cssn')
    nome = models.CharField(max_length=100, db_column='nome')
    cognome = models.CharField(max_length=100, db_column='cognome')
    data_nascita = models.DateField(db_column='datanascita')
    città = models.CharField(max_length=100, db_column='luogonascita')
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
    codice = models.CharField(max_length=10, primary_key=True, db_column='codospedale')
    nome = models.CharField(max_length=100, db_column='nome')
    città = models.CharField(max_length=100, db_column='città')
    indirizzo = models.CharField(max_length=100, db_column='indirizzo')
    CSSN_direttore = models.ForeignKey(Cittadino, on_delete=models.SET_NULL, null=True, db_column='cssn_id')

    class Meta:
        db_table = 'main_ospedale'
        managed = False

    def __str__(self):
        return self.nome


class Ricovero(models.Model):
    codRicovero = models.CharField(max_length=10, db_column='codricovero', primary_key=True)
    codOspedale = models.ForeignKey(Ospedale, on_delete=models.CASCADE, db_column='codospedale')
    CSSN = models.ForeignKey(Cittadino, on_delete=models.CASCADE, db_column='cssn_id')
    data_ingresso = models.DateField(db_column='data_ingresso')
    durata = models.IntegerField(db_column='durata')
    stato = models.IntegerField(default=0, db_column='stato')
    motivo = models.CharField(max_length=255, db_column='motivo')
    costo = models.DecimalField(max_digits=10, decimal_places=2, db_column='costo')
    
    patologie = models.ManyToManyField(
        'Patologia',
        through='PatologiaRicovero',
        related_name='ricoveri'
    )

    class Meta:
        db_table = 'main_ricovero' 
        managed = False
        unique_together = (('codRicovero', 'codOspedale'),)

    def __str__(self):
        return f"{self.codRicovero} - {self.codOspedale.nome}"

class Patologia(models.Model):
    cod = models.CharField(primary_key=True, max_length=10, db_column='codpatologia')
    nome = models.TextField(max_length=100, db_column='nome')
    criticita = models.IntegerField(db_column='criticita')

    class Meta:
        db_table = 'main_patologia'
        managed = False

    def __str__(self):
        return self.nome


class PatologiaCronica(models.Model):
    cod = models.ForeignKey(Patologia, on_delete=models.CASCADE, db_column='codpatologia_id')

    class Meta:
        db_table = 'main_patologiacronica'
        managed = False

    def __str__(self):
        return f"{self.cod.nome} (Cronica)"


class PatologiaMortale(models.Model):
    cod = models.ForeignKey(Patologia, on_delete=models.CASCADE, db_column='codpatologia_id')

    class Meta:
        db_table = 'main_patologiamortale'
        managed = False

    def __str__(self):
        return f"{self.cod.nome} (Mortale)"


class PatologiaRicovero(models.Model):
    codRicovero = models.ForeignKey(Ricovero, on_delete=models.CASCADE, db_column='codricovero')
    codOspedale = models.ForeignKey(Ospedale, on_delete=models.CASCADE, db_column='codospedale')
    codPatologia = models.ForeignKey(Patologia, on_delete=models.CASCADE, db_column='codpatologia_id')

    class Meta:
        db_table = 'main_patologiaricovero'
        managed = False
        constraints = [
            models.UniqueConstraint(fields=['codRicovero', 'codOspedale', 'codPatologia'], name='pk_patologiaricovero')
        ]

    def __str__(self):
        return f"{self.codRicovero} - {self.codOspedale} - {self.codPatologia.nome}"
    
    
class PatologiaRicoveroView(models.Model):
    id = models.IntegerField(primary_key=True)
    codRicovero = models.CharField(db_column='codricovero')
    codOspedale = models.CharField(db_column='codospedale')
    codPatologia = models.CharField(db_column='codpatologia_id')

    class Meta:
        db_table = 'main_patologiaricovero_view'
        managed = False

