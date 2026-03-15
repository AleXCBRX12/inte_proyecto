from django.urls import path
from . import views

urlpatterns = [
    path('', views.solicitud_ingreso_view, name='solicitud_ingreso'),
]
