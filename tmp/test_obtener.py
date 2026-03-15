import os
import sys

sys.path.append('c:\\Users\\milto\\Desktop\\inte2.0-main\\app_django\\Django_inte')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

import json
from django.test import RequestFactory
from apps.admin_app.views import obtener_solicitudes

factory = RequestFactory()
req = factory.get('/admin/obtener_solicitudes/')
req.session = {'rol':'Administrador', 'usuario_id':'123'}

res = obtener_solicitudes(req)
print("Status:", res.status_code)
# Get the first item's ID
data = json.loads(res.content.decode('utf-8'))
if data:
    print("First Item ID:", data[0].get('_id'))
    print("Length:", len(data[0].get('_id')))
else:
    print("No items found.")
