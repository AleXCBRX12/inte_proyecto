import os
import sys

sys.path.append('c:\\Users\\milto\\Desktop\\inte2.0-main\\app_django\\Django_inte')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

import json
from django.test import RequestFactory
from apps.admin_app.views import actualizar_estado
from config.database.mongo import db
from bson import ObjectId

def test_verify():
    factory = RequestFactory()
    
    # Get a real ID from DB to test
    doc = db.solicitudes.find_one()
    if not doc:
        print("No requests found in DB to test with. Creating a mock one.")
        res = db.solicitudes.insert_one({"nombre_completo": "Test User", "correo": "test@example.com", "estado": "EN PROCESO"})
        doc_id = str(res.inserted_id)
    else:
        doc_id = str(doc['_id'])
    
    print(f"Testing with ID: {doc_id} (Length: {len(doc_id)})")
    
    # Test Aceptar with Password
    payload = {"estado": "Aceptado", "password": "TestPassword123!"}
    req = factory.post(f'/admin/actualizar_estado/{doc_id}/', 
                       data=json.dumps(payload), 
                       content_type='application/json')
    req.session = {'rol':'Administrador', 'usuario_id':'123'}
    
    res = actualizar_estado(req, doc_id)
    print("Status code:", res.status_code)
    print("Response body:", res.content.decode('utf-8'))
    
    if res.status_code == 200:
        print("SUCCESS: Admin action processed correctly.")
    else:
        print("FAILED: Admin action failed.")

if __name__ == "__main__":
    test_verify()
