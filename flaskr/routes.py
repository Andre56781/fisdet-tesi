from flask import Blueprint, request, jsonify, send_file
import os
from flaskr.file_handler import *
from flaskr.file_handler import get_user_file
from dash_application.callbacks import *
import logging
import skfuzzy as fuzz
import numpy as np
import json

bp = Blueprint("api", __name__, url_prefix="/api")

# Salva i dati dell'utente
@bp.route("/save", methods=["POST"])
def save():
    data = request.json
    save_data(data)
    return jsonify({"status": "success"})

# Carica i dati dell'utente
@bp.route("/load", methods=["GET"])
def load():
    data = load_data()
    return jsonify(data)

# Esporta i dati in un file JSON
@bp.route("/export", methods=["GET"])
def export():
    user_file = get_user_file()
    if os.path.exists(user_file):
        return send_file(user_file, as_attachment=True, download_name="data.json")
    return jsonify({"error": "No data found"}), 404

#PROVA

# Crea un nuovo termine
@bp.route('/create_term', methods=['POST'])
def create_term():
    try:
        # Log the incoming data for debugging
        logging.debug(f"Received data: {request.get_data(as_text=True)}")

        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"error": "Formato dati non valido. Deve essere un oggetto JSON."}), 400

        term_name = data.get('term_name')
        variable_name = data.get('variable_name')
        domain_min = data.get('domain_min')
        domain_max = data.get('domain_max')
        function_type = data.get('function_type')
        params = data.get('params')

        missing_fields = []
        if not term_name: missing_fields.append("term_name")
        if not variable_name: missing_fields.append("variable_name")
        if domain_min is None: missing_fields.append("domain_min")
        if domain_max is None: missing_fields.append("domain_max")
        if not function_type: missing_fields.append("function_type")
        if not params: missing_fields.append("params")

        if missing_fields:
            return jsonify({"error": f"Dati incompleti: {', '.join(missing_fields)}"}), 400

        # Carica i dati esistenti
        terms_data = load_terms()

        # Controlla se la variabile esiste già
        if variable_name not in terms_data:
            terms_data[variable_name] = {
                "domain": [domain_min, domain_max],
                "terms": []
            }
        
        variable_data = terms_data[variable_name]

        # Controlla che il dominio sia coerente
        if variable_data['domain'] != [domain_min, domain_max]:
            return jsonify({"error": "Dominio incoerente per la variabile esistente"}), 400

        # Controlla se il termine esiste già
        existing_term = next((t for t in variable_data['terms'] if t['term_name'] == term_name), None)
        if existing_term:
            return jsonify({"error": "Il termine esiste già per questa variabile"}), 400

        # Aggiungi il nuovo termine
        new_term = {
            "term_name": term_name,
            "function_type": function_type,
            "params": params
        }
        variable_data['terms'].append(new_term)

        # Salva i dati aggiornati
        save_terms(terms_data)

        # Log the new term for debugging
        logging.debug(f"Created new term: {new_term}")

        return jsonify(new_term), 201

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500



# Ottieni tutti i termini
@bp.route('/get_terms', methods=['GET'])
def get_terms():
    try:
        terms_data = load_terms()
        if not terms_data:
            return jsonify({}), 404

        # Calcola x e y per ogni termine
        computed_terms = {}
        for variable_name, variable_data in terms_data.items():
            domain_min, domain_max = variable_data['domain']
            x = np.linspace(domain_min, domain_max, 100)
            computed_terms[variable_name] = {
                "domain": [domain_min, domain_max],
                "terms": []
            }

            for term in variable_data['terms']:
                term_name = term['term_name']
                function_type = term['function_type']
                params = term['params']

                if function_type == 'Triangolare':
                    y = fuzz.trimf(x, [params['a'], params['b'], params['c']])
                elif function_type == 'Gaussian':
                    y = fuzz.gaussmf(x, params['mean'], params['sigma'])
                elif function_type == 'Trapezoidale':
                    y = fuzz.trapmf(x, [params['a'], params['b'], params['c'], params['d']])
                else:
                    continue

                computed_terms[variable_name]['terms'].append({
                    "term_name": term_name,
                    "x": x.tolist(),
                    "y": y.tolist()
                })

        return jsonify(computed_terms), 200

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500



# Ottieni un termine specifico
@bp.route('/get_term/<variable_name>/<term_name>', methods=['GET'])
def get_term(variable_name, term_name):
    try:
        terms_data = load_terms()

        # Trova la variabile specifica
        if variable_name not in terms_data:
            return jsonify({"error": "Variabile non trovata."}), 404
        
        variable_data = terms_data[variable_name]

        # Trova il termine specifico
        term_to_get = next((t for t in variable_data['terms'] if t['term_name'] == term_name), None)
        if term_to_get:
            return jsonify(term_to_get), 200

        return jsonify({"error": "Termine non trovato."}), 404

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500



# Elimina un termine
@bp.route('/delete_term/<term_name>', methods=['POST'])
def delete_term(term_name):
    try:
        terms_data = load_terms()
        
        # Trova la variabile e il termine da eliminare
        for variable_name, variable_data in terms_data.items():
            term_to_delete = next((t for t in variable_data['terms'] if t['term_name'] == term_name), None)
            if term_to_delete:
                variable_data['terms'].remove(term_to_delete)
                save_terms(terms_data)
                return jsonify({"message": "Termine eliminato con successo!"}), 200

        return jsonify({"error": "Termine non trovato."}), 404

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500



# Modifica un termine
@bp.route('/modify_term/<term_name>', methods=['PUT'])
def modify_term(term_name):
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"error": "Formato dati non valido. Deve essere un oggetto JSON."}), 400

        variable_name = data.get('variable_name')
        domain_min = data.get('domain_min')
        domain_max = data.get('domain_max')
        function_type = data.get('function_type')
        params = data.get('params')

        missing_fields = []
        if not variable_name: missing_fields.append("variable_name")
        if domain_min is None: missing_fields.append("domain_min")
        if domain_max is None: missing_fields.append("domain_max")
        if not function_type: missing_fields.append("function_type")
        if not params: missing_fields.append("params")

        if missing_fields:
            return jsonify({"error": f"Dati incompleti: {', '.join(missing_fields)}"}), 400

        # Validazioni dei parametri
        if params.get('a') is not None and params.get('b') is not None:
            if params['a'] > params['b']:
                return jsonify({"error": "'a' non può essere maggiore di 'b'."}), 400

        if params.get('b') is not None and params.get('c') is not None:
            if params['b'] > params['c']:
                return jsonify({"error": "'b' non può essere maggiore di 'c'."}), 400

        if params.get('c') is not None and params.get('d') is not None:
            if params['c'] > params['d']:
                return jsonify({"error": "'c' non può essere maggiore di 'd'."}), 400

        # Carica i dati esistenti
        terms_data = load_terms()

        # Controlla se la variabile esiste
        if variable_name not in terms_data:
            return jsonify({"error": "Variabile non trovata."}), 404

        variable_data = terms_data[variable_name]

        # Controlla che il dominio sia coerente
        if variable_data['domain'] != [domain_min, domain_max]:
            return jsonify({"error": "Dominio incoerente per la variabile esistente"}), 400

        # Trova il termine da modificare
        term_to_modify = next((t for t in variable_data['terms'] if t['term_name'] == term_name), None)
        if not term_to_modify:
            return jsonify({"error": "Termine non trovato."}), 404

        # Aggiorna i dettagli del termine
        term_to_modify['function_type'] = function_type
        term_to_modify['params'] = params

        # Salva i dati aggiornati
        save_terms(terms_data)

        return jsonify({"message": "Termine modificato con successo!", "term": term_to_modify}), 201

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500