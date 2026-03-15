from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', include('apps.public.urls')),
      path('solicitudes/', include('apps.solicitudes.urls')),  
      path('admin/', include('apps.admin_app.urls')),
      path('usuarios/', include('apps.usuarios.urls')),

]
