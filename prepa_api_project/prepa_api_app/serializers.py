# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Employe


class EmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employe
        fields = '__all__'  # ou liste explicite des champs