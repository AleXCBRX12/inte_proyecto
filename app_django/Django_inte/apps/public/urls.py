from django.urls import path
from . import views

urlpatterns = [
    path('', views.portal_visitante, name='portal_visitante'),
    # Alias para evitar conflictos de reverse() con otras apps que también usan "portal_visitante"
    path('inicio/', views.portal_visitante, name='portal_visitante_public'),
    path('portal_publico/', views.portal_publico, name='portal_publico'),
    path('login/', views.login_view, name='login'),
    path('login/forgot/', views.solicitar_reset, name='solicitar_reset'),
    path('login/reset/<str:token>/', views.reset_password, name='reset_password'),
    path('ver-convocatorias/', views.ver_convocatorias, name='ver_convocatorias'),
    path('aviso-de-privacidad/', views.aviso_privacidad, name='aviso_privacidad'),
    path('contacto/', views.portal_contacto, name='portal_contacto'),
    path('desarrolladores/', views.portal_desarrolladores, name='portal_desarrolladores'),
]
