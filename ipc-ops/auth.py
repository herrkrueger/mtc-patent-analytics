import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_access_token():
    key = os.getenv("OPS_KEY")
    secret = os.getenv("OPS_SECRET")

    if not key or not secret:
        raise EnvironmentError("Bitte setze OPS_KEY und OPS_SECRET in der .env-Datei.")

    url = "https://ops.epo.org/3.2/auth/accesstoken"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data, auth=(key, secret))

    if response.status_code != 200:
        raise RuntimeError(f"Authentifizierung fehlgeschlagen: {response.status_code} – {response.text}")

    return response.json()["access_token"]
