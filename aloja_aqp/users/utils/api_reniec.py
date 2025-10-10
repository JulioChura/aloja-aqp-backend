import os
import unicodedata
import requests
from decouple import config

API_KEY = config('DECOLECTA_API_KEY')

RENIEC_URL = "https://api.decolecta.com/v1/reniec/dni"

def normalize_name(name: str) -> str:
    """Quita tildes y pasa a minúsculas"""
    name = name.lower()
    name = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )
    return name

def verificar_dni(dni: str):
    """Consulta RENIEC y devuelve nombres y apellidos oficiales del DNI"""
    if not API_KEY:
        print("No se encontró API_KEY en las variables de entorno.")
        return None

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        resp = requests.get(RENIEC_URL, headers=headers, params={"numero": dni}, timeout=10)
        print("Status code RENIEC:", resp.status_code)
        print("Respuesta cruda:", resp.text)

        if resp.status_code == 200:
            data = resp.json()
            print("Datos JSON recibidos:", data)
            return {
                "first_name": data.get("first_name", ""),
                "last_name_1": data.get("first_last_name", ""),
                "last_name_2": data.get("second_last_name", "")
            }

        elif resp.status_code == 401:
            print("401 Unauthorized — API key inválida.")
        elif resp.status_code == 429:
            print("429 Rate limit — Límite de peticiones alcanzado.")
        else:
            print(f"Error {resp.status_code}: {resp.text}")

        return None

    except requests.RequestException as e:
        print("Error de conexión a RENIEC:", e)
        return None
