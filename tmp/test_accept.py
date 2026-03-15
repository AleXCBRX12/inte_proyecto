import requests
import json

solicitud_id = "69b718cfd3e5662ebcd73927afe3c2e72aa19ae33"

# Start session
session = requests.Session()

# 1. Login as admin
login_data = {
    "correo": "admin@utacapulco.edu.mx",
    "contrasena": "admin123",
    "csrfmiddlewaretoken": ""
}
response = session.get('http://127.0.0.1:8000/')
csrf_token = session.cookies.get('csrftoken')
login_data["csrfmiddlewaretoken"] = csrf_token

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "http://127.0.0.1:8000/"
}
res_login = session.post('http://127.0.0.1:8000/usuarios/login/', data=login_data, headers=headers)
print("Login status:", res_login.status_code)

# 2. Get CSRF for admin action
res_admin = session.get('http://127.0.0.1:8000/admin/solicitudes/')
csrf_token_admin = session.cookies.get('csrftoken')

url_accept = f"http://127.0.0.1:8000/admin/actualizar_estado/{solicitud_id}/"

payload = {
    "estado": "Aceptado",
    "password": "Password1234!"
}

headers_admin = {
    "Content-Type": "application/json",
    "X-CSRFToken": csrf_token_admin,
    "Referer": "http://127.0.0.1:8000/admin/solicitudes/"
}

print(f"Sending POST to: {url_accept}")
res_accept = session.post(url_accept, json=payload, headers=headers_admin)
print("Accept status:", res_accept.status_code)
print("Accept response:", res_accept.text)
