from django.urls import path
from . import views

urlpatterns = [
    path('portal_publico/', views.portal_publico, name='portal_publico'),
    path('portal_visitante/', views.portal_visitante, name='portal_visitante'),
    path('panel/', views.panel_admin, name='panel_admin'),
    path('ver-anuncios/', views.lista_anuncios, name='lista_anuncios'),
    path('ver-convocatorias/', views.ver_convocatorias, name='ver_convocatorias'),
    path('documentacion/', views.documentacion_view, name="documentacion"),
    path('documentacion/contrato-vigente/ver/', views.ver_contrato_vigente_usuario, name='ver_contrato_vigente_usuario'),
    path('documentacion/contrato-vigente/descargar/', views.descargar_contrato_vigente_usuario, name='descargar_contrato_vigente_usuario'),
    path('documentacion/contrato/<str:contrato_id>/', views.ver_contrato_usuario, name='ver_contrato_usuario'),
    path('expediente/', views.expediente_usuario, name='expediente_usuario'),
    path('expediente/descargar/<str:documento_id>/', views.descargar_documento_expediente, name='descargar_documento_expediente'),
    path("perfil-emprendedor/", views.perfil_emprendedor, name="perfil_emprendedor"),
    path("calendario/", views.calendario_emprendedor, name="calendario_emprendedor"),
    path("chat/", views.chat_usuario, name="chat_usuario"),
    path("chat/api/mensajes/", views.chat_usuario_mensajes, name="chat_usuario_mensajes"),
    path("chat/api/enviar/", views.chat_usuario_enviar, name="chat_usuario_enviar"),
    path("chat/api/editar/<str:mensaje_id>/", views.chat_usuario_editar, name="chat_usuario_editar"),
    path("chat/api/eliminar/<str:mensaje_id>/", views.chat_usuario_eliminar, name="chat_usuario_eliminar"),
    path("chat/api/archivo/<str:mensaje_id>/", views.chat_usuario_archivo, name="chat_usuario_archivo"),
    path("convocatorias/reaccionar/", views.toggle_reaccion_convocatoria, name="reaccionar_convocatoria"),
    path("convocatorias/comentar/", views.agregar_comentario_convocatoria, name="comentar_convocatoria"),
]
