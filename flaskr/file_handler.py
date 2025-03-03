import os
import json
from flask import request
import hashlib

BASE_DIR = "instance/user_files"

def get_session_id():
    """Crea un identificativo di sessione basato sul browser senza autenticazione."""
    user_info = request.headers.get('User-Agent', '') + request.remote_addr
    session_id = hashlib.md5(user_info.encode()).hexdigest()
    return session_id

def get_session_file():
    """Restituisce il percorso del file della sessione."""
    session_id = get_session_id()
    return os.path.join(BASE_DIR, f"session_{session_id}.json")

def save_data(data):
    """Salva i dati dell'utente in un file JSON."""
    os.makedirs(BASE_DIR, exist_ok=True)  # Crea la cartella se non esiste
    file_path = get_session_file()
    with open(file_path, "w") as f:
        json.dump(data, f)

def load_data():
    """Carica i dati dell'utente dalla sessione, se esistono."""
    file_path = get_session_file()
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}  # Ritorna un dizionario vuoto se il file non esiste
