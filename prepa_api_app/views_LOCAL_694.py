# views.py
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from prepa_api_app.models import Employe
from prepa_api_app.serializers import EmployeSerializer


@api_view(['GET'])
def getUsers(request):
    users = Employe.objects.all()
    serializer = EmployeSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def addEmployee(request):
    serializer = EmployeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)