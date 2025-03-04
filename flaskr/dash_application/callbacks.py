import dash
from dash.dependencies import Input, Output, State, ALL
from flaskr import file_handler  
from dash import dcc, html, Input, Output, State
from dash import callback_context
import plotly.graph_objects as go
import requests

def register_callbacks(dash_app):
    # Callback per la gestione della sottomissione del modal e la visualizzazione del contenuto principale
    @dash_app.callback(
        [Output("variable-modal", "is_open"),
         Output("main-content", "style"),
         Output("num-variables-store", "data"),
         Output("modal-error-message", "children")],
        [Input("modal-submit-button", "n_clicks")],
        [State("num-variables-input", "value")]
    )
    def handle_modal_submit(n_clicks, num_variables):
        if not n_clicks:
            return [True, {"display": "none"}, None, ""]
        try:
            num_vars = int(num_variables)
            if num_vars < 1:
                raise ValueError
            # Salva il numero di variabili su un file (opzionale)
            try:
                file_handler.save_data({"num_variables": num_vars})
            except Exception as e:
                return [True, {"display": "none"}, None, f"Errore nel salvataggio dei dati: {str(e)}"]
            # Mostra il contenuto principale con il pulsante "Next"
            return [False, {"display": "block", "position": "relative"}, num_vars, ""]
        except:
            return [True, {"display": "none"}, None, "Inserisci un numero valido (≥ 1)"]

    # Callback per aggiornare il titolo della variabile (es. "Variabile X di Y")
    @dash_app.callback(
        Output("variable-title", "children"),
        [Input("current-index", "data"),
         Input("num-variables-store", "data")]
    )
    def update_title(current_index, num_vars):
        if num_vars is None or current_index is None:
            return ""
        try:
            current_index = int(current_index)
        except (ValueError, TypeError):
            return "Errore: Indice della variabile non valido."
        
        return f"Variabile {current_index + 1} di {num_vars}"

    # Callback per la gestione della logica del pulsante "Next"
    @dash_app.callback(
        [Output("current-index", "data"),
         Output("variable-input", "value"),
         Output("output-message", "children"),
         Output("variables-data", "data")],
        [Input("next-button", "n_clicks")],
        [State("variable-input", "value"),
         State("current-index", "data"),
         State("num-variables-store", "data"),
         State("variables-data", "data")]
    )
    def handle_next(n_clicks, input_value, current_index, num_vars, variables_data):
        if not n_clicks:
            raise dash.exceptions.PreventUpdate

        if variables_data is None:
            variables_data = {}
        # Salva il valore della variabile corrente
        variables_data[str(current_index)] = input_value

        new_index = current_index + 1
        if new_index < num_vars:
            # Passa alla variabile successiva e svuota il campo di input
            return new_index, "", "", variables_data
        else:
            # Se tutte le variabili sono state inserite, salva i dati finali e mostra il messaggio di completamento
            file_handler.save_data({"variables": variables_data})
            return current_index, input_value, "Hai inserito tutte le variabili!", variables_data

    # Funzione per generare i parametri in base al tipo di funzione fuzzy
    @dash_app.callback(
        Output('params-container', 'children'),
        Input('function-type', 'value')
    )
    def update_params(function_type):
        if function_type == 'Triangolare':
            return [
                html.Label("Parametro a:"),
                dcc.Input(id='param-a', type='number', value='', required=True),
                html.Label("Parametro b:"),
                dcc.Input(id='param-b', type='number', value='', required=True),
                html.Label("Parametro c:"),
                dcc.Input(id='param-c', type='number', value='', required=True),
                # Parametri invisibili
                dcc.Input(id='param-d', style={'display': 'none'}),
                dcc.Input(id='param-mean', style={'display': 'none'}),
                dcc.Input(id='param-sigma', style={'display': 'none'})
            ]
        elif function_type == 'Gaussian':
            return [
                html.Label("Parametro Mean:"),
                dcc.Input(id='param-mean', type='number', value='', required=True),
                html.Label("Parametro Sigma:"),
                dcc.Input(id='param-sigma', type='number', value='', required=True),
                # Parametri invisibili
                dcc.Input(id='param-b', style={'display': 'none'}),
                dcc.Input(id='param-a', style={'display': 'none'}),
                dcc.Input(id='param-c', style={'display': 'none'}),
                dcc.Input(id='param-d', style={'display': 'none'}),
            ]
        elif function_type == 'Trapezoidale':
            return [
                html.Label("Parametro a:"),
                dcc.Input(id='param-a', type='number', value='', required=True),
                html.Label("Parametro b:"),
                dcc.Input(id='param-b', type='number', value='', required=True),
                html.Label("Parametro c:"),
                dcc.Input(id='param-c', type='number', value='', required=True),
                html.Label("Parametro d:"),
                dcc.Input(id='param-d', type='number', value='', required=True),
                # Parametri invisibili
                dcc.Input(id='param-mean', style={'display': 'none'}),
                dcc.Input(id='param-sigma', style={'display': 'none'})
            ]
        else:
            return []

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
            Input({'type': 'delete-btn', 'index': ALL}, 'n_clicks'),
            Input({'type': 'modify-btn', 'index': ALL}, 'n_clicks')
        ],
        [
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
            State('create-term-btn', 'children')
        ],
        prevent_initial_call=True
    )
    def handle_terms(create_clicks, delete_clicks, modify_clicks, variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma, button_label):
        ctx = callback_context

        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Crea Termine'

        triggered_id = ctx.triggered[0]['prop_id']

        if triggered_id == 'create-term-btn.n_clicks':
            if button_label == 'Salva Modifica':
                terms_list, message = modify_term(variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma)
                terms_list, figure = update_terms_list_and_figure(variable_name)
                return terms_list, message, figure, '', '', '', '', '', '', '', 'Crea Termine'
            else:
                terms_list, message, figure = create_term(variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma)
                if message == "Termine creato con successo!":
                    return terms_list, message, figure, '', '', '', '', '', '', '', 'Crea Termine'
                return terms_list, message, figure, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Crea Termine'

        elif 'delete-btn' in triggered_id:
            term_name_to_delete = eval(triggered_id.split('.')[0])['index']
            return delete_term(variable_name, term_name_to_delete) + ('Crea Termine',)

        elif 'modify-btn' in triggered_id:
            term_name_to_modify = eval(triggered_id.split('.')[0])['index']
            response = requests.get(f'http://127.0.0.1:5000/get_term/{variable_name}/{term_name_to_modify}')
        
            if response.status_code == 200:
                term_data = response.json()
                term_params = term_data.get('params', {})

                return (
                    dash.no_update, 
                    "Dati del termine caricati, puoi modificarli.",
                    dash.no_update,
                    term_data.get('term_name', ''),
                    term_params.get('a', ''),
                    term_params.get('b', ''),
                    term_params.get('c', ''),
                    term_params.get('d', ''),
                    term_params.get('mean', ''),
                    term_params.get('sigma', ''),
                    'Salva Modifica'
                )
            else:
                # Ensure all 11 values are returned
                return (
                    dash.no_update,
                    "Errore nel caricamento dei dati del termine.",
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    'Crea Termine'
                )

        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Crea Termine'


    def create_term(variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma):
        if domain_min > domain_max:
            return dash.no_update, "Errore: Il dominio minimo non può essere maggiore del dominio massimo.", dash.no_update

        params = {}
        if function_type == 'Triangolare':
            params = {'a': param_a, 'b': param_b, 'c': param_c}
        elif function_type == 'Gaussian':
            params = {'mean': param_mean, 'sigma': param_sigma}
        elif function_type == 'Trapezoidale':
            params = {'a': param_a, 'b': param_b, 'c': param_c, 'd': param_d}

        payload = {
            'term_name': term_name,
            'variable_name': variable_name,
            'domain_min': domain_min,
            'domain_max': domain_max,
            'function_type': function_type,
            'params': params
        }
        try:
            response = requests.post('http://127.0.0.1:5000/create_term', json=payload)

            if response.status_code == 200 or response.status_code == 201:
                try:
                    response_data = response.json()  # Attempt to parse JSON
                    terms_list, figure = update_terms_list_and_figure(variable_name)
                    return terms_list, "Termine creato con successo!", figure
                except requests.exceptions.JSONDecodeError:
                    print(f"Error: Response is not JSON. Server response: {response.text}")
                    return dash.no_update, "Errore: La risposta del server non è valida.", dash.no_update
            else:
                return dash.no_update, f"Errore: {response.text}", dash.no_update

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            return dash.no_update, "Errore nella comunicazione con il server.", dash.no_update



    def delete_term(variable_name, term_name):
        response = requests.post(f'http://127.0.0.1:5000/delete_term/{term_name}')

        if response.status_code == 200:
            terms_list, figure = update_terms_list_and_figure(variable_name)
            return terms_list, f"Termine '{term_name}' eliminato con successo!", figure, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        else:
            return dash.no_update, f"Errore nell'eliminazione del termine: {response.json().get('error', 'Errore sconosciuto')}", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    def modify_term(variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma):
        if domain_min > domain_max:
            return dash.no_update, "Errore: Il dominio minimo non può essere maggiore del dominio massimo."

        params = {}
        if function_type == 'Triangolare':
            params = {'a': param_a, 'b': param_b, 'c': param_c}
        elif function_type == 'Gaussian':
            params = {'mean': param_mean, 'sigma': param_sigma}
        elif function_type == 'Trapezoidale':
            params = {'a': param_a, 'b': param_b, 'c': param_c, 'd': param_d}

        payload = {
            'term_name': term_name,
            'variable_name': variable_name,
            'domain_min': domain_min,
            'domain_max': domain_max,
            'function_type': function_type,
            'params': params
        }
        response = requests.put(f'http://127.0.0.1:5000/modify_term', json=payload)

        if response.status_code == 200:
            terms_list, figure = update_terms_list_and_figure(variable_name)
            return terms_list, "Termine modificato con successo!", figure
        else:
            error_message = response.json().get('error', 'Errore sconosciuto')
            return dash.no_update, f"Errore: {error_message}", dash.no_update

    def update_terms_list_and_figure(variable_name):
        response = requests.get(f'http://127.0.0.1:5000/get_terms/{variable_name}')
        if response.status_code == 200:
            terms = response.json().get('terms', [])
            terms_list = [html.Div(term) for term in terms]
            # Create your plotly figure here
            figure = go.Figure()
            return terms_list, figure
        return [], go.Figure()
