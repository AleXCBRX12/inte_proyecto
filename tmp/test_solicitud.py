import requests

session = requests.Session()
# Get CSRF token
response = session.get('http://127.0.0.1:8000/solicitudes/')
csrf_token = session.cookies.get('csrftoken')

print("CSRF Token:", csrf_token)

data = {
    "nombre_completo": "Test User",
    "correo": "test@utacapulco.edu.mx",
    "csrfmiddlewaretoken": csrf_token
}

headers = {
    "Content-Type": "application/json",
    "X-CSRFToken": csrf_token,
    "Referer": "http://127.0.0.1:8000/solicitudes/"
}

response = session.post('http://127.0.0.1:8000/solicitudes/', json=data, headers=headers)

print("Status Code:", response.status_code)
print("Response Headers:", response.headers)
print("Response Text:", response.text)
