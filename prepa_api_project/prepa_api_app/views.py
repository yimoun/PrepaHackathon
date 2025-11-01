# views.py

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

#Ici il faudrait des View (ViewSets ou APIViews) pour gérer les endpoints de l’API.
#Ces views utiliseront les serializers définis dans serializers.py pour valider et transformer les données.
#Elles interagiront avec les modèles de Django pour effectuer des opérations CRUD (Créer, Lire, Mettre à jour, Supprimer) sur les données.

#Une view par exmple pour gerer l'historique d'un Model d'API et ou d'obtenir les API toutes

# Faut penser qu'on fera des diagrammes cotÉ FrontEND 