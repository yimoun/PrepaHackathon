# models.py
from django.db import models
from django.contrib.auth.models import User


class Employe(models.Model):
    STATUS_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
        ('CONGE', 'En congé'),
        ('RETRAITE', 'Retraité'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='employe')
    name = models.CharField(max_length=100, verbose_name="Nom")
    surname = models.CharField(max_length=100, verbose_name="Prénom")
    poste = models.CharField(max_length=100, verbose_name="Poste")
    department = models.CharField(max_length=100, verbose_name="Département")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIF', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True) # pour le suivi en BD
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} {self.surname} - {self.poste}"

    class Meta:
        db_table = 'employes'
        ordering = ['name', 'surname']
        verbose_name = "Employé"
        verbose_name_plural = "Employés"


class Technicien(models.Model):
    ROLE_CHOICES = [
        ('SUPPORT', 'Support Technique'),
        ('MAINTENANCE', 'Maintenance'),
        ('RESEAU', 'Réseau'),
        ('SECURITE', 'Sécurité'),
    ]

    employee = models.ForeignKey(Employe,on_delete=models.CASCADE,related_name='techniciens',verbose_name="Employé")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, verbose_name="Rôle")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} {self.employee.surname} - {self.role}"

    class Meta:
        db_table = 'techniciens'
        ordering = ['employee__name']
        verbose_name = "Technicien"
        verbose_name_plural = "Techniciens"

class ModeleIA(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom du modèle")
    version = models.CharField(max_length=100, verbose_name="Version")
    sensibilite = models.IntegerField(verbose_name="Sensibilité")
    typesEpi = models.CharField(max_length=100, verbose_name="Types d'EPI détectés")
    active = models.BooleanField(default=False, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} v{self.version}"

    class Meta:
        db_table = 'modeles_ia'
        ordering = ['name', '-version']  # Ordre décroissant pour version
        verbose_name = "Modèle IA"
        verbose_name_plural = "Modèles IA"


class Alerte(models.Model):

    STATUT_CHOICES = [
        ('NOUVEAU', 'Nouveau'),
        ('EN_COURS', 'En cours de traitement'),
        ('RESOLU', 'Résolu'),
        ('IGNORE', 'Ignoré'),
    ]

    NIVEAU_CHOICES = [
        ('FAIBLE', 'Faible'),
        ('MOYEN', 'Moyen'),
        ('ELEVE', 'Élevé'),
        ('CRITIQUE', 'Critique'),
    ]

    employe = models.ForeignKey(Employe,on_delete=models.CASCADE,related_name='alertes',verbose_name="Employé")
    modeleIA = models.ForeignKey(ModeleIA,on_delete=models.CASCADE,related_name='alertes',verbose_name="Modèle IA")
    typeEpiManquants = models.CharField(max_length=500, verbose_name="EPI manquants")
    image = models.ImageField(upload_to='alertes/%Y/%m/%d/', verbose_name="Image")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='NOUVEAU', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    niveau = models.CharField(max_length=20,choices=NIVEAU_CHOICES,default='MOYEN',verbose_name="Niveau de gravité")
    commentaire = models.TextField(blank=True,verbose_name="Commentaire")

    def __str__(self):
        return f"Alerte {self.id} - {self.employee.name} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        db_table = 'alertes'
        ordering = ['-created_at']
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
