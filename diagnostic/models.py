from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Vehicule(models.Model):
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE)
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    immatriculation = models.CharField(max_length=20, unique=True)
    date_mise_en_circulation = models.DateField()

    def __str__(self):
        return f"{self.marque} {self.modele} - {self.immatriculation}"
    
class Diagnostic(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE)
    type_panne = models.CharField(max_length=200)
    description = models.TextField()
    fichier = models.FileField(upload_to='diagnostics/')
    date_diagnostic = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_panne} - {self.vehicule}"

