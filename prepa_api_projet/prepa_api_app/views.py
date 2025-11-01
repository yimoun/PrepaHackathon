# views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Employe
from .serializers import EmployeSerializer


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