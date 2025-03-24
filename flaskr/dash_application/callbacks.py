import dash
import base64
from dash import dcc, html, Input, Output, State, ctx, ALL, MATCH, callback_context
import plotly.graph_objects as go
import requests
import dash_bootstrap_components as dbc
import json
from flaskr import file_handler
from flaskr.file_handler import load_data, export_session
from datetime import datetime
import re
from dash.exceptions import PreventUpdate


def register_callbacks(dash_app):

    #IMPORT/EXPORT JSON
    @dash_app.callback(
        Output("download-json", "data"),
        Output("export-loading", "children"),
        Input("btn-json-export", "n_clicks"),
        prevent_initial_call=True
    )
    def handle_json_export(n_clicks):
        if n_clicks:
            try:
                session_data = file_handler.load_data()
                
                # Validazione struttura dati
                required_keys = {"variables", "terms", "rules"}
                if not required_keys.issubset(session_data.keys()):
                    missing = required_keys - session_data.keys()
                    raise ValueError(f"Dati mancanti: {', '.join(missing)}")
                
                # Preparazione dati per l'esportazione
                export_data = file_handler.export_session(session_data)
                
                return (
                    {
                        "content": json.dumps(export_data, indent=4, ensure_ascii=False),
                        "filename": f"fis_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    },
                    ""  # Contenuto vuoto per il loading
                )
            except Exception as e:
                print(f"Errore esportazione: {str(e)}")
                return dash.no_update, ""
        return dash.no_update, ""

    # Callback per l'importazione JSON
    @dash_app.callback(
        Output('session-store', 'data'),
        Input('upload-fis', 'contents'),
        State('upload-fis', 'filename'),
        prevent_initial_call=True
    )
    def handle_json_import(contents, filename):
        if contents is not None:
            try:
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                
                uploaded_data = json.loads(decoded.decode('utf-8'))

                validated_data = file_handler.import_json_data(uploaded_data)
                
                # Salvataggio nella sessione corrente
                current_data = file_handler.load_data()
                current_data.update({
                    "variables": validated_data["variables"],
                    "terms": validated_data["terms"],
                    "rules": validated_data["rules"]
                })
                file_handler.save_data(current_data)
                
                return current_data
                
            except Exception as e:
                print(f"Errore importazione: {str(e)}")
                return dash.no_update
        
        return dash.no_update


    #HOME_PAGE CALLBACKS
    @dash_app.callback(
    Output('url', 'pathname'),
    Input('upload-fis', 'contents'),
    prevent_initial_call=True
    )
    def handle_upload(contents):
        if contents:
            return '/report'
        return dash.no_update

    # Callback per la gestione della sottomissione del modal e la visualizzazione del contenuto principale
    @dash_app.callback(
            [Output("variable-modal", "is_open"),
            Output("main-content", "style"),
            Output("num-variables-store", "data")],
            [Input("modal-submit-button", "n_clicks")],
            [State("num-variables-input", "value")]
        )
    def handle_modal_submit(n_clicks, num_variables):
        if not n_clicks:
            return [True, {"display": "none"}, None]

        try:
            num_vars = int(num_variables)
            if num_vars < 1:
                raise ValueError

            file_handler.save_data({"num_variables": num_vars})
            return [False, {"display": "block", "position": "relative"}, num_vars]
        except:
            return [True, {"display": "none"}, None]

    # Callback per aggiornare il titolo della variabile (es. "Variabile X di Y")
    @dash_app.callback(
        Output("variable-title", "children"),
        Input("var-type-store", "data"),
        [Input("current-index", "data"),
        Input("num-variables-store", "data")]
    )
    def update_title(var_type, current_index, num_vars):
        if num_vars is None or current_index is None:
            return ""
        try:
            current_index = int(current_index)
        except (ValueError, TypeError):
            return "Errore: Indice della variabile non valido."

        return f"Creation of  {var_type} Variables {current_index + 1} of {num_vars}"

    # Callback per la navigazione tra le variabili
    @dash_app.callback(
    [Output("current-index", "data"),
    Output("back-button", "style"),
    Output("next-button", "style")],
    [Input("next-button", "n_clicks"),
    Input("back-button", "n_clicks"),
    Input("num-variables-store", "data")], 
    [State("current-index", "data")],
    prevent_initial_call=False  
)
    def navigate_variables(next_clicks, back_clicks, num_variables, current_index):
        ctx = dash.callback_context

        if not ctx.triggered:
            # Se il callback è stato eseguito all'avvio, imposta current_index a 0
            current_index = 0 if current_index is None else current_index
        else:
            # Altrimenti, gestisci i click sui pulsanti
            triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if triggered_id == "next-button" and current_index < num_variables - 1:
                current_index += 1
            elif triggered_id == "back-button" and current_index > 0:
                current_index -= 1

        # Gestione della visibilità dei pulsanti
        if num_variables == 1:
            back_button_style = {'display': 'none'}
            next_button_style = {'display': 'none'}
        else:
            back_button_style = {'display': 'none'} if current_index == 0 else {'display': 'inline-block'}
            num_variables = num_variables or 0
            next_button_style = {'display': 'none'} if current_index == num_variables-1 else {'display': 'inline-block'}


        return current_index, back_button_style, next_button_style

    @dash_app.callback(
        Output('open-type', 'value'),  
        Input('open-type-radio', 'value')  
    )
    def update_open_type(selected_value):
        return selected_value

    @dash_app.callback(
        [Output('defuzzy-type', 'value'),  
        Output('defuzzy-type', 'disabled')],  
        Input('classification-checkbox', 'value')  
    )
    def toggle_defuzzy_visibility(classification_value):
        default_value = 'centroid'
        
        if classification_value is None:
            return default_value, False 
        
        if 'Classification' in classification_value:
            return "Classification", True 
        else:
            return default_value, False  


    @dash_app.callback(
        Output('params-container', 'children'),
        Input('var-type-store', 'data'),
        [Input('function-type', 'value'),
        Input('num-variables-store', 'data'),
        Input('current-index', 'data'),
        Input('open-type', 'value')]
    )
    def update_params(var_type, function_type, num_variables, current_index, open_type):
        params = []
        
        if num_variables is None or current_index is None:
            return []

        # Aggiunta di opzioni di apertura per variabili input ai bordi
        if var_type == 'input':
            params.append(dbc.RadioItems(
                id='open-type-radio',
                options=[
                    {'label': 'Left open', 'value': 'left'},
                    {'label': 'Right open', 'value': 'right'},
                ],
                inline=True,
                value=open_type  
            ))

        if var_type == 'output':
            params.append(dbc.Checklist(
                id='classification-checkbox', 
                options=[
                    {'label': 'Classification', 'value': 'Classification'},
                ],
                inline=True,
                value=[open_type] if open_type else []
            ))

        # Parametri per funzione Triangolare
        if function_type == 'Triangolare':
            params.append(dbc.Label("Parametro a:"))
            params.append(dbc.Input(id='param-a', type='number', value='', required=True))
            
            params.append(dbc.Label("Parametro b:"))
            if open_type == 'left':  
                params.append(dbc.Input(id='param-b', type='number', value='', disabled=True))
            elif open_type == 'right':
                params.append(dbc.Input(id='param-b', type='number', value='', disabled=True))
            elif open_type is None:
                params.append(dbc.Input(id='param-b', type='number', value='', required=True))
                
            params.append(dbc.Label("Parametro c:"))
            params.append(dbc.Input(id='param-c', type='number', value='', required=True))
            
            # Parametri invisibili
            params.append(dbc.Input(id='param-d', style={'display': 'none'}))
            params.append(dbc.Input(id='param-mean', style={'display': 'none'}))
            params.append(dbc.Input(id='param-sigma', style={'display': 'none'}))

        # Parametri per funzione Gaussian
        elif function_type == 'Gaussian':
            params.append(dbc.Label("Parametro Mean:"))
            params.append(dbc.Input(id='param-mean', type='number', value='', required=True))
            params.append(dbc.Label("Parametro Sigma:"))
            params.append(dbc.Input(id='param-sigma', type='number', value='', required=True))

            # Parametri invisibili
            params.append(dbc.Input(id='param-b', style={'display': 'none'}))
            params.append(dbc.Input(id='param-c', style={'display': 'none'}))
            params.append(dbc.Input(id='param-d', style={'display': 'none'}))

        # Se il tipo di funzione è "Trapezoidale"
        elif function_type == 'Trapezoidale':
            params.append(dbc.Label("Parametro a:"))
            params.append(dbc.Input(id='param-a', type='number', value='', required=True))
            
            params.append(dbc.Label("Parametro b:"))
            if open_type == 'left':  
                params.append(dbc.Input(id='param-b', type='number', value='', disabled=True))
            else:
                params.append(dbc.Input(id='param-b', type='number', value='', required=True))
            
            params.append(dbc.Label("Parametro c:"))
            if open_type == 'right':  
                params.append(dbc.Input(id='param-c', type='number', value='', disabled=True))
            else:
                params.append(dbc.Input(id='param-c', type='number', value='', required=True))
                
            params.append(dbc.Label("Parametro d:"))
            params.append(dbc.Input(id='param-d', type='number', value='', required=True))

            params.append(dbc.Input(id='param-mean', style={'display': 'none'}))
            params.append(dbc.Input(id='param-sigma', style={'display': 'none'}))

        return params

    @dash_app.callback(
    Output('defuzzy-type', 'invalid'),
    Input('defuzzy-type', 'value'),
    prevent_initial_call=True
)
    def validate_defuzzy_type(selected_value):
        if selected_value is None:
            return True  
        return False  

    @dash_app.callback(
        [
            Output('terms-list', 'children', allow_duplicate=True),
            Output('message', 'children'),
            Output('graph', 'figure', allow_duplicate=True),
            Output('term-name', 'value', allow_duplicate=True),  
            Output('param-a', 'value', allow_duplicate=True),     
            Output('param-b', 'value', allow_duplicate=True),     
            Output('param-c', 'value', allow_duplicate=True),     
            Output('param-d', 'value', allow_duplicate=True),     
            Output('param-mean', 'value', allow_duplicate=True),  
            Output('param-sigma', 'value', allow_duplicate=True), 
            Output('create-term-btn', 'children')
        ],
        [
            Input('create-term-btn', 'n_clicks'),
            Input('delete-term-btn', 'n_clicks'),
            Input('modify-term-btn', 'n_clicks'),
        ],
        [
            State('open-type', 'value'),
            State('var-type-store', 'data'), 
            State('variable-name', 'value'),
            State('domain-min', 'value'),
            State('domain-max', 'value'),
            State('function-type', 'value'),
            State('term-name', 'value'),
            State('param-a', 'value'),
            State('param-b', 'value'),
            State('param-c', 'value'),
            State('param-d', 'value'),
            State('param-mean', 'value'),
            State('param-sigma', 'value'),
            State('defuzzy-type', 'value'), 
            State('create-term-btn', 'children'),
            State('selected-term', 'data'),
            State('classification-checkbox', 'value')  
        ],
        prevent_initial_call=True
    )
    def handle_terms(create_clicks, delete_clicks, modify_clicks, open_type,
                    var_type, variable_name, domain_min, domain_max, function_type,
                    term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma,
                    defuzzy_type, button_label, selected_term, classification_value): 
        ctx = dash.ctx

        if not ctx.triggered:
            return [dash.no_update] * 11

        triggered_id = ctx.triggered[0]['prop_id']

        # Se siamo nella pagina di input, imposta defuzzy_type e classification_value a None
        if var_type == "input":
            defuzzy_type = None
            classification_value = None
            
        if var_type == "output":
            open_type = None
        
        if open_type is None:
            open_type = []

        if isinstance(open_type, str) and ('left' in open_type or 'right' in open_type):
            function_type = f"{function_type}-open"
        
        # Verifica che var_type sia valido
        if var_type not in ['input', 'output']:
            return [dash.no_update,
                    "Errore: var_type deve essere 'input' o 'output'",
                    dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                    dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                    'Crea Termine']

        # --- Creazione del Termine ---
        if triggered_id == 'create-term-btn.n_clicks':             
            if button_label == 'Salva Modifica':
                # Esegui la modifica e poi ricarica la lista aggiornata
                terms_list, message, figure = modify_term(open_type, var_type, variable_name, domain_min, domain_max,
                                                        function_type, term_name, param_a, param_b,
                                                        param_c, param_d, param_mean, param_sigma,
                                                        defuzzy_type, classification_value)  
                terms_list, figure = update_terms_list_and_figure(variable_name, var_type)
                return (terms_list, message, figure,
                        '', '', '', '', '', '', '', 'Crea Termine')
            else:
                # Creazione di un nuovo termine
                terms_list, message, figure = create_term(open_type, var_type, variable_name, domain_min, domain_max,
                                                        function_type, term_name, param_a, param_b,
                                                        param_c, param_d, param_mean, param_sigma,
                                                        defuzzy_type)  
                if message == "Termine creato con successo!":
                    return (terms_list, message, figure,
                            '', '', '', '', '', '', '', 'Crea Termine')
                return (terms_list, message, figure,
                        dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                        dash.no_update, dash.no_update, dash.no_update, 'Crea Termine')

        # --- Eliminazione del Termine (usando il termine selezionato) ---
        elif triggered_id == 'delete-term-btn.n_clicks':
            if not selected_term:
                return (dash.no_update,
                        "Nessun termine selezionato",
                        dash.no_update,
                        dash.no_update, dash.no_update, dash.no_update,
                        dash.no_update, dash.no_update, dash.no_update,
                        dash.no_update, 'Crea Termine')
            return delete_term(variable_name, selected_term, var_type) + ('Crea Termine',)

        # --- Modifica del Termine (usando il termine selezionato) ---
        elif triggered_id == 'modify-term-btn.n_clicks':
            if not selected_term:
                return (dash.no_update,
                        "Nessun termine selezionato",
                        dash.no_update,
                        dash.no_update, dash.no_update, dash.no_update,
                        dash.no_update, dash.no_update, dash.no_update,
                        dash.no_update, 'Crea Termine')
            url = f'http://127.0.0.1:5000/api/get_term/{variable_name}/{selected_term}'
            headers = {'Content-Type': 'application/json'}
            response = requests.get(url)
            if response.status_code == 200:
                term_data = response.json()
                term_params = term_data.get('params', {})
                return (dash.no_update,
                        dash.no_update,
                        dash.no_update,
                        term_data.get('term_name', ''),
                        term_params.get('a', ''),
                        term_params.get('b', ''),
                        term_params.get('c', ''),
                        term_params.get('d', ''),
                        term_params.get('mean', ''),
                        term_params.get('sigma', ''),
                        'Salva Modifica')
            else:
                return (dash.no_update,
                        "Errore nel caricamento dei dati del termine.",
                        dash.no_update,
                        dash.no_update, dash.no_update, dash.no_update,
                        dash.no_update, dash.no_update, dash.no_update,
                        dash.no_update, 'Crea Termine')

        return [dash.no_update] * 11


    def validate_params(open_type, params, domain_min, domain_max, function_type):
        """
        Valida che i parametri siano compresi tra domain_min e domain_max.
        """
        if function_type == 'Triangolare':
            a, b, c = params.get('a'), params.get('b'), params.get('c')
            
            if not (domain_min <= a <= domain_max and domain_min <= b <= domain_max and domain_min <= c <= domain_max):
                return False, "Errore: I parametri a, b, c devono essere compresi tra il dominio minimo e massimo."
            
            # Controllo che a <= b <= c
            if not (a <= b <= c):
                return False, "Errore: I parametri devono rispettare l'ordine a <= b <= c."
            
        elif function_type == 'Triangolare-open':
            if open_type == "left":
                a, b, c = params.get('a'), params.get('a'), params.get('c')
            if open_type == "right":
                a, b, c = params.get('a'), params.get('c'), params.get('c')
            
            # Controllo che i parametri siano compresi tra domain_min e domain_max
            if not (domain_min <= a <= domain_max and domain_min <= b <= domain_max and domain_min <= c <= domain_max):
                return False, "Errore: I parametri a, b, c devono essere compresi tra il dominio minimo e massimo."
            
            # Controllo che a <= b <= c
            if not (a <= b <= c):
                return False, "Errore: I parametri devono rispettare l'ordine a <= b <= c."
        
        elif function_type == 'Gaussian':
            mean, sigma = params.get('mean'), params.get('sigma')
            
            # Controllo che mean sia compreso tra domain_min e domain_max
            if not (domain_min <= mean <= domain_max):
                return False, "Errore: Il parametro mean deve essere compreso tra il dominio minimo e massimo."
            
            # Controllo che sigma sia positivo (opzionale, se necessario)
            if sigma <= 0:
                return False, "Errore: Il parametro sigma deve essere maggiore di zero."
            
        elif function_type == 'Gaussian-open':
            mean, sigma = params.get('mean'), params.get('sigma')
            
            # Controllo che mean sia compreso tra domain_min e domain_max
            if not (domain_min <= mean <= domain_max):
                return False, "Errore: Il parametro mean deve essere compreso tra il dominio minimo e massimo."
            
            # Controllo che sigma sia positivo (opzionale, se necessario)
            if sigma <= 0:
                return False, "Errore: Il parametro sigma deve essere maggiore di zero."
        
        elif function_type == 'Trapezoidale':
            a, b, c, d = params.get('a'), params.get('b'), params.get('c'), params.get('d')
            
            # Controllo che i parametri siano compresi tra domain_min e domain_max
            if not (domain_min <= a <= domain_max and domain_min <= b <= domain_max and domain_min <= c <= domain_max and domain_min <= d <= domain_max):
                return False, "Errore: I parametri a, b, c, d devono essere compresi tra il dominio minimo e massimo."
            
            # Controllo che a <= b <= c <= d
            if not (a <= b <= c <= d):
                return False, "Errore: I parametri devono rispettare l'ordine a <= b <= c <= d."
        
        elif function_type == 'Trapezoidale-open':
            if open_type == "left":
                a, b, c, d = params.get('a'), params.get('a'), params.get('c'), params.get('d')
            if open_type == "right":
                a, b, c, d = params.get('a'), params.get('b'), params.get('d'), params.get('d')
            # Controllo che i parametri siano compresi tra domain_min e domain_max
            if not (domain_min <= a <= domain_max and domain_min <= b <= domain_max and domain_min <= c <= domain_max and domain_min <= d <= domain_max):
                return False, "Errore: I parametri a, b, c, d devono essere compresi tra il dominio minimo e massimo."
            
            # Controllo che a <= b <= c <= d
            if not (a <= b <= c <= d):
                return False, "Errore: I parametri devono rispettare l'ordine a <= b <= c <= d."
            
        return True, ""

    def create_term(open_type, var_type, variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma, defuzzy_type=None):
        try:
            domain_min = int(domain_min)
            domain_max = int(domain_max)
        except (ValueError, TypeError):
            return dash.no_update, "Errore: I valori del dominio devono essere numeri.", dash.no_update

        if not term_name or not re.match(r"^[A-Za-z0-9_-]+$", term_name):
            return dash.no_update, "Errore: Il nome del termine è vuoto o contiene caratteri non validi. Usa solo lettere, numeri, trattini e sottolineature.", dash.no_update

        if domain_min > domain_max:
            return dash.no_update, "Errore: Il dominio minimo non può essere maggiore del dominio massimo.", dash.no_update

        params = {}
        if function_type == 'Triangolare':
            params = {'a': param_a, 'b': param_b, 'c': param_c}
            
        if function_type == 'Triangolare-open':
            if open_type == 'left':
                params = {'a': param_a, 'b': param_a, 'c': param_c}
            elif open_type == 'right':
                params = {'a': param_a, 'b': param_c, 'c': param_c}

        if function_type == 'Gaussian':
            params = {'mean': param_mean, 'sigma': param_sigma}
            
        elif function_type == 'Gaussian-open':
            if open_type == 'left':
                params = {'mean': param_mean, 'sigma': param_sigma}
            elif open_type == 'right':
                params = {'mean': param_mean, 'sigma': param_sigma}

        if function_type == 'Trapezoidale':
            params = {'a': param_a, 'b': param_b, 'c': param_c, 'd': param_d}
            
        elif function_type == 'Trapezoidale-open':
            if open_type == 'left':
                params = {'a': param_a, 'b': param_a, 'c': param_c, 'd': param_d}
            elif open_type == 'right':
                params = {'a': param_a, 'b': param_b, 'c': param_d, 'd': param_d}


        is_valid, error_message = validate_params(open_type, params, domain_min, domain_max, function_type)
        if not is_valid:
            return dash.no_update, error_message, dash.no_update

        payload = {
            'var_type': var_type,
            'term_name': term_name,
            'variable_name': variable_name,
            'domain_min': domain_min,
            'domain_max': domain_max,
            'function_type': function_type,
            'params': params
        }

        # Aggiungi defuzzy_type solo se siamo nella pagina di output
        if var_type == "output" and defuzzy_type:
            payload['defuzzy_type'] = defuzzy_type

        headers = {'Content-Type': 'application/json'}
        response = requests.post('http://127.0.0.1:5000/api/create_term', json=payload)

        if response.status_code == 201:
            terms_list, figure = update_terms_list_and_figure(variable_name, var_type)
            return terms_list, "Termine creato con successo!", figure
        else:
            error_message = response.json().get('error', 'Errore sconosciuto')
            return dash.no_update, f"Errore: {error_message}", dash.no_update

    @dash_app.callback(
        [
            Output('selected-term', 'data'),
            Output({'type': 'term-item', 'index': dash.ALL}, 'style')
        ],
        Input({'type': 'term-item', 'index': dash.ALL}, 'n_clicks'),
        State({'type': 'term-item', 'index': dash.ALL}, 'id')
    )
    def update_selected_term_and_styles(n_clicks_list, ids):
        default_style = {'cursor': 'pointer'}
        if not n_clicks_list or all(nc is None for nc in n_clicks_list):
            return dash.no_update, [default_style for _ in ids]

        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, [default_style for _ in ids]

        triggered_prop = ctx.triggered[0]['prop_id']
        triggered_id_str = triggered_prop.split('.')[0]
        try:
            triggered_id = json.loads(triggered_id_str)
        except Exception:
            return dash.no_update, [default_style for _ in ids]

        selected_term = triggered_id.get('index')
        styles = []
        for item in ids:
            if item.get('index') == selected_term:
                styles.append({'cursor': 'pointer', 'backgroundColor': '#cce5ff'})
            else:
                styles.append(default_style)
        return selected_term, styles

    @dash_app.callback(
        [
            Output('modify-term-btn', 'disabled'),
            Output('delete-term-btn', 'disabled')
        ],
        Input('selected-term', 'data')
    )
    def update_buttons(selected_term):
        if selected_term:
            return False, False
        return True, True


    # Funzione per l'eliminazione di un termine fuzzy
    def delete_term(variable_name, term_name, var_type):
        response = requests.post(f'http://127.0.0.1:5000/api/delete_term/{term_name}')

        if response.status_code == 200:
            # Dopo aver eliminato il termine, aggiorna la lista e il grafico
            terms_list, figure = update_terms_list_and_figure(variable_name,var_type)
            # Restituisci 10 valori, includendo terms_list e figure aggiornati
            return terms_list, f"Termine '{term_name}' eliminato con successo!", figure, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        else:
            # Restituisci un errore se l'eliminazione fallisce, con dash.no_update per i valori non modificati
            return dash.no_update, f"Errore nell'eliminazione del termine: {response.json().get('error', 'Errore sconosciuto')}", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    def modify_term(open_type, var_type, variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma, defuzzy_type=None, classification_value=None):
        try:
            domain_min = int(domain_min)
            domain_max = int(domain_max)
        except (ValueError, TypeError):
            return dash.no_update, "Errore: I valori del dominio devono essere numeri.", dash.no_update

        if domain_min > domain_max:
            return dash.no_update, "Errore: Il dominio minimo non può essere maggiore del dominio massimo.", dash.no_update

        params = {}
        if function_type == 'Triangolare':
            params = {'a': param_a, 'b': param_b, 'c': param_c}
            
        if function_type == 'Triangolare-open':
            if open_type == 'left':
                params = {'a': param_a, 'b': param_a, 'c': param_c}
            elif open_type == 'right':
                params = {'a': param_a, 'b': param_c, 'c': param_c}

        if function_type == 'Gaussian':
            params = {'mean': param_mean, 'sigma': param_sigma}
            
        elif function_type == 'Gaussian-open':
            if open_type == 'left':
                params = {'mean': param_mean, 'sigma': param_sigma}
            elif open_type == 'right':
                params = {'mean': param_mean, 'sigma': param_sigma}

        if function_type == 'Trapezoidale':
            params = {'a': param_a, 'b': param_b, 'c': param_c, 'd': param_d}
            
        elif function_type == 'Trapezoidale-open':
            if open_type == 'left':
                params = {'a': param_a, 'b': param_a, 'c': param_c, 'd': param_d}
            elif open_type == 'right':
                params = {'a': param_a, 'b': param_b, 'c': param_d, 'd': param_d}

        is_valid, error_message = validate_params(open_type, params, domain_min, domain_max, function_type)
        if not is_valid:
            return dash.no_update, error_message, dash.no_update

        payload = {
            'term_name': term_name,
            'variable_name': variable_name,
            'domain_min': domain_min,
            'domain_max': domain_max,
            'function_type': function_type,
            'params': params
        }

        # Gestione del defuzzy_type in base alla checkbox
        if var_type == "output":
            if classification_value and 'Classification' in classification_value:
                # Se la checkbox è spuntata, rimuovi il defuzzy_type
                payload['defuzzy_type'] = "Classification"
            else:
                # Altrimenti, aggiorna il defuzzy_type
                payload['defuzzy_type'] = defuzzy_type

        headers = {'Content-Type': 'application/json'}
        response = requests.put(f'http://127.0.0.1:5000/api/modify_term/{term_name}', json=payload)

        if response.status_code == 201:
            terms_list, figure = update_terms_list_and_figure(variable_name, var_type)
            return terms_list, "Termine modificato con successo!", figure
        else:
            error_message = response.json().get('error', 'Errore sconosciuto')
            return dash.no_update, f"Errore: {error_message}", dash.no_update
        
    def update_terms_list_and_figure(variable_name, var_type):
        if variable_name and var_type:
            try:
                headers = {'Content-Type': 'application/json'}
                response = requests.get('http://127.0.0.1:5000/api/get_terms')
                if response.status_code == 200:
                    terms_data = response.json()
                    terms_list = []
                    input_data = []
                    output_data = []

                    # Estrai i dati solo se esistono nella risposta
                    input_variables = terms_data.get('input', {})
                    output_variables = terms_data.get('output', {})

                    # Gestisci i termini di input
                    if var_type == 'input' and variable_name in input_variables:
                        variable_data = input_variables[variable_name]
                        for term in variable_data['terms']:
                            term_name = term['term_name']
                            x = term['x']
                            y = term['y']
                            terms_list.append(
                                dbc.ListGroupItem(
                                    term_name,
                                    id={'type': 'term-item', 'index': term_name},
                                    n_clicks=0,
                                    style={
                                        'cursor': 'pointer',
                                    }
                                )
                            )
                            input_data.append(go.Scatter(x=x, y=y, mode='lines', name=term_name))

                    # Gestisci i termini di output
                    elif var_type == 'output' and variable_name in output_variables:
                        variable_data = output_variables[variable_name]
                        for term in variable_data['terms']:
                            term_name = term['term_name']
                            x = term['x']
                            y = term['y']
                            terms_list.append(
                                dbc.ListGroupItem(
                                    term_name,
                                    id={'type': 'term-item', 'index': term_name},
                                    n_clicks=0,
                                    style={
                                        'cursor': 'pointer',
                                    }
                                )
                            )
                            output_data.append(go.Scatter(x=x, y=y, mode='lines', name=term_name))

                    # Creazione del grafico in base al tipo di variabile
                    if var_type == 'input':
                        combined_figure = {
                            'data': input_data,
                            'layout': go.Layout(
                                title=f'Fuzzy set for {variable_name} (Input)',
                                xaxis={
                                    'title': 'Domain',
                                    'showgrid': True, 
                                    'gridwidth': 1,   
                                    'gridcolor': 'lightgray', 
                                    'dtick': 5  
                                },
                                yaxis={
                                    'title': 'Degree of membership',
                                    'showgrid': True,  
                                    'gridwidth': 1,    
                                    'gridcolor': 'lightgray', 
                                    'dtick': 0.1  
                                }
                            )
                        }
                    elif var_type == 'output':
                        combined_figure = {
                            'data': output_data,
                            'layout': go.Layout(
                                title=f'Fuzzy set for {variable_name} (Output)',
                                xaxis={
                                    'title': 'Domain',
                                    'showgrid': True,  
                                    'gridwidth': 1,    
                                    'gridcolor': 'lightgray',  
                                    'dtick': 5  
                                },
                                yaxis={
                                    'title': 'Degree of membership',
                                    'showgrid': True,  
                                    'gridwidth': 1,    
                                    'gridcolor': 'lightgray',  
                                    'dtick': 0.1  

                                }
                            )
                        }
                    else:
                        combined_figure = {
                            'data': [],
                            'layout': go.Layout(
                                title=f'No valid data for {variable_name}',
                                xaxis={'title': 'Domain'},
                                yaxis={'title': 'Degree of membership'}
                            )
                        }

                    # Restituzione della lista dei termini e della figura combinata
                    return terms_list, combined_figure
                else:
                    # Se la richiesta all'API fallisce
                    return [html.Li("Errore nel recupero dei termini.")], dash.no_update
            except Exception as e:
                # Gestione dell'errore nella richiesta o nel processamento
                return [html.Li(f"Errore durante il recupero dei dati: {str(e)}")], dash.no_update
        else:
            return [], dash.no_update

    # Callback per rules_page
    @dash_app.callback(
        Output("rules-container", "children"),
        Input("create-rule", "n_clicks"),
        [State({"type": "if-dropdown", "index": ALL}, "value"),  # Valori selezionati in tutti i dropdown delle variabili
        State({"type": "if-term-dropdown", "index": ALL}, "value"),  # Valori selezionati in tutti i dropdown dei termini
        State("then-dropdown", "value"),  # Valore selezionato nel dropdown dell'output
        State("then-term-dropdown", "value"),  # Valore selezionato nel dropdown del termine dell'output
        State("rules-container", "children")],  # Regole esistenti
        prevent_initial_call=True
    )
    def update_rules(n_clicks, all_input_vars, all_input_terms, output_var, output_term, existing_rules):
        """Crea una nuova regola fuzzy e la aggiunge alla lista."""
        if n_clicks is None:
            return existing_rules

        # Verifica che tutti i campi siano selezionati
        if not all(all_input_vars) or not all(all_input_terms) or not output_var or not output_term:
            return existing_rules  # Se mancano dei valori, non fare nulla

        # Costruisci la parte IF della regola
        if_part = " AND ".join([f"({var} IS {term})" for var, term in zip(all_input_vars, all_input_terms)])

        # Costruisci la regola completa
        new_rule_text = f"IF {if_part} THEN ({output_var} IS {output_term})"

        # Crea un nuovo elemento HTML per la regola
        new_rule = html.Div(
            new_rule_text,
            className="rule-item",
            style={"marginBottom": "10px", "padding": "5px", "border": "1px solid #ccc", "borderRadius": "5px"}
        )

        # Aggiungi la nuova regola alla lista delle regole esistenti
        return existing_rules + [new_rule]

    @dash_app.callback(
        [Output({"type": "if-dropdown", "index": ALL}, "options"),
        Output("then-dropdown", "options"),
        Output({"type": "if-term-dropdown", "index": ALL}, "options"),
        Output("then-term-dropdown", "options")], 
        [Input({"type": "if-dropdown", "index": ALL}, "value"),
        Input("then-dropdown", "value")],  
        prevent_initial_call=True
    )
    def update_dropdowns(all_input_values, output_variable):

        try:
            response = requests.get("http://127.0.0.1:5000/api/get_variables_and_terms")
            if response.status_code == 200:
                data = response.json()

                # Estrai le opzioni delle variabili di input
                input_options = [{"label": var, "value": var} for var in data.get("input", {}).keys()]

                # Estrai le opzioni delle variabili di output
                output_options = [{"label": var, "value": var} for var in data.get("output", {}).keys()]

                # Estrai i termini per ogni variabile di input selezionata
                if_terms = []
                for input_value in all_input_values:
                    if input_value and input_value in data.get("input", {}):
                        terms = [{"label": term["label"], "value": term["value"]} for term in data["input"][input_value]]
                        if_terms.append(terms)
                    else:
                        if_terms.append([])  # Se la variabile non è valida, restituisci una lista vuota

                # Estrai i termini per la variabile di output selezionata
                then_terms = []
                if output_variable and output_variable in data.get("output", {}):
                    then_terms = [{"label": term["label"], "value": term["value"]} for term in data["output"][output_variable]]

                return [input_options] * len(all_input_values), output_options, if_terms, then_terms

            else:
                print("Errore nella risposta:", response.status_code)
                return [[]] * len(all_input_values), [], [[]] * len(all_input_values), []

        except Exception as e:
            print(f"Errore nella callback: {e}")
            return [[]] * len(all_input_values), [], [[]] * len(all_input_values), []

    @dash_app.callback(
        [Output('rules-list', 'children', allow_duplicate=True),
        Output('error-message', 'children')],
        Input('create-rule', 'n_clicks'),
        [
            State('input-container', 'children'),
            State('then-dropdown', 'value'),
            State('then-term-dropdown', 'value'),
            State('rules-list', 'children')
        ],
        prevent_initial_call=True
        )
    def create_rule(n_clicks, input_components, output_variable, output_term, current_rules):
        if n_clicks is None:
            return current_rules, ''

        # Estrai i valori degli input
        inputs = []
        for component in input_components:
            try:
                # Accedi ai valori dei dropdown
                input_var = component['props']['children'][0]['props']['children'][1]['props']['value']
                input_term = component['props']['children'][0]['props']['children'][3]['props']['value']
                if input_var and input_term:
                    inputs.append({"input_variable": input_var, "input_term": input_term})
            except (IndexError, KeyError) as e:
                print(f"Errore nell'accesso ai valori del componente: {e}")
                return current_rules, 'Errore: struttura del componente non valida!'

        if not inputs or not output_variable or not output_term:
            return current_rules, 'Errore: compila tutti i campi!'

        # Crea il testo della regola
        rule_text = " AND ".join([f"({input['input_variable']} IS {input['input_term']})" for input in inputs])
        rule_text = f"IF {rule_text} THEN ({output_variable} IS {output_term})"

        # Verifica se la regola esiste già
        existing_rules_texts = [rule['props']['children'] if isinstance(rule, dict) else rule.children for rule in current_rules]
        if rule_text in existing_rules_texts:
            return current_rules, 'Errore: questa regola esiste già!'

        # Invia la regola al backend
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            "http://127.0.0.1:5000/api/create_rule",
            json={
                "inputs": inputs,
                "output_variable": output_variable,
                "output_term": output_term
            }
        )

        if response.status_code == 201:
            new_rule = html.P(
                rule_text,
                className="rule-item",
                style={"fontSize": "0.9em"}
            )
            current_rules.append(new_rule)
            return current_rules, ''

        return current_rules, ''


    @dash_app.callback(
    Output('rules-list', 'children',  allow_duplicate=True),
    Input('delete-rule', 'n_clicks'),
    [State('rules-list', 'children')],
    prevent_initial_call=True
    )
    def delete_rule(n_clicks, current_rules):
        if n_clicks is None or not current_rules:
            return current_rules

        # Ottieni l'ID della regola da eliminare (ad esempio, l'ultima regola)
        rule_id = f"Rule{len(current_rules) - 1}"

        headers = {'Content-Type': 'application/json'}
        response = requests.delete(f"http://127.0.0.1:5000/api/delete_rule/{rule_id}")

        if response.status_code == 200:
            # Rimuovi la regola dalla lista visualizzata
            return current_rules[:-1]

        return current_rules
                
    @dash_app.callback(
        Output("rules-store", "data"),
        Input("url_rules", "pathname")
    )
    def load_rules_on_page_load(pathname):
        try:
            response = requests.get("http://127.0.0.1:5000/api/get_rules")
            if response.status_code == 200:
                return response.json()  
            return []
        except Exception as e:
            print(f"Errore nel caricamento delle regole: {e}")
            return []
        
    @dash_app.callback(
    Output("rules-list", "children"),
    Input("rules-store", "data")
    )
    def display_existing_rules(rules_data):

        return [
            html.P(
                f"IF ({rule['input_variable']} IS {rule['input_term']}) THEN ({rule['output_variable']} IS {rule['output_term']})",
                className="rule-item",
                style={"fontSize": "0.9em"}
            ) for rule in rules_data
        ]

    @dash_app.callback(
    Output('input-container', 'children'),
    Input('add-input', 'n_clicks'),
    State('input-container', 'children')
    )
    def manage_inputs(add_clicks, current_inputs):
        if add_clicks is None:
            return current_inputs
        # Aggiungi un nuovo set di dropdown
        new_input = dbc.Row([
            dbc.Col([
                dbc.Label("IF", html_for=f"if-dropdown-{add_clicks}", className="w-100 text-center mb-0"),
                dcc.Dropdown(
                    id={"type": "if-dropdown", "index": add_clicks},
                    options=[], 
                    placeholder="Select Input Variable",
                    className="custom-dropdown mb-2",
                    style={"width": "300px"}  
                ),
                dbc.Label("Term", html_for=f"if-term-dropdown-{add_clicks}", className="w-100 text-center mb-0"),
                dcc.Dropdown(
                    id={"type": "if-term-dropdown", "index": add_clicks},
                    options=[],  
                    placeholder="Select Term",
                    className="custom-dropdown",
                    style={"width": "300px"}  
                ),
            ], md=6, className="d-flex flex-column align-items-center pe-2")
        ])

        current_inputs.append(new_input)
        return current_inputs

#Regole
    @dash_app.callback(
        Output("inference-data", "data"),
        Output("rules-list-membership", "children"),
        Output("membership-values", "children"),
        Input("start-inference", "n_clicks"),
        State("inference-inputs", "children"),
        prevent_initial_call=True
    )
    def run_inference(n_clicks, input_children):
        try:
            inputs_dict = {}
            for col in input_children[0]["props"]["children"]:
                input_id = col["props"]["children"][1]["props"]["id"]
                input_value = col["props"]["children"][1]["props"]["value"]
                var_name = input_id.replace("-input", "")
                if input_value is not None:
                    inputs_dict[var_name] = float(input_value)

            response = requests.post("http://127.0.0.1:5000/api/infer", json={"inputs": inputs_dict})
            if response.status_code != 200:
                return dash.no_update, ["Errore"], ["Errore"]

            result = response.json()
            rule_outputs = result["rule_outputs"]
            outputs = result["results"]

            # Visualizza le attivazioni delle regole
            rules_display = [
                html.Div(f"{r['output_variable']} IS {r['output_term']} --> {round(r['activation'], 3)}", className="mb-1")
                for r in rule_outputs
            ]

            # Nessuna ripetizione dei risultati finali, già visibili nei box
            membership_display = []

            return result, rules_display, membership_display

        except Exception as e:
            print(f"Errore inferenza: {e}")
            return dash.no_update, ["Errore"], ["Errore"]



    @dash_app.callback(
        Output({"type": "output", "variable": MATCH}, "children"),
        Input("inference-data", "data"),
        State({"type": "output", "variable": MATCH}, "id"),
        prevent_initial_call=True
    )
    def update_output_value(data, matched_id):
        if not data:
            raise PreventUpdate

        var_name = matched_id["variable"]
        value = data.get("results", {}).get(var_name, 0)

        return str(round(value, 2))



#Report_page callbakcs
def fetch_data():
    """Function to fetch data from the backend."""
    try:
        # Request to the backend to get terms and rules
        response_terms = requests.get(f"http://127.0.0.1:5000/api/get_terms")
        response_rules = requests.get(f"http://127.0.0.1:5000/api/get_rules")

        if response_terms.status_code == 200 and response_rules.status_code == 200:
            terms_data = response_terms.json()
            rules_data = response_rules.json()
            return {"terms": terms_data, "rules": rules_data}
        else:
            return None
    except Exception as e:
        print(f"Error while loading data: {e}")
        return None

def generate_variable_section(variables, var_type):
    """Generates sections for input or output variables."""
    children = []
    for var_name, var_data in variables.items():
        children.append(
            dbc.Card([
                dbc.CardHeader(f"{var_type.capitalize()} Variable: {var_name}"),
                dbc.CardBody([
                    html.Div([
                        html.H5(var_name, className="text-primary mb-2" if var_type == "input" else "text-success mb-2"),
                        dbc.Row([
                            dbc.Col(f"Domain: {var_data['domain'][0]}-{var_data['domain'][1]}", width=6),
                            dbc.Col(f"Type: {var_type.capitalize()}", width=6),
                        ]),
                        html.Div(
                            className="mt-2",
                            children=[
                                html.Small("Membership Functions:", className="text-muted"),
                                html.Div([
                                    dbc.Badge(term["term_name"], color="info" if var_type == "input" else "secondary", className="me-1")
                                    for term in var_data["terms"]
                                ], className="mt-1")
                            ]
                        )
                    ], className="variable-card mb-3 p-3")
                ])
            ], className="shadow-sm")
        )
    return children

def generate_rules_section(rules):
    """Generates the section for fuzzy rules."""
    children = []
    for rule in rules:
        children.append(
            html.Li(
                f"IF {rule['input_variable']} IS {rule['input_term']} THEN {rule['output_variable']} IS {rule['output_term']}",
                className="rule-item mb-2 p-2"
            )
        )
    return children

