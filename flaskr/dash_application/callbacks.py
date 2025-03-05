import dash
from dash.dependencies import Input, Output, State, ALL
from flaskr import file_handler  
from dash import dcc, html
import plotly.graph_objects as go
import requests
import numpy as np
import skfuzzy as fuzz
from dash.exceptions import PreventUpdate

def register_callbacks(dash_app):
    # Callback per chiusura modal
    @dash_app.callback(
        Output("variable-modal", "is_open"),
        Input("modal-submit-button", "n_clicks"),
        State("num-variables-input", "value"),
        prevent_initial_call=True
    )
    def handle_modal_submit(n_clicks, num_vars):
        if n_clicks is None:
            raise PreventUpdate
            
        if num_vars and int(num_vars) > 0:
            return False
        return True

@dash_app.callback(
    [Output("current-index", "data"),
     Output("variable-name", "value"),
     Output("domain-min", "value"),
     Output("domain-max", "value"),
     Output("output-message", "children"),
     Output("variables-data", "data"),
     Output("progress-bar", "value")],
    [Input("next-button", "n_clicks"),
     Input("back-button", "n_clicks")],
    [State("current-index", "data"),
     State("num-variables-store", "data"),
     State("variables-data", "data"),
     State("variable-name", "value"),
     State("domain-min", "value"),
     State("domain-max", "value")]
)
def handle_navigation(next_clicks, back_clicks, current_idx, total_vars, vars_data, name, dmin, dmax):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    vars_data = vars_data or {}
    msg = ""
    progress = 0

    # Validazione campi
    if triggered_id == "next-button":
        if not all([name, dmin, dmax]):
            return [dash.no_update]*6 + ["Compila tutti i campi!"]
        
        try:
            vars_data[str(current_idx)] = {
                "name": name,
                "domain": [float(dmin), float(dmax)],
                "terms": []
            }
        except ValueError:
            return [dash.no_update]*6 + ["Valori non validi"]

    # Gestione navigazione
    if triggered_id == "next-button":
        new_idx = current_idx + 1
        progress = (new_idx / total_vars) * 100
        
        if new_idx >= total_vars:
            try:
                file_handler.save_data(vars_data)
                msg = "Dati salvati con successo!"
                return [current_idx, name, dmin, dmax, msg, vars_data, progress]
            except Exception as e:
                msg = f"Errore salvataggio: {str(e)}"
                return [current_idx, name, dmin, dmax, msg, vars_data, progress]
            
        return [new_idx, "", "", "", "", vars_data, progress]

    elif triggered_id == "back-button":
        new_idx = max(0, current_idx - 1)
        progress = (new_idx / total_vars) * 100
        prev_data = vars_data.get(str(new_idx), {})
        return [
            new_idx,
            prev_data.get("name", ""),
            prev_data.get("domain", [0,0])[0],
            prev_data.get("domain", [0,0])[1],
            "",
            vars_data,
            progress
        ]

    return [dash.no_update]*7

    # Callback termini fuzzy
    @dash_app.callback(
        [Output('terms-list', 'children'),
         Output('message', 'children'),
         Output('graph', 'figure'),
         Output('term-name', 'value'),
         Output('param-a', 'value'),
         Output('param-b', 'value'),
         Output('param-c', 'value'),
         Output('param-d', 'value'),
         Output('param-mean', 'value'),
         Output('param-sigma', 'value'),
         Output('create-term-btn', 'children')],
        [Input('create-term-btn', 'n_clicks'),
         Input({'type': 'delete-btn', 'index': ALL}, 'n_clicks'),
         Input({'type': 'modify-btn', 'index': ALL}, 'n_clicks'),
         Input('reset-fields', 'n_clicks')],
        [State('current-index', 'data'),
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
         State('create-term-btn', 'children')]
    )
    def handle_terms(create_clicks, del_clicks, mod_clicks, reset_clicks, current_idx, var_name, dom_min, dom_max, 
                    func_type, term_name, a, b, c, d, mean, sigma, btn_label):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        triggered_id = ctx.triggered[0]['prop_id']
        terms = []
        figure = go.Figure()
        msg = ""
        
        # Logica creazione/modifica/eliminazione termini
        # ... (implementa la logica specifica qui)
        
        return [terms, msg, figure, '', '', '', '', '', '', '', 'Crea Termine']

    # Funzioni helper
    def generate_figure(terms):
        fig = go.Figure()
        # ... (mantieni la logica esistente)
        return fig

    def generate_terms_list(terms):
        # ... (mantieni la logica esistente)
        return html.Div()