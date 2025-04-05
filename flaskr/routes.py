from flask import Blueprint, request, jsonify, send_file, Response
import os
from flaskr.file_handler import *
import logging
import skfuzzy as fuzz
import numpy as np
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
bp = Blueprint("api", __name__, url_prefix="/api")

# Salva i dati dell'utente
@bp.route("/save", methods=["POST"])
def save():
    """Salva i dati inviati dal frontend come file di sessione."""  
    data = request.json
    save_data(data)
    return jsonify({"status": "success"})

# Carica i dati dell'utente
@bp.route("/load", methods=["GET"])
def load():
    """Carica i dati di sessione dell’utente."""  
    data = load_data()
    return jsonify(data)


#Backend 

@bp.route('/create_term', methods=['POST'])
def create_term():
    """Crea un nuovo termine fuzzy e lo salva nel file dei termini."""  
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
                    "error": f"Only one variable can be entered {var_type}. It already exists {existing_variables[0]}'."
                }), 400

        # Se la variabile non esiste, creala
        if variable_name not in terms_data[var_type]:
            terms_data[var_type][variable_name] = {
                "domain": [domain_min, domain_max],
                "terms": []
            }

        variable_data = terms_data[var_type][variable_name]

        if variable_data['domain'] != [domain_min, domain_max]:
            return jsonify({"error": "Inconsistent domain for the existing variable"}), 400

        # Controlla duplicazione del termine
        existing_term = next((t for t in variable_data['terms'] if t['term_name'] == term_name), None)
        if existing_term:
            return jsonify({"error": "The term already exists for this variable"}), 400

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
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@bp.route('/get_terms', methods=['GET'])
def get_terms():
    """Restituisce tutti i termini fuzzy con le coordinate x-y per calcolare il grafico."""  
    try:
        terms_data = load_terms()

        if not terms_data:
            return jsonify({"message": "No terms found"}), 404

        computed_terms = {"input": {}, "output": {}}
        
        for var_type in ["input", "output"]:
            variables = terms_data.get(var_type, {})
            if not isinstance(variables, dict):
                continue

            for variable_name, variable_data in variables.items():
                if not isinstance(variable_data, dict):
                    continue

                terms = variable_data.get('terms', [])

                # === Gestione Classification ===
                if terms and terms[0].get('function_type') == 'Classification':
                    computed_terms[var_type][variable_name] = {
                        "domain": [0, 1],  # dominio dummy per compatibilità
                        "terms": [
                            {
                                "term_name": term['term_name'],
                                "function_type": "Classification"
                            } for term in terms
                        ]
                    }
                    continue

                # === Gestione normale ===
                if 'domain' not in variable_data:
                    continue

                domain_min, domain_max = variable_data['domain']
                x = np.linspace(domain_min, domain_max, 100)
                computed_terms[var_type][variable_name] = {
                    "domain": [domain_min, domain_max],
                    "terms": []
                }

                for term in terms:
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
                        open_type = params.get('open_type', 'left')
                        y = open_gaussmf(x, params['mean'], params['sigma'], domain_min, domain_max, open_type)
                    elif function_type == 'Trapezoidale-open':
                        y = open_trapmf(x, params['a'], params['b'], params['c'], params['d'])
                    else:
                        continue

                    computed_terms[var_type][variable_name]['terms'].append({
                        "term_name": term_name,
                        "x": x.tolist(),
                        "y": y.tolist(),
                        "function_type": function_type
                    })

        return jsonify(computed_terms), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


    
def open_trimf(x, a, b, c):
    """Versione 'open' di una funzione triangolare: forza y=0 fuori da [a, c]."""  
    y = fuzz.trimf(x, [a, b, c])
    y[x < a] = 0
    y[x > c] = 0
    return y
def open_gaussmf(x, mean, sigma, min_val, max_val, open_type):
    """Versione 'open' di una gaussiana: forza y=0 alle estremità del dominio."""  
    y = fuzz.gaussmf(x, mean, sigma)
    
    if open_type == 'left':
        y[x < min_val] = 0  # Forza la coda sinistra a 0
    elif open_type == 'right':
        y[x > max_val] = 0  # Forza la coda destra a 0
    
    return y

def open_trapmf(x, a, b, c, d):
    """Versione 'open' di una trapezoidale: forza y=0 fuori da [a, d]."""  
    y = fuzz.trapmf(x, [a, b, c, d])
    y[x < a] = 0
    y[x > d] = 0
    return y

@bp.route('/get_term/<variable_name>/<term_name>', methods=['GET'])
def get_term(variable_name, term_name):
    """Restituisce i parametri di un singolo termine fuzzy."""  
    try:
        terms_data = load_terms()
        
        for var_type, variables in terms_data.items():
            if variable_name in variables:
                variable_data = variables[variable_name]
                term_to_get = next((t for t in variable_data['terms'] if t['term_name'] == term_name), None)
                if term_to_get:
                    return jsonify(term_to_get), 200

        return jsonify({"error": "No terms found."}), 404

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@bp.route('/delete_term/<term_name>', methods=['POST'])
def delete_term(term_name):
    """Elimina un termine fuzzy dal file in base al nome."""  
    try:
        terms_data = load_terms()
        
        for var_type, variables in terms_data.items():
            for variable_name, variable_data in variables.items():
                term_to_delete = next((t for t in variable_data['terms'] if t['term_name'] == term_name), None)
                if term_to_delete:
                    variable_data['terms'].remove(term_to_delete)
                    save_terms(terms_data)
                    return jsonify({"message": "Term successfully deleted!"}), 200

        return jsonify({"error": "No terms found."}), 404

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@bp.route('/modify_term/<old_term_name>', methods=['PUT'])
def modify_term(old_term_name):
    """Modifica un termine fuzzy esistente con i nuovi parametri (e anche il nome)."""  
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid data format. Must be a JSON object."}), 400

        variable_name = data.get('variable_name')
        new_term_name = data.get('term_name')
        domain_min = data.get('domain_min')
        domain_max = data.get('domain_max')
        function_type = data.get('function_type')
        params = data.get('params')
        defuzzy_type = data.get('defuzzy_type')
        open_type = data.get('open_type')

        # Verifica campi obbligatori
        missing_fields = []
        if not variable_name: missing_fields.append("variable_name")
        if domain_min is None: missing_fields.append("domain_min")
        if domain_max is None: missing_fields.append("domain_max")
        if not function_type: missing_fields.append("function_type")
        if params is None: missing_fields.append("params")

        if missing_fields and open_type is not None:
            return jsonify({"error": f"Incomplete data: {', '.join(missing_fields)}"}), 400

        # Validazioni per tipo funzione
        if function_type == 'Triangolare':
            if not all(key in params for key in ['a', 'b', 'c']):
                return jsonify({"error": "Missing parameters for the triangular function."}), 400
            if params['a'] > params['b'] or params['b'] > params['c']:
                return jsonify({"error": "The parameters must respect the order a <= b <= c."}), 400

        elif function_type == 'Triangolare-open':
            if open_type == 'left':
                params['b'] = params['a']
            elif open_type == 'right':
                params['b'] = params['c']
            if not all(key in params for key in ['a', 'b', 'c']):
                return jsonify({"error": "Missing parameters for the open triangular function."}), 400
            if params['a'] > params['b'] or params['b'] > params['c']:
                return jsonify({"error": "The parameters must respect the order a <= b <= c."}), 400

        elif function_type == 'Gaussian':
            if not all(key in params for key in ['mean', 'sigma']):
                return jsonify({"error": "Missing parameters for the Gaussian function."}), 400
            if params['sigma'] <= 0:
                return jsonify({"error": "The sigma parameter must be greater than zero."}), 400

        elif function_type == 'Trapezoidale':
            if not all(key in params for key in ['a', 'b', 'c', 'd']):
                return jsonify({"error": "Missing parameters for the trapezoidal function."}), 400
            if params['a'] > params['b'] or params['b'] > params['c'] or params['c'] > params['d']:
                return jsonify({"error": "Parameters must respect the order a <= b <= c <= d."}), 400

        elif function_type == 'Trapezoidale-open':
            if open_type == 'left':
                params['b'] = params['a']
            elif open_type == 'right':
                params['c'] = params['d']
            if not all(key in params for key in ['a', 'b', 'c', 'd']):
                return jsonify({"error": "Missing parameters for the open trapezoidal function."}), 400
            if params['a'] > params['b'] or params['b'] > params['c'] or params['c'] > params['d']:
                return jsonify({"error": "Parameters must respect the order a <= b <= c <= d."}), 400

        elif function_type == 'Classification':
            pass  # Nessuna validazione sui parametri

        # Carica i dati esistenti
        terms_data = load_terms()

        # Trova la variabile
        for var_type, variables in terms_data.items():
            if variable_name in variables:
                variable_data = variables[variable_name]
                terms = variable_data.get("terms", [])

                # Trova il termine da modificare
                term_to_modify = next((t for t in terms if t['term_name'] == old_term_name), None)

                if term_to_modify:
                    # Verifica se il nuovo nome è già usato da un altro termine
                    if new_term_name != old_term_name:
                        if any(t['term_name'] == new_term_name for t in terms):
                            return jsonify({"error": f"The new term name '{new_term_name}' already exists."}), 400

                    # Modifica i dati
                    term_to_modify['term_name'] = new_term_name
                    term_to_modify['function_type'] = function_type
                    term_to_modify['params'] = params

                    # Solo output: gestisci defuzzy_type
                    if var_type == 'output':
                        if defuzzy_type is None and 'defuzzy_type' in term_to_modify:
                            del term_to_modify['defuzzy_type']
                        elif defuzzy_type:
                            term_to_modify['defuzzy_type'] = defuzzy_type

                    save_terms(terms_data)
                    return jsonify({"message": "Term successfully modified!", "term": term_to_modify}), 201

        return jsonify({"error": "No terms found."}), 404

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


    
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
        
        return jsonify({"message": "Output section and associated rules successfully removed."}), 200
    except Exception as e:
        return jsonify({"error": f"Error while deleting output: {str(e)}"}), 500




#Creazione Regole
@bp.route('/get_variables_and_terms', methods=['GET'])
def get_variables_and_terms():
    """Restituisce variabili input/output e i relativi termini per la creazione delle regole."""  
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
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



@bp.route('get_rules', methods=['GET'])
def get_rules():
    """Restituisce tutte le regole fuzzy salvate."""  
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
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@bp.route('create_rule', methods=['POST'])
def create_rule():
    """Crea una nuova regola fuzzy e la salva nei dati persistenti."""  
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        inputs = data.get('inputs')  
        output_variable = data.get('output_variable')
        output_term = data.get('output_term')

        # Valida i dati
        if not all([inputs, output_variable, output_term]):
            return jsonify({"error": "Incomplete data"}), 400

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

        return jsonify({"message": "Rule created successfully!", "rule_id": rule_id}), 201

    except Exception as e:
        return jsonify({"error": f" {str(e)}"}), 500
    
@bp.route('/delete_rule/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """Elimina una regola fuzzy in base al suo ID."""  
    try:
        rules_data = load_rule()

        if rule_id in rules_data:
            del rules_data[rule_id]
            save_terms(rules_data)
            return jsonify({"message": "Rule successfully deleted"}), 200
        else:
            return jsonify({"error": "Rule not found"}), 404

    except Exception as e:
        return jsonify({"error": f"Error during deletion: {str(e)}"}), 500

    
@bp.route('/infer', methods=['POST'])
def infer():
    """Esegue l'inferenza fuzzy sui valori di input forniti."""  
    try:
        def compute_membership_y(term, x):
            func = term.get("function_type")
            params = term.get("params", {})

            if func == "Triangolare":
                a, b, c = params["a"], params["b"], params["c"]
                return fuzz.trimf(x, [a, b, c])
            elif func == "Trapezoidale":
                a, b, c, d = params["a"], params["b"], params["c"], params["d"]
                return fuzz.trapmf(x, [a, b, c, d])
            elif func == "Gaussian":
                mean, sigma = params["mean"], params["sigma"]
                return fuzz.gaussmf(x, mean, sigma)

            return np.zeros_like(x)

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

        for var_name, output_var in terms_data["output"].items():
            domain_min, domain_max = output_var["domain"]
            x = np.linspace(domain_min, domain_max, 1000)
            for term in output_var["terms"]:
                term["x"] = x.tolist()
                term["y"] = compute_membership_y(term, x).tolist()

        fuzzified = fuzzify_input(terms_data, inputs)
        rule_outputs = apply_rules(fuzzified, rules)

        for rule_out, original_rule in zip(rule_outputs, rules):
            rule_out["inputs"] = original_rule["inputs"]

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
        print(f"Error during /infer: {e}")
        return jsonify({"error": str(e)}), 500


    
def fuzzify_input(terms_data, inputs):
    """Fuzzifica i valori di input rispetto ai termini fuzzy delle variabili."""  
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
    """Applica le regole fuzzy calcolando l'attivazione per ciascuna."""  
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
    output_terms_by_var = {}

    for rule in rule_outputs:
        var_name = rule["output_variable"]
        term_name = rule["output_term"]
        activation = rule["activation"]

        if var_name not in output_terms_by_var:
            output_terms_by_var[var_name] = {}

        if term_name not in output_terms_by_var[var_name]:
            output_terms_by_var[var_name][term_name] = 0.0

        output_terms_by_var[var_name][term_name] = max(
            output_terms_by_var[var_name][term_name],
            activation
        )

    for var_name, terms in output_terms_by_var.items():
        term_defs = terms_data["output"][var_name]["terms"]
        is_classification = term_defs[0].get("function_type") == "Classification"

        if is_classification:
            best_term = max(terms.items(), key=lambda x: x[1])[0]
            results[var_name] = best_term
        else:
            domain_min, domain_max = terms_data["output"][var_name]["domain"]
            x = np.linspace(domain_min, domain_max, 1000)
            aggregated = np.zeros_like(x)

            for term_def in term_defs:
                term_name = term_def["term_name"]
                y = np.array(term_def["y"])
                weight = terms.get(term_name, 0.0)
                aggregated = np.fmax(aggregated, np.fmin(weight, y))

            if aggregated.sum() == 0:
                results[var_name] = 0
            else:
                result = fuzz.defuzz(x, aggregated, 'centroid')
                results[var_name] = result

    return results



#IMPORT/EXPORT
@bp.route("/export_json", methods=["GET"])
def export_json():
    try:
        data = load_data()

        ordered_data = {}

        # 1. input
        if "input" in data:
            ordered_data["input"] = data["input"]

        # 2. output
        if "output" in data:
            ordered_data["output"] = data["output"]

        # 3. Rule0, Rule1, ..., RuleN (ordinati numericamente)
        rules = {k: v for k, v in data.items() if k.startswith("Rule")}
        sorted_rules = dict(sorted(rules.items(), key=lambda x: int(x[0].replace("Rule", ""))))
        ordered_data.update(sorted_rules)

        # Usa json.dumps per mantenere l’ordine
        json_data = json.dumps(ordered_data, indent=4, ensure_ascii=False)

        return Response(json_data, mimetype='application/json')

    except Exception as e:
        return jsonify({"error": str(e)}), 500





@bp.route("/import_json", methods=["POST"])
def import_json():
    """Importa un file JSON come nuova sessione utente."""  
    try:
        data = request.get_json()

        if not isinstance(data, dict):
            return jsonify({"error": "Invalid format"}), 400

        # Salva direttamente come file di sessione
        save_data(data)

        return jsonify({"message": "Import completed"}), 200

    except Exception as e:
        print(f"Error import:", e)
        return jsonify({"error": f"Error during import: {str(e)}"}), 500

