# views.py

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

