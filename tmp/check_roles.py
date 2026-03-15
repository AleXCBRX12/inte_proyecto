import os
import sys

# Force the Django context to load the actual database
sys.path.append('c:\\Users\\milto\\Desktop\\inte2.0-main\\app_django\\Django_inte')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from config.database.mongo import db

roles = list(db.roles.find())
print("Roles in DB:")
for r in roles:
    print(r)

req = db.solicitudes.find_one()
if req:
    print("\nFirst Solicitude:")
    print(req)
else:
    print("\nNo solicitudes found.")
