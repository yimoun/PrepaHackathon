from django.urls import include, path
from . import views


urlpatterns = [
    path('', views.getUsers),
    path('add/', views.addEmployee),
]