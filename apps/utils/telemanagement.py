import requests, environ, os, warnings
from pathlib import Path
from urllib3.exceptions import InsecureRequestWarning

# Suppress warnings
warnings.simplefilter("ignore", InsecureRequestWarning)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# initialize environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


class Telemanagement:
    # En el contratuctor se realiza la autenticación a la api y se guarda el token para realizar las peticiones
    def __init__(self):
        payload = { "username": env('TELEGESTION_USER'), "password": env('TELEGESTION_PASS')}
        response = requests.post(f"{env('TELEGESTION_URL')}/user/login", json=payload, verify=False)
        login_data = response.json()
        self.token = login_data["data"]["access_token"]

    # Trae toda la información de telegestión del nodo
    def getAllInformationFromNode(self, id):
        headers = { "x-access-token": self.token}
        output = requests.get(f"{env('TELEGESTION_URL')}/api/getAll/{id}", headers=headers, verify=False)
        return output
    
