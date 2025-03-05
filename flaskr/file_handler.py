import os
import json
from flask import request
import hashlib

BASE_DIR = "instance/user_files"

def get_session_id():
    """Crea un identificativo di sessione basato sul browser senza autenticazione."""
    user_info = request.headers.get('User-Agent', '') + request.remote_addr
    user_id = request.cookies.get('user_id', 'default_user')  # Ad esempio, usando un cookie per identificare univocamente l'utente
    session_id = hashlib.md5((user_info + user_id).encode()).hexdigest()
    return session_id

def get_session_file():
    """Restituisce il percorso del file della sessione."""
    session_id = get_session_id()
    return os.path.join(BASE_DIR, f"session_{session_id}.json")

def save_data(data):
    """Salva i dati dell'utente in un file JSON."""
    os.makedirs(BASE_DIR, exist_ok=True)  # Crea la cartella se non esiste
    file_path = get_session_file()
    try:
        with open(file_path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Errore durante il salvataggio dei dati: {e}")
        raise

def load_data():
    """Carica i dati dell'utente dalla sessione, se esistono."""
    file_path = get_session_file()
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Errore durante il caricamento dei dati: {e}")
    return {}  # Ritorna un dizionario vuoto in caso di errore

#Prova

def load_terms():
    """Carica i dati dell'utente dalla sessione, se esistono."""
    file_path = get_session_file()
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def save_terms(new_data):
    """Salva i dati nel file JSON senza sovrascrivere i dati esistenti."""
    file_path = get_session_file()
    
    # Carica i dati esistenti
    existing_data = load_terms()
    
    # Aggiorna i dati esistenti con i nuovi dati
    variable_name = new_data.get('variable_name')
    term_name = new_data.get('term_name')
    
    if variable_name not in existing_data:
        existing_data[variable_name] = {"terms": []}
    
    # Cerca se il termine esiste già
    term_exists = False
    for term in existing_data[variable_name]["terms"]:
        if term['term_name'] == term_name:
            # Aggiorna il termine esistente
            term.update(new_data)
            term_exists = True
            break
    
    if not term_exists:
        # Aggiungi il nuovo termine
        existing_data[variable_name]["terms"].append(new_data)
    
    # Salva i dati aggiornati
    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=4)