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

    @dash_app.callback(
    [Output("current-index", "data"),
     Output("back-button", "style"),
     Output("next-button", "style")],
    [Input("next-button", "n_clicks"),
     Input("back-button", "n_clicks"),
     Input("num-variables-store", "data")],  # Aggiungi questo input per monitorare il cambiamento del numero di variabili
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
            next_button_style = {'display': 'none'} if current_index == num_variables - 1 else {'display': 'inline-block'}

        return current_index, back_button_style, next_button_style


#Inizio Logica Fuzzy
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
        State('create-term-btn', 'children')
    ],
        prevent_initial_call=True
    )
    def handle_terms(create_clicks, delete_clicks, modify_clicks, var_type, variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma, button_label):
        ctx = dash.ctx

        if not ctx.triggered:
            return [dash.no_update] * 11

        triggered_id = ctx.triggered[0]['prop_id']
        
        # Controlla se var_type è valido
        if var_type not in ['input', 'output']:
            return [dash.no_update, "Errore: var_type deve essere 'input' o 'output'", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Crea Termine']

        if triggered_id == 'create-term-btn.n_clicks':
            if button_label == 'Salva Modifica':
                terms_list, message, figure = modify_term(variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma)
                terms_list, figure = update_terms_list_and_figure(variable_name)
                return terms_list, message, figure, '', '', '', '', '', '', '', 'Crea Termine'
            else:
                terms_list, message, figure = create_term(var_type, variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma)
                if message == "Termine creato con successo!":
                    return terms_list, message, figure, '', '', '', '', '', '', '', 'Crea Termine'
                return terms_list, message, figure, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Crea Termine'

        elif 'delete-btn' in triggered_id:
            term_name_to_delete = eval(triggered_id.split('.')[0])['index']
            return delete_term(variable_name, term_name_to_delete) + ('Crea Termine',)

        elif 'modify-btn' in triggered_id:
            term_name_to_modify = eval(triggered_id.split('.')[0])['index']
            
            url = f'http://127.0.0.1:5000/api/get_term/{variable_name}/{term_name_to_modify}'
            
            headers = {'Content-Type': 'application/json'}
            response = requests.get(url)
            
            #print(f"Stato della risposta: {response.status_code}")  # Debug
            #print(f"Contenuto della risposta: {response.text}")  # Debug
            
            if response.status_code == 200:
                term_data = response.json()
                
                # Popola i campi con i dati ricevuti
                term_params = term_data.get('params', {})

                return (
                    dash.no_update, 
                    dash.no_update, 
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
                return dash.no_update, "Errore nel caricamento dei dati del termine.", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Crea Termine'

    def validate_params(params, domain_min, domain_max, function_type):
        """
        Valida che i parametri siano compresi tra domain_min e domain_max.
        """
        if function_type == 'Triangolare':
            a, b, c = params.get('a'), params.get('b'), params.get('c')
            
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
            
        elif function_type == 'Trapezoidale':
            a, b, c, d = params.get('a'), params.get('b'), params.get('c'), params.get('d')
            
            # Controllo che i parametri siano compresi tra domain_min e domain_max
            if not (domain_min <= a <= domain_max and domain_min <= b <= domain_max and domain_min <= c <= domain_max and domain_min <= d <= domain_max):
                return False, "Errore: I parametri a, b, c, d devono essere compresi tra il dominio minimo e massimo."
            
            # Controllo che a <= b <= c <= d
            if not (a <= b <= c <= d):
                return False, "Errore: I parametri devono rispettare l'ordine a <= b <= c <= d."
            
        return True, ""


    # Funzione per la creazione di un termine fuzzy
    def create_term(var_type, variable_name, domain_min, domain_max, function_type, term_name, param_a, param_b, param_c, param_d, param_mean, param_sigma):
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

        is_valid, error_message = validate_params(params, domain_min, domain_max, function_type)
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

        is_valid, error_message = validate_params(params, domain_min, domain_max, function_type)
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
        headers = {'Content-Type': 'application/json'}
        response = requests.put(f'http://127.0.0.1:5000/api/modify_term/{term_name}', json=payload)

        if response.status_code == 201:
            terms_list, figure = update_terms_list_and_figure(variable_name)
            return terms_list, "Termine modificato con successo!", figure
        else:
            error_message = response.json().get('error', 'Errore sconosciuto')
            return dash.no_update, f"Errore: {error_message}", dash.no_update


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

