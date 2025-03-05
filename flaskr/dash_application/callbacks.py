import dash
from dash.dependencies import Input, Output, State, ALL
from flaskr import file_handler  
from dash import dcc, html, Input, Output, State
from dash import callback_context
import plotly.graph_objects as go
import requests
import dash_bootstrap_components as dbc
import json

def register_callbacks(dash_app):
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
            # Se tutte le variabili sono state inserite, salva i dati finali usando file_handler.save_data
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
                dbc.Label("Parametro a:"),
                dbc.Input(id='param-a', type='number', value='', required=True),
                dbc.Label("Parametro b:"),
                dbc.Input(id='param-b', type='number', value='', required=True),
                dbc.Label("Parametro c:"),
                dbc.Input(id='param-c', type='number', value='', required=True),
                # Parametri invisibili
                dbc.Input(id='param-d', style={'display': 'none'}),
                dbc.Input(id='param-mean', style={'display': 'none'}),
                dbc.Input(id='param-sigma', style={'display': 'none'})
            ]
        elif function_type == 'Gaussian':
            return [
                dbc.Label("Parametro Mean:"),
                dbc.Input(id='param-mean', type='number', value='', required=True),
                dbc.Label("Parametro Sigma:"),
                dbc.Input(id='param-sigma', type='number', value='', required=True),
                # Parametri invisibili
                dbc.Input(id='param-b', style={'display': 'none'}),
                dbc.Input(id='param-a', style={'display': 'none'}),
                dbc.Input(id='param-c', style={'display': 'none'}),
                dbc.Input(id='param-d', style={'display': 'none'}),
            ]
        elif function_type == 'Trapezoidale':
            return [
                dbc.Label("Parametro a:"),
                dbc.Input(id='param-a', type='number', value='', required=True),
                dbc.Label("Parametro b:"),
                dbc.Input(id='param-b', type='number', value='', required=True),
                dbc.Label("Parametro c:"),
                dbc.Input(id='param-c', type='number', value='', required=True),
                dbc.Label("Parametro d:"),
                dbc.Input(id='param-d', type='number', value='', required=True),
                # Parametri invisibili
                dbc.Input(id='param-mean', style={'display': 'none'}),
                dbc.Input(id='param-sigma', style={'display': 'none'})
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
                terms_list, message, figure = modify_term(variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma)
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
        try:
            domain_min = float(domain_min)
            domain_max = float(domain_max)
        except (ValueError, TypeError):
            return dash.no_update, "Errore: I valori del dominio devono essere numeri.", dash.no_update

        if domain_min > domain_max:
            return dash.no_update, "Errore: Il dominio minimo non può essere maggiore del dominio massimo.", dash.no_update

        params = {}
        if function_type == 'Triangolare':
            params = {'a': param_a, 'b': param_b, 'c': param_c}
        elif function_type == 'Gaussian':
            params = {'mean': param_mean, 'sigma': param_sigma}
        elif function_type == 'Trapezoidale':
            params = {'a': param_a, 'b': param_b, 'c': param_c, 'd': param_d}

        # Creazione del payload nel formato richiesto
        payload = {
            'term_name': term_name,
            'variable_name': variable_name,
            'domain_min': domain_min,
            'domain_max': domain_max,
            'function_type': function_type,
            'params': params
        }
        try:
            file_handler.save_terms(payload)
            terms_list, figure = update_terms_list_and_figure(variable_name)
            return terms_list, "Termine creato con successo!", figure
        except Exception as e:
            print(f"Errore durante il salvataggio dei dati: {str(e)}")
            return dash.no_update, "Errore durante il salvataggio dei dati.", dash.no_update

    def delete_term(variable_name, term_name):
        # Ottieni i dati attuali
        try:
            current_data = file_handler.load_data() 
            if variable_name in current_data:
                # Rimuovi il termine specifico
                current_data[variable_name]["terms"] = [
                    term for term in current_data[variable_name]["terms"] if term["term_name"] != term_name
                ]
                # Salva i dati aggiornati
                file_handler.save_terms(current_data)
                terms_list, figure = update_terms_list_and_figure(variable_name)
                return terms_list, f"Termine '{term_name}' eliminato con successo!", figure, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
            else:
                return dash.no_update, f"Errore: Variabile '{variable_name}' non trovata.", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        except Exception as e:
            print(f"Errore durante l'eliminazione del termine: {str(e)}")
            return dash.no_update, "Errore durante l'eliminazione del termine.", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

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

        # Creazione del payload nel formato richiesto
        payload = {
        'term_name': term_name,
        'variable_name': variable_name,
        'domain_min': domain_min,
        'domain_max': domain_max,
        'function_type': function_type,
        'params': params
    }

        try:
            file_handler.save_terms(payload)
            terms_list, figure = update_terms_list_and_figure(variable_name)
            return terms_list, "Termine modificato con successo!", figure
        except Exception as e:
            print(f"Errore durante il salvataggio dei dati: {str(e)}")
            return dash.no_update, "Errore durante il salvataggio dei dati.", dash.no_update

    def update_terms_list_and_figure(variable_name):
        # Ottieni i dati salvati
        try:
            current_data = file_handler.load_data()
            if variable_name in current_data:
                terms = current_data[variable_name]["terms"]
                terms_list = [html.Div(term['term_name']) for term in terms]
                figure = go.Figure()
                return terms_list, figure
            return [], go.Figure()
        except Exception as e:
            print(f"Errore durante il caricamento dei dati: {str(e)}")
            return [], go.Figure()