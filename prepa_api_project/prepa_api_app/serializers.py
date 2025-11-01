# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

# serializers.py
from rest_framework import serializers

from decimal import Decimal

# IL faut un ModelIASerializer pour sérialiser les instances de ModelIA
from prepa_api_app.models import ModelIA, Alerte

class ModelIASerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelIA
        fields = ['id', 'name', 'version', 'sensibilite', 'typesEpi', 'active', 'created_at']


class AlerteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alerte
        fields = ['id', 'employe', 'modeleIA', 'typeEpiManquants', 'image', 'statut', 'created_at', 'updated_at', 'niveau', 'commentaire']