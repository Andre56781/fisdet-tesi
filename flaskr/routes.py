from flask import Blueprint, request, jsonify, send_file
import os
from flaskr.file_handler import *
import logging
import skfuzzy as fuzz
import numpy as np
import json

logging.basicConfig(level=logging.DEBUG)
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


#PROVA

@bp.route('/create_term', methods=['POST'])
def create_term():
    try:
        data = request.get_json()
        var_type = data.get('var_type')
        term_name = data.get('term_name')
        variable_name = data.get('variable_name')
        domain_min = data.get('domain_min')
        domain_max = data.get('domain_max')
        function_type = data.get('function_type')
        params = data.get('params')

        if var_type not in ["input", "output"]:
            return jsonify({"error": "var_type deve essere 'input' o 'output'"}), 400

        terms_data = load_terms()

        # Controlla se la variabile esiste già
        if variable_name not in terms_data:
            terms_data[variable_name] = {
                "var_type": var_type,
                "domain": [domain_min, domain_max],
                "terms": []
            }
        
        variable_data = terms_data[variable_name]

        # Controlla che il dominio sia coerente
        if variable_data['domain'] != [domain_min, domain_max]:
            return jsonify({"error": "Dominio incoerente per la variabile esistente"}), 400

        existing_term = next((t for t in variable_data['terms'] if t['term_name'] == term_name), None)
        if existing_term:
            return jsonify({"error": "Il termine esiste già per questa variabile"}), 400

        new_term = {"term_name": term_name, "function_type": function_type, "params": params}
        variable_data['terms'].append(new_term)

        save_terms(terms_data)

        return jsonify(new_term), 201

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500


import logging

# Configura il logger

@bp.route('/get_terms', methods=['GET'])
def get_terms():
    try:
        logging.debug("Inizio del caricamento dei termini.")
        terms_data = load_terms()

        if not terms_data:
            logging.debug("Nessun termine trovato, restituito 404.")
            return jsonify({"message": "Nessun termine trovato"}), 404
    
        computed_terms = {}
        for variable_name, variable_data in terms_data.items():
            # Verifica che 'domain' sia presente prima di procedere
            if 'domain' not in variable_data:
                logging.error(f"Variabile '{variable_name}' non contiene il campo 'domain'. Non sarà elaborata.")
                continue  # Salta questa variabile

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
                elif function_type == 'Triangolare-chiusa':
                    y = closed_trimf(x, params['a'], params['b'], params['c'])
                elif function_type == 'Gaussian-chiusa':
                    y = closed_gaussmf(x, params['mean'], params['sigma'], domain_min, domain_max)
                elif function_type == 'Trapezoidale-chiusa':
                    y = closed_trapmf(x, params['a'], params['b'], params['c'], params['d'])

                else:
                    continue

                computed_terms[variable_name]['terms'].append({
                    "term_name": term_name,
                    "x": x.tolist(),
                    "y": y.tolist()
                })

        logging.debug("Termini calcolati correttamente, restituito 200.")
        return jsonify(computed_terms), 200

    except Exception as e:
        logging.error(f"Errore durante il processo: {str(e)}")
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500
def closed_trimf(x, a, b, c):
    # Usa la funzione triangolare e forzala a essere 0 fuori dall'intervallo [a, c]
    y = fuzz.trimf(x, [a, b, c])
    y[x < a] = 0
    y[x > c] = 0
    return y
def closed_gaussmf(x, mean, sigma, min_val, max_val):
    y = fuzz.gaussmf(x, mean, sigma)
    y[x < min_val] = 0
    y[x > max_val] = 0
    return y
def closed_trapmf(x, a, b, c, d):
    y = fuzz.trapmf(x, [a, b, c, d])
    y[x < a] = 0
    y[x > d] = 0
    return y

@bp.route('/get_term/<variable_name>/<term_name>', methods=['GET'])
def get_term(variable_name, term_name):
    try:
        #print(f"Richiesta per variabile: {variable_name}, termine: {term_name}")  # Debug
        terms_data = load_terms()  # Carica i termini dal file
        
        if variable_name not in terms_data:
            #print("Variabile non trovata")  # Debug
            return jsonify({"error": "Variabile non trovata."}), 404

        variable_data = terms_data[variable_name]
        term_to_get = next((t for t in variable_data['terms'] if t['term_name'] == term_name), None)

        if term_to_get:
            #print("Termine trovato:", term_to_get)  # Debug
            return jsonify(term_to_get), 200  # Restituisce i dati del termine
        else:
            #print("Termine non trovato")  # Debug
            return jsonify({"error": "Termine non trovato."}), 404

    except Exception as e:
        print("Errore:", str(e))  # Debug
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500

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


@bp.route('/modify_term/<term_name>', methods=['PUT'])
def modify_term(term_name):
    try:
        print(request.data)
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