from flask import Blueprint, request, jsonify, send_file
import os
from flaskr.file_handler import (
    save_complete_config,
    load_complete_config,
    save_term,
    delete_term as file_delete_term,
    get_variable_terms
)
import logging
import skfuzzy as fuzz
import numpy as np
import json

bp = Blueprint("api", __name__, url_prefix="/api")

# Salva l'intera configurazione
@bp.route("/variables", methods=["POST"])
def save_variables():
    try:
        data = request.json
        save_complete_config(data)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logging.error(f"Save variables error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Carica l'intera configurazione
@bp.route("/variables", methods=["GET"])
def load_variables():
    try:
        config = load_complete_config()
        return jsonify(config), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Gestione termini fuzzy
@bp.route("/terms/<int:variable_index>", methods=["POST", "GET"])
def handle_terms(variable_index):
    try:
        if request.method == "POST":
            term_data = request.json
            if not term_data.get('term_name') or not term_data.get('function_type'):
                return jsonify({"error": "Dati incompleti"}), 400
                
            save_term(variable_index, term_data)
            return jsonify({"status": "success"}), 200
            
        elif request.method == "GET":
            terms = get_variable_terms(variable_index)
            return jsonify({"terms": terms}), 200
            
    except Exception as e:
        logging.error(f"Terms error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route("/terms/<int:variable_index>/<term_name>", methods=["DELETE"])
def delete_term(variable_index, term_name):
    try:
        file_delete_term(variable_index, term_name)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Calcola le funzioni di appartenenza
@bp.route("/calculate_membership/<int:variable_index>", methods=["GET"])
def calculate_membership(variable_index):
    try:
        config = load_complete_config()
        variable = config['variables'].get(str(variable_index), {})
        
        if not variable:
            return jsonify({"error": "Variabile non trovata"}), 404
            
        domain_min = variable.get('domain', [0, 0])[0]
        domain_max = variable.get('domain', [0, 0])[1]
        x = np.linspace(domain_min, domain_max, 100)
        results = []

        for term in variable.get('terms', []):
            params = term.get('params', {})
            y = np.zeros(100)
            
            if term['function_type'] == 'Triangolare':
                y = fuzz.trimf(x, [params['a'], params['b'], params['c']])
            elif term['function_type'] == 'Gaussian':
                y = fuzz.gaussmf(x, params['mean'], params['sigma'])
            elif term['function_type'] == 'Trapezoidale':
                y = fuzz.trapmf(x, [params['a'], params['b'], params['c'], params['d']])
                
            results.append({
                "term_name": term['term_name'],
                "x": x.tolist(),
                "y": y.tolist()
            })

        return jsonify({"terms": results}), 200

    except Exception as e:
        logging.error(f"Membership error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Modifica un termine esistente
@bp.route("/terms/<int:variable_index>/<term_name>", methods=["PUT"])
def modify_term(variable_index, term_name):
    try:
        data = request.json
        config = load_complete_config()
        variable_key = str(variable_index)
        
        if variable_key not in config['variables']:
            return jsonify({"error": "Variabile non trovata"}), 404
            
        terms = config['variables'][variable_key]['terms']
        term_index = next((i for i, t in enumerate(terms) if t['term_name'] == term_name), None)
        
        if term_index is None:
            return jsonify({"error": "Termine non trovato"}), 404
            
        # Validazione parametri
        params = data.get('params', {})
        if data['function_type'] == 'Triangolare':
            if not all(key in params for key in ['a', 'b', 'c']):
                return jsonify({"error": "Parametri mancanti per triangolare"}), 400
            if not (params['a'] <= params['b'] <= params['c']):
                return jsonify({"error": "Parametri non validi (a <= b <= c richiesto)"}), 400
                
        elif data['function_type'] == 'Trapezoidale':
            if not all(key in params for key in ['a', 'b', 'c', 'd']):
                return jsonify({"error": "Parametri mancanti per trapezoidale"}), 400
            if not (params['a'] <= params['b'] <= params['c'] <= params['d']):
                return jsonify({"error": "Parametri non validi (a <= b <= c <= d richiesto)"}), 400
                
        elif data['function_type'] == 'Gaussian':
            if not all(key in params for key in ['mean', 'sigma']):
                return jsonify({"error": "Parametri mancanti per gaussiana"}), 400
            if params['sigma'] <= 0:
                return jsonify({"error": "Sigma deve essere positivo"}), 400
                
        # Aggiorna il termine
        terms[term_index] = {
            'term_name': term_name,
            'function_type': data['function_type'],
            'params': params
        }
        
        save_complete_config(config['variables'])
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"Modify term error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Esporta i dati (mantenuto dalla versione originale)
@bp.route("/export", methods=["GET"])
def export():
    try:
        config = load_complete_config()
        return jsonify(config), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500