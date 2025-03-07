import dash
from dash import dcc, html, Input, Output, State,ctx, ALL
import plotly.graph_objects as go
import requests
import dash_bootstrap_components as dbc
import json
from flaskr import file_handler  

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

        return f"Creazione Variabile di Input {current_index + 1} di {num_vars}"

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
        ctx = dash.ctx

        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Crea Termine'

        triggered_id = ctx.triggered[0]['prop_id']

        if triggered_id == 'create-term-btn.n_clicks':
            if button_label == 'Salva Modifica':
                # Usa il nome del termine corrente come identificatore per la modifica
                terms_list, message = modify_term(variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma)
                # Aggiorna la lista dei termini e il grafico dopo la modifica
                terms_list, figure = update_terms_list_and_figure(variable_name)
                return terms_list, message, figure, '', '', '', '', '', '', '', 'Crea Termine'
            else:
                # Creazione del termine
                terms_list, message, figure = create_term(variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma)
                if message == "Termine creato con successo!":
                    return terms_list, message, figure, '', '', '', '', '', '', '', 'Crea Termine'
                return terms_list, message, figure, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Crea Termine'

        elif 'delete-btn' in triggered_id:
            # Estrai l'indice del termine da eliminare in modo più sicuro
            term_name_to_delete = eval(triggered_id.split('.')[0])['index']
            return delete_term(variable_name, term_name_to_delete) + ('Crea Termine',)

        elif 'modify-btn' in triggered_id:
            term_name_to_modify = eval(triggered_id.split('.')[0])['index']
            
            # Recupera i dati del termine da modificare utilizzando l'endpoint del backend
            response = requests.get(f'http://127.0.0.1:5000/get_term/{variable_name}/{term_name_to_modify}')
        
            if response.status_code == 200:
                term_data = response.json()
                
                # Popola i campi con i dati ricevuti
                term_params = term_data.get('params', {})

                return (
                    dash.no_update, 
                    "Dati del termine caricati, puoi modificarli.",
                    dash.no_update,  # Se necessario, inserisci la logica per aggiornare il grafico
                    term_data.get('term_name', ''),  # Nome del termine
                    term_params.get('a', ''),    # Parametro A
                    term_params.get('b', ''),    # Parametro B
                    term_params.get('c', ''),    # Parametro C
                    term_params.get('d', ''),    # Parametro D
                    term_params.get('mean', ''),    # Parametro Mean
                    term_params.get('sigma', ''),   # Parametro Sigma
                    'Salva Modifica'
                )
            else:
                return dash.no_update, "Errore nel caricamento dei dati del termine.", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Crea Termine'

        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Crea Termine'


    # Funzione per la creazione di un termine fuzzy
    def create_term(variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma):
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
        headers = {'Content-Type': 'application/json'}
        response = requests.post('http://127.0.0.1:5000/api/create_term', json=payload)


        if response.status_code == 201:
            terms_list, figure = update_terms_list_and_figure(variable_name)
            return terms_list, "Termine creato con successo!", figure
        else:
            error_message = response.json().get('error', 'Errore sconosciuto')
            return dash.no_update, f"Errore: {error_message}", dash.no_update

    # Funzione per l'eliminazione di un termine fuzzy
    def delete_term(variable_name, term_name):
        response = requests.post(f'http://127.0.0.1:5000/api/delete_term/{term_name}')

        if response.status_code == 200:
            # Dopo aver eliminato il termine, aggiorna la lista e il grafico
            terms_list, figure = update_terms_list_and_figure(variable_name)
            # Restituisci 10 valori, includendo terms_list e figure aggiornati
            return terms_list, f"Termine '{term_name}' eliminato con successo!", figure, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        else:
            # Restituisci un errore se l'eliminazione fallisce, con dash.no_update per i valori non modificati
            return dash.no_update, f"Errore nell'eliminazione del termine: {response.json().get('error', 'Errore sconosciuto')}", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Funzione per la modifica di un termine fuzzy
    def modify_term(variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma):
        # Aggiungi controllo sul dominio minimo e massimo
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
        headers = {'Content-Type': 'application/json'}
        response = requests.put(f'http://127.0.0.1:5000/api/modify_term/{term_name}', json=payload)

        if response.status_code == 201:
            terms_list = update_terms_list_and_figure(variable_name)
            return terms_list, f"Termine '{term_name}' Modificato con successo!"
        else:
            # Restituisci un errore se la Modifica fallisce, con dash.no_update per i valori non modificati
            return dash.no_update, f"Errore nella Modifica del termine: {response.json().get('error', 'Errore sconosciuto')}"

    # Funzione per aggiornare la lista dei termini e il grafico
    def update_terms_list_and_figure(variable_name):
        if variable_name:
            terms_response = requests.get('http://127.0.0.1:5000/api/get_terms')
            if terms_response.status_code == 200:
                terms_data = terms_response.json()
                terms_list = []
                data = []
                if variable_name in terms_data:
                        variable_data = terms_data[variable_name]
                        for term in variable_data['terms']:
                            terms_list.append(
                                html.Div([
                                    html.Span(f"Termine: {term['term_name']} ({variable_name})"),
                                    html.Button('Modifica', id={'type': 'modify-btn', 'index': term['term_name']}),
                                    html.Button('Elimina', id={'type': 'delete-btn', 'index': term['term_name']}),
                                ])
                            )
                            if 'x' in term and 'y' in term:
                                data.append(go.Scatter(x=term['x'], y=term['y'], mode='lines', name=f"{term['term_name']} ({variable_name})"))
                figure = {
                        'data': data,
                        'layout': go.Layout(title=f"Termini Fuzzy - {variable_name}", xaxis={'title': 'X'}, yaxis={'title': 'Y'}, showlegend=True)
                    }
                return terms_list, figure
            else:
                return [html.Div(f"Nessun termine trovato per la variabile: {variable_name}.")], go.Figure()
        else:
            return [html.Div("Errore nel recupero dei termini.")]

