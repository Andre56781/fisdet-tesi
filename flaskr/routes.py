from flask import Blueprint, request, jsonify, send_file
import os
from flaskr.file_handler import *
import logging
import skfuzzy as fuzz
import numpy as np
import json
import logging

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


#Backend 

@bp.route('/create_term', methods=['POST'])
def create_term():
    try:
        data = request.get_json()
        #print("Dati ricevuti:", data)  # Debug

        var_type = data.get('var_type')
        term_name = data.get('term_name')
        variable_name = data.get('variable_name')
        domain_min = data.get('domain_min')
        domain_max = data.get('domain_max')
        function_type = data.get('function_type')
        params = data.get('params')
        defuzzy_type = data.get('defuzzy_type') 

        if var_type not in ["input", "output"]:
            return jsonify({"error": "var_type deve essere 'input' o 'output'"}), 400

        terms_data = load_terms()
        #print("Termini caricati:", terms_data)  # Debug

        # Inizializza il tipo di variabile se non esiste
        if var_type not in terms_data:
            terms_data[var_type] = {}

        # Controlla se la variabile esiste già
        if variable_name not in terms_data[var_type]:
            terms_data[var_type][variable_name] = {
                "domain": [domain_min, domain_max],
                "terms": []
            }

        variable_data = terms_data[var_type][variable_name]

        # Controlla che il dominio sia coerente
        if variable_data['domain'] != [domain_min, domain_max]:
            return jsonify({"error": "Dominio incoerente per la variabile esistente"}), 400

        existing_term = next((t for t in variable_data['terms'] if t['term_name'] == term_name), None)
        if existing_term:
            return jsonify({"error": "Il termine esiste già per questa variabile"}), 400

        new_term = {"term_name": term_name, "function_type": function_type, "params": params}
        
        # Aggiungi defuzzy_type solo se var_type è 'output'
        if var_type == 'output' and defuzzy_type:
            new_term['defuzzy_type'] = defuzzy_type

        variable_data['terms'].append(new_term)

        save_terms(terms_data)
        #print("Termini salvati:", terms_data)  # Debug

        return jsonify(new_term), 201

    except Exception as e:
        #print("Errore durante la creazione del termine:", str(e))  # Debug
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500


@bp.route('/get_terms', methods=['GET'])
def get_terms():
    try:
        logging.debug("Inizio del caricamento dei termini.")
        terms_data = load_terms()

        if not terms_data:
            logging.debug("Nessun termine trovato, restituito 404.")
            return jsonify({"message": "Nessun termine trovato"}), 404
    
        computed_terms = {"input": {}, "output": {}}
        for var_type, variables in terms_data.items():
            for variable_name, variable_data in variables.items():
                # Verifica che 'domain' sia presente prima di procedere
                if 'domain' not in variable_data:
                    #logging.error(f"Variabile '{variable_name}' non contiene il campo 'domain'. Non sarà elaborata.") # Debug
                    continue  # Salta questa variabile

                domain_min, domain_max = variable_data['domain']
                x = np.linspace(domain_min, domain_max, 100)
                computed_terms[var_type][variable_name] = {
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

                    computed_terms[var_type][variable_name]['terms'].append({
                        "term_name": term_name,
                        "x": x.tolist(),
                        "y": y.tolist()
                    })
        #logging.debug("Termini calcolati correttamente, restituito 200.") # Debug
        return jsonify(computed_terms), 200

    except Exception as e:
        #logging.error(f"Errore durante il processo: {str(e)}")# Debug
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
        terms_data = load_terms()
        
        for var_type, variables in terms_data.items():
            if variable_name in variables:
                variable_data = variables[variable_name]
                term_to_get = next((t for t in variable_data['terms'] if t['term_name'] == term_name), None)
                if term_to_get:
                    return jsonify(term_to_get), 200

        return jsonify({"error": "Termine non trovato."}), 404

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500

@bp.route('/delete_term/<term_name>', methods=['POST'])
def delete_term(term_name):
    try:
        terms_data = load_terms()
        
        for var_type, variables in terms_data.items():
            for variable_name, variable_data in variables.items():
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
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"error": "Formato dati non valido. Deve essere un oggetto JSON."}), 400
        
        variable_name = data.get('variable_name')
        domain_min = data.get('domain_min')
        domain_max = data.get('domain_max')
        function_type = data.get('function_type')
        params = data.get('params')
        defuzzy_type = data.get('defuzzy_type') 

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

        # Trova il termine da modificare
        for var_type, variables in terms_data.items():
            if variable_name in variables:
                variable_data = variables[variable_name]
                term_to_modify = next((t for t in variable_data['terms'] if t['term_name'] == term_name), None)
                if term_to_modify:
                    # Aggiorna i dettagli del termine
                    term_to_modify['function_type'] = function_type
                    term_to_modify['params'] = params

                    # Aggiungi defuzzy_type solo se var_type è 'output'
                    if var_type == 'output' and defuzzy_type:
                        term_to_modify['defuzzy_type'] = defuzzy_type

                    # Salva i dati aggiornati
                    save_terms(terms_data)

                    return jsonify({"message": "Termine modificato con successo!", "term": term_to_modify}), 201

        return jsonify({"error": "Termine non trovato."}), 404

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500
    
    
#Creazione Regole
@bp.route('/get_variables_and_terms', methods=['GET'])
def get_variables_and_terms():
    try:
        terms_data = load_rule()

        if not terms_data:
            return jsonify({"error": "No variables found"}), 404

        # Verifica che terms_data sia un dizionario
        if not isinstance(terms_data, dict):
            return jsonify({"error": "Invalid data structure"}), 400

        formatted_data = {
            "input": {},
            "output": {}
        }

        # Itera solo sulle chiavi "input" e "output"
        for var_type in ["input", "output"]:
            if var_type in terms_data:
                variables = terms_data[var_type]

                if not isinstance(variables, dict):
                    continue  # Salta se non è un dizionario

                for variable_name, variable_data in variables.items():
                    terms = []

                    # Verifica se "terms" esiste per la variabile
                    if isinstance(variable_data, dict) and "terms" in variable_data:
                        terms = [{"label": term["term_name"], "value": term["term_name"]} for term in variable_data["terms"]]
                    
                    formatted_data[var_type][variable_name] = terms

        return jsonify(formatted_data), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



@bp.route('/api/get_rules', methods=['GET'])
def get_rules():
    try:
        logging.info("Richiesta ricevuta su /api/get_rules")  # Log della richiesta
        rules_data = load_rule()
        logging.info(f"Loaded rules data: {rules_data}")  # Log dei dati caricati DEBUG

        if not rules_data:
            return jsonify({"error": "No rules found"}), 404

        rules = []
        for key, value in rules_data.items():
            if key.startswith("Rule"):
                rules.append({
                    "id": key,
                    "input_variable": value["input_variable"],
                    "input_term": value["input_term"],
                    "output_variable": value["output_variable"],
                    "output_term": value["output_term"]
                })

        logging.info(f"Returning rules: {rules}")  # Log delle regole restituite DEBUG
        return jsonify(rules), 200

    except Exception as e:
        logging.error(f"Error in get_rules: {str(e)}")  # Log dell'errore DEBUG
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@bp.route('/create_rule', methods=['POST'])
def create_rule():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Nessun dato fornito"}), 400

        input_variable = data.get('input_variable')
        input_term = data.get('input_term')
        output_variable = data.get('output_variable')
        output_term = data.get('output_term')

        if not all([input_variable, input_term, output_variable, output_term]):
            return jsonify({"error": "Dati incompleti"}), 400

        rules_data = load_rule()
        rule_id = f"Rule{len(rules_data)}"
        rules_data[rule_id] = {
            "input_variable": input_variable,
            "input_term": input_term,
            "output_variable": output_variable,
            "output_term": output_term
        }

        save_terms(rules_data)
        return jsonify({"message": "Regola creata con successo!", "rule_id": rule_id}), 201

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500
    
@bp.route('/delete_rule/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    try:
        rules_data = load_rule()
        if rule_id not in rules_data:
            return jsonify({"error": "Regola non trovata"}), 404

        del rules_data[rule_id]
        save_terms(rules_data)
        return jsonify({"message": "Regola eliminata con successo!"}), 200

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500