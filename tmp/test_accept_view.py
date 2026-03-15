import os
import sys

sys.path.append('c:\\Users\\milto\\Desktop\\inte2.0-main\\app_django\\Django_inte')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

import json
from django.test import RequestFactory
from apps.admin_app.views import actualizar_estado

factory = RequestFactory()
req = factory.post('/admin/actualizar_estado/69b718cfd3e5662ebcd73927afe3c2e72aa19ae33/', 
                   data=json.dumps({"estado":"Aceptado", "password":"Test1234!"}), 
                   content_type='application/json')
req.session = {'rol':'Administrador', 'usuario_id':'123'}

print(f"content_type is: {req.content_type}")
res = actualizar_estado(req, '69b718cfd3e5662ebcd73927afe3c2e72aa19ae33')
print("Status:", res.status_code)
print("Response:", res.content.decode('utf-8'))
