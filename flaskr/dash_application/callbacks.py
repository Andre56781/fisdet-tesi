import dash
import base64
from dash import dcc, html, Input, Output, State, ctx, ALL, MATCH, callback_context
import plotly.graph_objects as go
import requests
import dash_bootstrap_components as dbc
import json
from flaskr import file_handler
from flaskr.file_handler import save_terms
from datetime import datetime
import re
from dash.exceptions import PreventUpdate


def register_callbacks(dash_app):
    """Registra tutti i callback necessari all'app Dash per la gestione delle variabili fuzzy, regole e inferenza."""
    @dash_app.callback(
        Output("download-json", "data"),
        Output("export-loading", "children"),
        Input("btn-json-export", "n_clicks"),
        prevent_initial_call=True
    )
    def handle_json_export(n_clicks):
        """Esporta il file JSON con la configurazione attuale."""
        if n_clicks:
            try:
                response = requests.get("http://127.0.0.1:5000/api/export_json")
                if response.status_code == 200:
                    data = response.json()
                    return (
                        {
                            "content": json.dumps(data, indent=4, ensure_ascii=False),
                            "filename": f"fis_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        },
                        ""
                    )
                else:
                    return dash.no_update, "Errore export"
            except Exception as e:
                print(f"Errore esportazione: {e}")
                return dash.no_update, ""
        return dash.no_update, ""


    @dash_app.callback(
        Output('session-store', 'data'),
        Output('import-feedback', 'children'),
        Input('upload-fis', 'contents'),
        State('upload-fis', 'filename'),
        prevent_initial_call=True
    )
    def handle_json_import(contents, filename):
        """Importa un file JSON e aggiorna lo store di sessione."""
        if contents:
            try:
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                uploaded_data = json.loads(decoded.decode('utf-8'))

                response = requests.post(
                    "http://127.0.0.1:5000/api/import_json",
                    json=uploaded_data
                )
                if response.status_code == 200:
                    return uploaded_data, dbc.Alert("Importazione completata!", color="success", dismissable=True)
                else:
                    return dash.no_update, dbc.Alert(f"Errore: {response.json().get('error', 'Errore sconosciuto')}", color="danger", dismissable=True)
            except Exception as e:
                return dash.no_update, dbc.Alert(f"Errore durante l'import: {e}", color="danger", dismissable=True)
        return dash.no_update, dash.no_update


    @dash_app.callback(
    Output('url', 'pathname'),
    Input('upload-fis', 'contents'),
    prevent_initial_call=True
    )
    def handle_upload(contents):
        """Reindirizza alla pagina /report dopo l'upload del file."""
        if contents:
            return '/report'
        return dash.no_update


    @dash_app.callback(
            [Output("variable-modal", "is_open"),
            Output("main-content", "style"),
            Output("num-variables-store", "data")],
            [Input("modal-submit-button", "n_clicks")],
            [State("num-variables-input", "value")]
        )
    def handle_modal_submit(n_clicks, num_variables):
        """Gestisce l'inserimento del numero di variabili da creare."""
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

    @dash_app.callback(
        Output("variable-title", "children"),
        Input("var-type-store", "data"),
        [Input("current-index", "data"),
        Input("num-variables-store", "data")]
    )
    def update_title(var_type, current_index, num_vars):
        """Aggiorna il titolo della variabile in base all'indice corrente."""
        if num_vars is None or current_index is None:
            return ""
        try:
            current_index = int(current_index)
        except (ValueError, TypeError):
            return "Errore: Indice della variabile non valido."

        return f"Creation of  {var_type} Variables {current_index + 1} of {num_vars}"

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
            current_index = 0 if current_index is None else current_index
        else:
            triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if triggered_id == "next-button" and current_index < num_variables - 1:
                current_index += 1
            elif triggered_id == "back-button" and current_index > 0:
                current_index -= 1

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
        [
            Input('var-type-store', 'data'),
            Input('function-type', 'value'),
            Input('num-variables-store', 'data'),
            Input('current-index', 'data'),
            Input('open-type', 'value')
        ]
    )
    def update_params(var_type, function_type, num_variables, current_index, open_type):
        if not function_type or num_variables is None or current_index is None:
            return [] 

        params = []

        if var_type == 'input':
            params.append(dbc.RadioItems(
                id='open-type-radio',
                options=[
                    {'label': 'Left open', 'value': 'left'},
                    {'label': 'Right open', 'value': 'right'}
                ],
                inline=True,
                value=open_type
            ))

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
            
            params.append(dbc.Input(id='param-d', style={'display': 'none'}))
            params.append(dbc.Input(id='param-mean', style={'display': 'none'}))
            params.append(dbc.Input(id='param-sigma', style={'display': 'none'}))

        elif function_type == 'Gaussian':
            params.append(dbc.Label("Parametro Mean:"))
            params.append(dbc.Input(id='param-mean', type='number', value='', required=True))
            params.append(dbc.Label("Parametro Sigma:"))
            params.append(dbc.Input(id='param-sigma', type='number', value='', required=True))

            params.append(dbc.Input(id='param-b', style={'display': 'none'}))
            params.append(dbc.Input(id='param-c', style={'display': 'none'}))
            params.append(dbc.Input(id='param-d', style={'display': 'none'}))

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
        ],
        prevent_initial_call=True
    )
    def handle_terms(create_clicks, delete_clicks, modify_clicks, open_type,
                    var_type, variable_name, domain_min, domain_max, function_type,
                    term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma,
                    defuzzy_type, button_label, selected_term): 
        """Gestisce la creazione, modifica ed eliminazione dei termini fuzzy.""" 
        ctx = dash.ctx

        if not ctx.triggered:
            return [dash.no_update] * 11

        triggered_id = ctx.triggered[0]['prop_id']

        if var_type == "input":
            defuzzy_type = None
            
        if var_type == "output":
            open_type = None
        
        if open_type is None:
            open_type = []

        if isinstance(open_type, str) and ('left' in open_type or 'right' in open_type):
            function_type = f"{function_type}-open"
        
        if var_type not in ['input', 'output']:
            return [dash.no_update,
                    "Errore: var_type deve essere 'input' o 'output'",
                    dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                    dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                    'Crea Termine']

        if triggered_id == 'create-term-btn.n_clicks':             
            if button_label == 'Salva Modifica':
                terms_list, message, figure = modify_term(open_type, var_type, variable_name, domain_min, domain_max,
                                                        function_type, term_name, param_a, param_b,
                                                        param_c, param_d, param_mean, param_sigma,
                                                        defuzzy_type)  
                terms_list, figure = update_terms_list_and_figure(variable_name, var_type)
                return (terms_list, message, figure,
                        '', '', '', '', '', '', '', 'Crea Termine')
            else:
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

        elif triggered_id == 'delete-term-btn.n_clicks':
            if not selected_term:
                return (dash.no_update,
                        "Nessun termine selezionato",
                        dash.no_update,
                        dash.no_update, dash.no_update, dash.no_update,
                        dash.no_update, dash.no_update, dash.no_update,
                        dash.no_update, 'Crea Termine')
            return delete_term(variable_name, selected_term, var_type) + ('Crea Termine',)

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

    @dash_app.callback(
        Output("classification-warning-modal", "is_open"),
        Input("classification-checkbox", "value"),
        State("classification-confirmed", "data")
    )
    def show_classification_modal(value, confirmed):
        """Mostra un modal di conferma quando si attiva la modalità Classification.""" 
        if value and "Classification" in value and not confirmed:
            return True
        return False


    @dash_app.callback(
    [
        Output("classification-checkbox", "value", allow_duplicate=True),
        Output("message", "children", allow_duplicate=True),
        Output("terms-list", "children", allow_duplicate=True),
        Output("graph", "figure", allow_duplicate=True),
        Output("classification-warning-modal", "is_open", allow_duplicate=True),
        Output("classification-confirmed", "data", allow_duplicate=True)  
    ],
    [
        Input("confirm-classification", "n_clicks"),
        Input("cancel-classification", "n_clicks")
    ],
    prevent_initial_call=True
    )
    def handle_classification_change(confirm_click, cancel_click):
        """Gestisce la conferma o l'annullamento della modalità Classification.""" 
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == "confirm-classification":
            try:
                response = requests.post("http://127.0.0.1:5000/api/clear_output")
                if response.status_code == 200:
                    return (
                        ["Classification"],  
                        "Output data has been cleared.",
                        [dbc.ListGroupItem("No Terms Present", style={"textAlign": "center"})],
                        {},  
                        False,  
                        True   
                    )
                else:
                    return (
                        ["Classification"],
                        f"Errore: {response.json().get('error', 'Errore sconosciuto')}",
                        dash.no_update,
                        dash.no_update,
                        False,
                        False
                    )
            except Exception as e:
                return (
                    ["Classification"],
                    f"Errore di connessione al backend: {e}",
                    dash.no_update,
                    dash.no_update,
                    False,
                    False
                )

        elif triggered_id == "cancel-classification":
            return (
                [], "", dash.no_update, dash.no_update, False, False
            )

        raise dash.exceptions.PreventUpdate



    @dash_app.callback(
        Output("graph-container", "style"),
        Output("output-hideable-fields", "style"),
        Input("classification-checkbox", "value"),
        prevent_initial_call=True,
        allow_duplicate=True
    )
    def toggle_fields_classification(classification_value):
        """Mostra o nasconde i campi fuzzy in base alla modalità Classification.""" 
        if classification_value and "Classification" in classification_value:
            return {"display": "none"}, {"display": "none"}  
        return {"display": "block"}, {"display": "block"}  

    @dash_app.callback(
        Output("classification-counter", "style"),
        Output("classification-counter", "children"),
        Input("classification-checkbox", "value"),
        Input("classification-term-count", "data")
    )
    def update_classification_counter(classification_value, term_count):
        """Aggiorna e mostra il contatore dei termini in modalità Classification.""" 
        if classification_value and "Classification" in classification_value:
            return {"display": "block"}, f"Classification Terms Created: {term_count}"
        return {"display": "none"}, ""

    @dash_app.callback(
    Output("dynamic-right-column", "children"),
    Input("classification-checkbox", "value"),
    prevent_initial_call="initial_duplicate"
    )
    def switch_right_column_content(classification_value):
        """Cambia i campi mostrati nella colonna destra in base alla modalità Classification.""" 
        if classification_value and "Classification" in classification_value:
            return html.Div([
                dbc.Label("Fuzzy Term Name", className="mb-0"),
                dbc.Input(
                    id='term-name',
                    type='text',
                    value='',
                    pattern="^[a-zA-Z0-9]*$",
                    className="input-field",
                    debounce=True,
                    required=True
                )
            ])
        else:
            return html.Div([
                dbc.Label("Domain", className="form-label mb-0"),
                dbc.InputGroup([
                    dbc.Input(
                        id='domain-min',
                        type='number',
                        className="input-field",
                        value='0',
                        placeholder="0",
                        debounce=True,
                        required=True
                    ),
                    dbc.Input(
                        id='domain-max',
                        type='number',
                        className="input-field",
                        value='',
                        placeholder="100",
                        debounce=True,
                        required=True
                    )
                ], className="domain-input-group mb-3")
            ])
    @dash_app.callback(
        Output("term-name-row", "style"),
        Input("classification-checkbox", "value"),
        prevent_initial_call=True
    )
    def toggle_term_name_row(classification_value):
        """Mostra o nasconde la riga del nome del termine in base alla modalità Classification.""" 
        if classification_value and "Classification" in classification_value:
            return {"display": "none"}
        return {"display": "block"}



    def validate_params(open_type, params, domain_min, domain_max, function_type):
        """Valida i parametri di un termine fuzzy rispetto al dominio e al tipo di funzione.""" 
        if function_type == 'Triangolare':
            a, b, c = params.get('a'), params.get('b'), params.get('c')
            
            if not (domain_min <= a <= domain_max and domain_min <= b <= domain_max and domain_min <= c <= domain_max):
                return False, "Errore: I parametri a, b, c devono essere compresi tra il dominio minimo e massimo."
            
            if not (a <= b <= c):
                return False, "Errore: I parametri devono rispettare l'ordine a <= b <= c."
            
        elif function_type == 'Triangolare-open':
            if open_type == "left":
                a, b, c = params.get('a'), params.get('a'), params.get('c')
            if open_type == "right":
                a, b, c = params.get('a'), params.get('c'), params.get('c')
            
            if not (domain_min <= a <= domain_max and domain_min <= b <= domain_max and domain_min <= c <= domain_max):
                return False, "Errore: I parametri a, b, c devono essere compresi tra il dominio minimo e massimo."
            
            if not (a <= b <= c):
                return False, "Errore: I parametri devono rispettare l'ordine a <= b <= c."
        
        elif function_type == 'Gaussian':
            mean, sigma = params.get('mean'), params.get('sigma')
            
            if not (domain_min <= mean <= domain_max):
                return False, "Errore: Il parametro mean deve essere compreso tra il dominio minimo e massimo."
            
            if sigma <= 0:
                return False, "Errore: Il parametro sigma deve essere maggiore di zero."
            
        elif function_type == 'Gaussian-open':
            mean, sigma = params.get('mean'), params.get('sigma')
            
            if not (domain_min <= mean <= domain_max):
                return False, "Errore: Il parametro mean deve essere compreso tra il dominio minimo e massimo."
            
        
        elif function_type == 'Trapezoidale':
            a, b, c, d = params.get('a'), params.get('b'), params.get('c'), params.get('d')
            
            if not (domain_min <= a <= domain_max and domain_min <= b <= domain_max and domain_min <= c <= domain_max and domain_min <= d <= domain_max):
                return False, "Errore: I parametri a, b, c, d devono essere compresi tra il dominio minimo e massimo."
            
            if not (a <= b <= c <= d):
                return False, "Errore: I parametri devono rispettare l'ordine a <= b <= c <= d."
        
        elif function_type == 'Trapezoidale-open':
            if open_type == "left":
                a, b, c, d = params.get('a'), params.get('a'), params.get('c'), params.get('d')
            if open_type == "right":
                a, b, c, d = params.get('a'), params.get('b'), params.get('d'), params.get('d')
            if not (domain_min <= a <= domain_max and domain_min <= b <= domain_max and domain_min <= c <= domain_max and domain_min <= d <= domain_max):
                return False, "Errore: I parametri a, b, c, d devono essere compresi tra il dominio minimo e massimo."
            
            if not (a <= b <= c <= d):
                return False, "Errore: I parametri devono rispettare l'ordine a <= b <= c <= d."
            
        return True, ""

    def create_term(open_type, var_type, variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma, defuzzy_type=None):
        """Crea un nuovo termine fuzzy e aggiorna grafico e lista.""" 
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

        if 'open' in function_type and open_type:
            payload['open_type'] = open_type

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
        """Aggiorna il termine selezionato e applica lo stile evidenziato.""" 
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
        """Abilita o disabilita i pulsanti di modifica/eliminazione in base alla selezione.""" 
        if selected_term:
            return False, False
        return True, True


    def delete_term(variable_name, term_name, var_type):
        """Elimina un termine fuzzy esistente.""" 
        response = requests.post(f'http://127.0.0.1:5000/api/delete_term/{term_name}')

        if response.status_code == 200:
            terms_list, figure = update_terms_list_and_figure(variable_name,var_type)
            return terms_list, f"Termine '{term_name}' eliminato con successo!", figure, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        else:
            return dash.no_update, f"Errore nell'eliminazione del termine: {response.json().get('error', 'Errore sconosciuto')}", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    def modify_term(open_type, var_type, variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma, defuzzy_type=None):
        """Modifica un termine fuzzy esistente e aggiorna grafico e lista.""" 
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

        if var_type == "input":
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
        """Recupera i termini fuzzy e costruisce il grafico corrispondente.""" 
        if variable_name and var_type:
            try:
                headers = {'Content-Type': 'application/json'}
                response = requests.get('http://127.0.0.1:5000/api/get_terms')
                if response.status_code == 200:
                    terms_data = response.json()
                    terms_list = []
                    input_data = []
                    output_data = []

                    input_variables = terms_data.get('input', {})
                    output_variables = terms_data.get('output', {})

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

                    return terms_list, combined_figure
                else:
                    return [html.Li("Errore nel recupero dei termini.")], dash.no_update
            except Exception as e:
                return [html.Li(f"Errore durante il recupero dei dati: {str(e)}")], dash.no_update
        else:
            return [], dash.no_update

    @dash_app.callback(
        Output("rules-container", "children"),
        Input("create-rule", "n_clicks"),
        [State({"type": "if-dropdown", "index": ALL}, "value"),  
        State({"type": "if-term-dropdown", "index": ALL}, "value"),  
        State("then-dropdown", "value"),  
        State("then-term-dropdown", "value"),  
        State("rules-container", "children")],  
        prevent_initial_call=True
    )
    def update_rules(n_clicks, all_input_vars, all_input_terms, output_var, output_term, existing_rules):
        """Crea una nuova regola fuzzy e la aggiunge al contenitore.""" 
        if n_clicks is None:
            return existing_rules

        if not all(all_input_vars) or not all(all_input_terms) or not output_var or not output_term:
            return existing_rules  

        if_part = " AND ".join([f"({var} IS {term})" for var, term in zip(all_input_vars, all_input_terms)])

        new_rule_text = f"IF {if_part} THEN ({output_var} IS {output_term})"

        new_rule = html.Div(
            new_rule_text,
            className="rule-item",
            style={"marginBottom": "10px", "padding": "5px", "border": "1px solid #ccc", "borderRadius": "5px"}
        )

        return existing_rules + [new_rule]

    @dash_app.callback(
        [Output({"type": "if-dropdown", "index": ALL}, "options"),
        Output({"type": "if-term-dropdown", "index": ALL}, "options"),
        Output("then-dropdown", "options"),
        Output("then-dropdown", "value"),
        Output("then-term-dropdown", "options")],
        [Input({"type": "if-dropdown", "index": ALL}, "value")],
        prevent_initial_call=True
    )
    def update_dropdowns(all_input_values):
        """Aggiorna le opzioni delle dropdown IF/THEN in base alle variabili disponibili.""" 
        try:
            response = requests.get("http://127.0.0.1:5000/api/get_variables_and_terms")
            if response.status_code != 200:
                return [[]] * len(all_input_values), [[]] * len(all_input_values), [], None, []

            data = response.json()
            input_vars = list(data.get("input", {}).keys())
            output_data = data.get("output", {})

            output_var_name = next(iter(output_data), None)

            input_options_list = []
            for i, selected in enumerate(all_input_values):
                used = [v for j, v in enumerate(all_input_values) if j != i and v]
                available = [v for v in input_vars if v not in used]
                input_options_list.append([{"label": v, "value": v} for v in available])

            if_term_options = []
            for selected in all_input_values:
                if selected and selected in data["input"]:
                    terms = data["input"][selected]
                    if_term_options.append([{"label": t["label"], "value": t["value"]} for t in terms])
                else:
                    if_term_options.append([])

            then_dropdown_options = [{"label": output_var_name, "value": output_var_name}] if output_var_name else []
            then_dropdown_value = output_var_name

            then_terms = []
            if output_var_name and output_var_name in output_data:
                then_terms = [{"label": t["label"], "value": t["value"]} for t in output_data[output_var_name]]

            return input_options_list, if_term_options, then_dropdown_options, then_dropdown_value, then_terms

        except Exception as e:
            print(f"Errore in update_dropdowns: {e}")
            return [[]] * len(all_input_values), [[]] * len(all_input_values), [], None, []




    @dash_app.callback(
        [
            Output('rules-list', 'children', allow_duplicate=True),
            Output('rules-store', 'data', allow_duplicate=True),
            Output('error-message', 'children')
        ],
        Input('create-rule', 'n_clicks'),
        [
            State({'type': 'if-dropdown', 'index': ALL}, 'value'),
            State({'type': 'if-term-dropdown', 'index': ALL}, 'value'),
            State('then-dropdown', 'value'),
            State('then-term-dropdown', 'value'),
            State('rules-list', 'children'),
            State('rules-store', 'data')
        ],
        prevent_initial_call=True
    )
    def create_rule(n_clicks, input_vars, input_terms, output_variable, output_term, current_rules, rules_data):
        """Crea una regola fuzzy e la salva nel backend.""" 
        if n_clicks is None:
            return current_rules, rules_data, ''

        if not all(input_vars) or not all(input_terms) or not output_variable or not output_term:
            return current_rules, rules_data, 'Errore: compila tutti i campi!'

        inputs = [{"input_variable": var, "input_term": term} for var, term in zip(input_vars, input_terms)]

        rule_text = " AND ".join([f"({i['input_variable']} IS {i['input_term']})" for i in inputs])
        rule_text = f"IF {rule_text} THEN ({output_variable} IS {output_term})"

        existing_rules_texts = [rule['props']['children'] if isinstance(rule, dict) else rule.children for rule in current_rules]
        if rule_text in existing_rules_texts:
            return current_rules, rules_data, 'Errore: questa regola esiste già!'

        response = requests.post(
            "http://127.0.0.1:5000/api/create_rule",
            json={
                "inputs": inputs,
                "output_variable": output_variable,
                "output_term": output_term
            }
        )

        if response.status_code == 201:
            rule_id = response.json().get("rule_id")
            rules_data.append({
                "id": rule_id,
                "inputs": inputs,
                "output_variable": output_variable,
                "output_term": output_term
            })

            new_rule = dbc.ListGroupItem(
                rule_text,
                id={'type': 'rule-item', 'index': rule_id},
                n_clicks=0,
                style={"cursor": "pointer"}
            )

            return current_rules + [new_rule], rules_data, ''

        return current_rules, rules_data, 'Errore durante il salvataggio della regola'


    @dash_app.callback(
        [Output("rules-list", "children", allow_duplicate=True),
        Output("delete-rule", "disabled"),
        Output("selected-rule-id", "data")],
        Input({"type": "rule-item", "index": ALL}, "n_clicks"),
        State({"type": "rule-item", "index": ALL}, "id"),
        State("rules-store", "data"),
        prevent_initial_call=True
    )
    def select_rule(n_clicks, all_ids, rules_data):
        """Evidenzia la regola selezionata e salva il relativo ID.""" 
        selected_id = None
        styles = []

        if not n_clicks:
            return dash.no_update, True, None

        for idx, click in enumerate(n_clicks):
            if click and click > 0:
                selected_id = all_ids[idx]['index']
                break

        rule_items = []
        for rule in rules_data:
            inputs = rule.get("inputs", [])
            inputs_text = " AND ".join(
                f"({inp['input_variable']} IS {inp['input_term']})" for inp in inputs
            )
            output_text = f"({rule['output_variable']} IS {rule['output_term']})"
            rule_text = f"IF {inputs_text} THEN {output_text}"

            style = {"cursor": "pointer"}
            if rule["id"] == selected_id:
                style["backgroundColor"] = "#d1ecf1"

            rule_items.append(
                dbc.ListGroupItem(
                    rule_text,
                    id={'type': 'rule-item', 'index': rule['id']},
                    n_clicks=0,
                    style=style
                )
            )

        return rule_items, selected_id is None, selected_id


    @dash_app.callback(
        Output("rules-store", "data", allow_duplicate=True),
        Input("delete-rule", "n_clicks"),
        State("selected-rule-id", "data"),
        State("rules-store", "data"),
        prevent_initial_call=True
    )
    def delete_selected_rule(n_clicks, selected_rule_id, rules_data):
        """Elimina la regola selezionata e aggiorna la lista.""" 
        if not selected_rule_id:
            raise dash.exceptions.PreventUpdate

        response = requests.delete(f"http://127.0.0.1:5000/api/delete_rule/{selected_rule_id}")
        if response.status_code != 200:
            return dash.no_update

        updated_rules = [r for r in rules_data if r["id"] != selected_rule_id]
        return updated_rules


                
    @dash_app.callback(
        [Output("rules-store", "data"),
        Output("input-variables", "data")],
        Input("url_rules", "pathname")
    )
    def load_rules_on_page_load(pathname):
        try:
            response_rules = requests.get("http://127.0.0.1:5000/api/get_rules")
            rules = response_rules.json() if response_rules.status_code == 200 else []

            response_vars = requests.get("http://127.0.0.1:5000/api/get_variables_and_terms")
            input_vars = []

            if response_vars.status_code == 200:
                data = response_vars.json()
                input_vars = list(data.get("input", {}).keys())

            return rules, input_vars

        except Exception as e:
            print(f"Errore nel caricamento delle regole o variabili: {e}")
            return [], []

        
    @dash_app.callback(
        Output("rules-list", "children"),
        Input("rules-store", "data")
    )
    def display_existing_rules(rules_data):
        """Mostra tutte le regole presenti nella lista.""" 
        rules_display = []
        for rule in rules_data:
            inputs = rule.get("inputs", [])
            inputs_text = " AND ".join(
                f"({inp['input_variable']} IS {inp['input_term']})" for inp in inputs
            )
            output_text = f"({rule['output_variable']} IS {rule['output_term']})"
            rule_text = f"IF {inputs_text} THEN {output_text}"

            rules_display.append(
                dbc.ListGroupItem(
                    rule_text,
                    id={'type': 'rule-item', 'index': rule['id']},
                    n_clicks=0,
                    style={"cursor": "pointer"}
                )
            )
        return rules_display


    @dash_app.callback(
        [Output('input-container', 'children', allow_duplicate=True),
        Output('input-count', 'data', allow_duplicate=True)],
        Input('input-variables', 'data'),
        prevent_initial_call=True
    )
    def init_input_blocks(input_variables):
        """Inizializza il primo blocco IF-Term per la creazione di una regola.""" 
        if not input_variables:
            return [], 0

        first_input = html.Div([
            dbc.Label("IF", className="w-100 text-center mb-0"),
            dcc.Dropdown(id={"type": "if-dropdown", "index": 0}, placeholder="Select Input Variable", style={"width": "200px"}),
            dbc.Label("Term", className="w-100 text-center mb-0"),
            dcc.Dropdown(id={"type": "if-term-dropdown", "index": 0}, placeholder="Select Term", style={"width": "200px"}),
        ], className="d-flex flex-column align-items-center border rounded p-2", style={"minWidth": "220px"})

        return [first_input], 1


    @dash_app.callback(
        [Output('input-container', 'children'),
        Output('input-count', 'data')],
        Input('add-input', 'n_clicks'),
        State('input-container', 'children'),
        State('input-variables', 'data'),
        State('input-count', 'data'),
        prevent_initial_call=True
    )
    def manage_inputs(add_clicks, current_inputs, input_variables, input_count):
        """Aggiunge dinamicamente nuovi blocchi IF-Term per la creazione delle regole.""" 
        if not input_variables or input_count >= len(input_variables):
            return current_inputs, input_count

        new_input = html.Div([
            dbc.Label("IF", className="w-100 text-center mb-0"),
            dcc.Dropdown(id={"type": "if-dropdown", "index": input_count}, placeholder="Select Input Variable", style={"width": "200px"}),
            dbc.Label("Term", className="w-100 text-center mb-0"),
            dcc.Dropdown(id={"type": "if-term-dropdown", "index": input_count}, placeholder="Select Term", style={"width": "200px"}),
        ], className="d-flex flex-column align-items-center border rounded p-2", style={"minWidth": "220px"})

        current_inputs.append(new_input)
        return current_inputs, input_count + 1


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
        """Esegue l'inferenza fuzzy sui valori inseriti e mostra attivazioni e output.""" 
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
                return dash.no_update, [html.Div("Errore nell'inferenza", className="text-danger")], []

            result = response.json()
            rule_outputs = result.get("rule_outputs", [])
            outputs = result.get("results", {})

            rule_map = {
                (rule["output_variable"], rule["output_term"]): rule
                for key, rule in result.items()
                if key.startswith("Rule") and isinstance(rule, dict)
            }

            rules_display = []
            for rule in rule_outputs:
                key = (rule["output_variable"], rule["output_term"])
                rule_data = rule_map.get(key)

                if rule_data and "inputs" in rule_data:
                    inputs = rule_data["inputs"]
                    inputs_text = " AND ".join(
                        f"({inp['input_variable']} IS {inp['input_term']})"
                        for inp in inputs
                    )
                    output_text = f"({rule['output_variable']} IS {rule['output_term']})"
                    rule_text = f"IF {inputs_text} THEN {output_text} → {round(rule['activation'], 3)}"
                else:
                    output_text = f"({rule['output_variable']} IS {rule['output_term']})"
                    rule_text = f"IF ? THEN {output_text} → {round(rule['activation'], 3)}"

                rules_display.append(
                    html.P(rule_text, className="rule-inference text-center", style={"fontSize": "0.9em"})
                )

            membership_display = [
                html.P(f"{k}: {round(v, 2)}", className="fw-bold text-center")
                for k, v in outputs.items()
            ]

            return result, rules_display, membership_display

        except Exception as e:
            print(f"Errore inferenza: {e}")
            return dash.no_update, [html.Div("Errore durante l'inferenza", className="text-danger")], []

    @dash_app.callback(
        Output({"type": "output", "variable": MATCH}, "children"),
        Input("inference-data", "data"),
        State({"type": "output", "variable": MATCH}, "id"),
        prevent_initial_call=True
    )
    def update_output_value(data, matched_id):
        """Aggiorna il valore visualizzato per ogni variabile di output dopo l'inferenza.""" 
        if not data:
            raise PreventUpdate

        var_name = matched_id["variable"]
        value = data.get("results", {}).get(var_name, 0)

        return str(round(value, 2))


#Report_page callbakcs
def fetch_data():
    """Recupera dati da backend per la pagina report.""" 
    try:
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
    """Genera le card per visualizzare le variabili (input/output) nel report.""" 
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
    """Genera la sezione di visualizzazione delle regole fuzzy nel report.""" 
    children = []
    for rule in rules:
        inputs = rule.get("inputs", [])
        inputs_text = " AND ".join(
            f"({inp['input_variable']} IS {inp['input_term']})" for inp in inputs
        )
        output_text = f"({rule['output_variable']} IS {rule['output_term']})"
        rule_text = f"IF {inputs_text} THEN {output_text}"

        children.append(
            html.Li(
                rule_text,
                className="rule-item mb-2 p-2"
            )
        )
    return children


