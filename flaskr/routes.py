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

        # Inizializza il tipo di variabile se non esiste
        if var_type not in terms_data:
            terms_data[var_type] = {}

        if var_type == "output":
            existing_variables = list(terms_data[var_type].keys())
            if existing_variables and variable_name not in existing_variables:
                return jsonify({
                    "error": f"È possibile inserire solo una variabile {var_type}. Esiste già '{existing_variables[0]}'."
                }), 400

        # Se la variabile non esiste, creala
        if variable_name not in terms_data[var_type]:
            terms_data[var_type][variable_name] = {
                "domain": [domain_min, domain_max],
                "terms": []
            }

        variable_data = terms_data[var_type][variable_name]

        if variable_data['domain'] != [domain_min, domain_max]:
            return jsonify({"error": "Dominio incoerente per la variabile esistente"}), 400

        # Controlla duplicazione del termine
        existing_term = next((t for t in variable_data['terms'] if t['term_name'] == term_name), None)
        if existing_term:
            return jsonify({"error": "Il termine esiste già per questa variabile"}), 400

        new_term = {
            "term_name": term_name,
            "function_type": function_type,
            "params": params
        }

        if var_type == 'output' and defuzzy_type:
            new_term['defuzzy_type'] = defuzzy_type

        variable_data['terms'].append(new_term)

        save_terms(terms_data)

        return jsonify(new_term), 201

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500



@bp.route('/get_terms', methods=['GET'])
def get_terms():
    try:
        terms_data = load_terms()

        if not terms_data:
            return jsonify({"message": "Nessun termine trovato"}), 404
    
        computed_terms = {"input": {}, "output": {}}
        for var_type, variables in terms_data.items():
            for variable_name, variable_data in variables.items():
                # Verifica che 'domain' sia presente prima di procedere
                if 'domain' not in variable_data:
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
                    elif function_type == 'Triangolare-open':
                        y = open_trimf(x, params['a'], params['b'], params['c'])
                    elif function_type == 'Gaussian-open':
                        open_type = params.pop('open_type', 'left')  # rimuove e NON salva
                        y = open_gaussmf(x, params['mean'], params['sigma'], domain_min, domain_max, open_type)
                    elif function_type == 'Trapezoidale-open':
                        y = open_trapmf(x, params['a'], params['b'], params['c'], params['d'])

                    else:
                        continue

                    computed_terms[var_type][variable_name]['terms'].append({
                        "term_name": term_name,
                        "x": x.tolist(),
                        "y": y.tolist()
                    })
        return jsonify(computed_terms), 200

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500
    
def open_trimf(x, a, b, c):
    # Usa la funzione triangolare e forzala a essere 0 fuori dall'intervallo [a, c]
    y = fuzz.trimf(x, [a, b, c])
    y[x < a] = 0
    y[x > c] = 0
    return y
def open_gaussmf(x, mean, sigma, min_val, max_val, open_type):
    y = fuzz.gaussmf(x, mean, sigma)
    
    if open_type == 'left':
        y[x < min_val] = 0  # Forza la coda sinistra a 0
    elif open_type == 'right':
        y[x > max_val] = 0  # Forza la coda destra a 0
    
    return y

def open_trapmf(x, a, b, c, d):
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
        open_type = data.get('open_type')

        # Verifica che tutti i campi obbligatori siano presenti
        missing_fields = []
        if not variable_name: missing_fields.append("variable_name")
        if domain_min is None: missing_fields.append("domain_min")
        if domain_max is None: missing_fields.append("domain_max")
        if not function_type: missing_fields.append("function_type")
        if not params: missing_fields.append("params")

        if missing_fields and open_type != None:
            return jsonify({"error": f"Dati incompleti: {', '.join(missing_fields)}"}), 400

        # Validazioni dei parametri in base al tipo di funzione
        if function_type == 'Triangolare':
            if not all(key in params for key in ['a', 'b', 'c']):
                return jsonify({"error": "Parametri mancanti per la funzione triangolare."}), 400
            if params['a'] > params['b'] or params['b'] > params['c']:
                return jsonify({"error": "I parametri devono rispettare l'ordine a <= b <= c."}), 400

        elif function_type == 'Triangolare-open':
            if open_type == 'left':
                params['b'] = params['a']
            elif open_type == 'right':
                params['b'] = params['c']
            if not all(key in params for key in ['a', 'b', 'c']):
                return jsonify({"error": "Parametri mancanti per la funzione triangolare aperta."}), 400
            if params['a'] > params['b'] or params['b'] > params['c']:
                return jsonify({"error": "I parametri devono rispettare l'ordine a <= b <= c."}), 400

        elif function_type == 'Gaussian':
            if not all(key in params for key in ['mean', 'sigma']):
                return jsonify({"error": "Parametri mancanti per la funzione gaussiana."}), 400
            if params['sigma'] <= 0:
                return jsonify({"error": "Il parametro sigma deve essere maggiore di zero."}), 400

        elif function_type == 'Trapezoidale':
            if not all(key in params for key in ['a', 'b', 'c', 'd']):
                return jsonify({"error": "Parametri mancanti per la funzione trapezoidale."}), 400
            if params['a'] > params['b'] or params['b'] > params['c'] or params['c'] > params['d']:
                return jsonify({"error": "I parametri devono rispettare l'ordine a <= b <= c <= d."}), 400

        elif function_type == 'Trapezoidale-open':
            if open_type == 'left':
                params['b'] = params['a']
            elif open_type == 'right':
                params['c'] = params['d']
            if not all(key in params for key in ['a', 'b', 'c', 'd']):
                return jsonify({"error": "Parametri mancanti per la funzione trapezoidale aperta."}), 400
            if params['a'] > params['b'] or params['b'] > params['c'] or params['c'] > params['d']:
                return jsonify({"error": "I parametri devono rispettare l'ordine a <= b <= c <= d."}), 400

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

                    # Gestione del defuzzy_type
                    if var_type == 'output':
                        if defuzzy_type is None:
                            # Se defuzzy_type è None, rimuovilo
                            if 'defuzzy_type' in term_to_modify:
                                del term_to_modify['defuzzy_type']
                        else:
                            # Altrimenti, aggiorna il defuzzy_type
                            term_to_modify['defuzzy_type'] = defuzzy_type

                    # Salva i dati aggiornati
                    save_terms(terms_data)

                    return jsonify({"message": "Termine modificato con successo!", "term": term_to_modify}), 201

        return jsonify({"error": "Termine non trovato."}), 404

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500
    
@bp.route('/clear_output', methods=['POST'])
def clear_output():
    try:
        data = load_data()
        output_vars = list(data.get("output", {}).keys())

        # Rimuovi completamente la sezione "output" se presente
        if "output" in data:
            del data["output"]

        # Rimuovi tutte le RuleX con quella variabile in output_variable
        rules_to_delete = []
        for key, value in data.items():
            if key.startswith("Rule") and value.get("output_variable") in output_vars:
                rules_to_delete.append(key)
        for rule_key in rules_to_delete:
            del data[rule_key]
        save_data(data)
        
        return jsonify({"message": "Sezione output e regole associate rimosse con successo."}), 200
    except Exception as e:
        return jsonify({"error": f"Errore durante la cancellazione dell'output: {str(e)}"}), 500




#Creazione Regole
@bp.route('/get_variables_and_terms', methods=['GET'])
def get_variables_and_terms():
    try:
        terms_data = load_rule()
        if not terms_data or not isinstance(terms_data, dict):
            return jsonify({"error": "No variables found"}), 404

        formatted_data = {"input": {}, "output": {}}
        for var_type in ["input", "output"]:
            if var_type in terms_data and isinstance(terms_data[var_type], dict):
                for variable_name, variable_data in terms_data[var_type].items():
                    terms = [{"label": term["term_name"], "value": term["term_name"]} 
                            for term in variable_data.get("terms", [])]
                    formatted_data[var_type][variable_name] = terms

        return jsonify(formatted_data), 200

    except Exception as e:
        logging.error(f"Errore in get_variables_and_terms: {e}")
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500



@bp.route('get_rules', methods=['GET'])
def get_rules():
    try:
        rules_data = load_rule()

        if not rules_data or not isinstance(rules_data, dict):
            return jsonify([]), 200  

        rules = [
            {
                "id": key, 
                "inputs": value["inputs"],  # Lista di input
                "output_variable": value["output_variable"], 
                "output_term": value["output_term"]
            }
            for key, value in rules_data.items() if key.startswith("Rule")
        ]

        return jsonify(rules), 200

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500

@bp.route('create_rule', methods=['POST'])
def create_rule():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Nessun dato fornito"}), 400

        inputs = data.get('inputs')  
        output_variable = data.get('output_variable')
        output_term = data.get('output_term')

        # Valida i dati
        if not all([inputs, output_variable, output_term]):
            return jsonify({"error": "Dati incompleti"}), 400

        # Carica le regole esistenti
        rules_data = load_rule()

        # Genera un nuovo ID per la regola
        rule_ids = [int(key.replace("Rule", "")) for key in rules_data.keys() if key.startswith("Rule")]
        next_rule_id = max(rule_ids) + 1 if rule_ids else 0
        rule_id = f"Rule{next_rule_id}"

        # Aggiungi la nuova regola
        rules_data[rule_id] = {
            "inputs": inputs,
            "output_variable": output_variable,
            "output_term": output_term
        }

        # Salva le regole aggiornate
        save_terms(rules_data)

        return jsonify({"message": "Regola creata con successo!", "rule_id": rule_id}), 201

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500
    

    
@bp.route('/infer', methods=['POST'])
def infer():
    try:
        inputs = request.json.get("inputs")
        terms_data = load_terms()
        rules_data = load_rule()
        rules = [
            {
                "inputs": rule["inputs"],
                "output_variable": rule["output_variable"],
                "output_term": rule["output_term"]
            }
            for key, rule in rules_data.items() if key.startswith("Rule")
        ]

        fuzzified = fuzzify_input(terms_data, inputs)
        rule_outputs = apply_rules(fuzzified, rules)
        results = aggregate_and_defuzzify(terms_data, rule_outputs)

        full_result = {
            "inputs": inputs,
            "fuzzified": fuzzified,
            "rule_outputs": rule_outputs,
            "results": results
        }

        for key, rule in rules_data.items():
            if key.startswith("Rule"):
                full_result[key] = rule

        return jsonify(full_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def fuzzify_input(terms_data, inputs):
    fuzzified = {}
    for var_name, value in inputs.items():
        variable = terms_data["input"].get(var_name)
        if not variable:
            continue

        domain_min, domain_max = variable["domain"]
        x = np.linspace(domain_min, domain_max, 100)
        memberships = {}

        for term in variable["terms"]:
            name = term["term_name"]
            ftype = term["function_type"]
            p = term["params"]

            if ftype == "Triangolare":
                y = fuzz.trimf(x, [p["a"], p["b"], p["c"]])
            elif ftype == "Gaussian":
                y = fuzz.gaussmf(x, p["mean"], p["sigma"])
            elif ftype == "Trapezoidale":
                y = fuzz.trapmf(x, [p["a"], p["b"], p["c"], p["d"]])
            elif ftype == "Triangolare-open":
                y = fuzz.trimf(x, [p["a"], p["b"], p["c"]])
                y[x < p["a"]] = 0
                y[x > p["c"]] = 0
            elif ftype == "Gaussian-open":
                y = fuzz.gaussmf(x, p["mean"], p["sigma"])
                y[x < domain_min] = 0
                y[x > domain_max] = 0
            elif ftype == "Trapezoidale-open":
                y = fuzz.trapmf(x, [p["a"], p["b"], p["c"], p["d"]])
                y[x < p["a"]] = 0
                y[x > p["d"]] = 0
            else:
                continue

            mu = np.interp(value, x, y)
            memberships[name] = mu

        fuzzified[var_name] = memberships
    return fuzzified


def apply_rules(fuzzified_inputs, rules):
    rule_outputs = []

    for rule in rules:
        strength = 1.0
        for cond in rule["inputs"]:
            var = cond["input_variable"]
            term = cond["input_term"]
            mu = fuzzified_inputs.get(var, {}).get(term, 0)
            strength = min(strength, mu)

        rule_outputs.append({
            "output_variable": rule["output_variable"],
            "output_term": rule["output_term"],
            "activation": strength
        })
    return rule_outputs


def aggregate_and_defuzzify(terms_data, rule_outputs):
    results = {}

    for var_name in terms_data["output"]:
        domain_min, domain_max = terms_data["output"][var_name]["domain"]
        x = np.linspace(domain_min, domain_max, 100)
        agg_y = np.zeros_like(x)

        for ro in rule_outputs:
            if ro["output_variable"] != var_name:
                continue

            for term in terms_data["output"][var_name]["terms"]:
                if term["term_name"] == ro["output_term"]:
                    ftype = term["function_type"]
                    p = term["params"]

                    if ftype == "Triangolare":
                        y = fuzz.trimf(x, [p["a"], p["b"], p["c"]])
                    elif ftype == "Gaussian":
                        y = fuzz.gaussmf(x, p["mean"], p["sigma"])
                    elif ftype == "Trapezoidale":
                        y = fuzz.trapmf(x, [p["a"], p["b"], p["c"], p["d"]])
                    else:
                        continue

                    agg_y = np.fmax(agg_y, np.fmin(ro["activation"], y))

        defuzzy_method = terms_data["output"][var_name].get("defuzzy_type", "centroid")

        try:
            result = fuzz.defuzz(x, agg_y, defuzzy_method) if np.sum(agg_y) > 0 else 0
        except Exception as e:
            print(f"[ERRORE defuzzificazione] Variabile '{var_name}', metodo '{defuzzy_method}':", e)
            result = 0

        results[var_name] = result

    return results
