import dash
from dash.dependencies import Input, Output, State, ALL
from flaskr import file_handler  # Assicurati che il percorso sia corretto

def register_callbacks(dash_app):
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
            # Salva il numero di variabili su file (opzionale)
            file_handler.save_data({"num_variables": num_vars})
            # Mostra il contenuto principale con il bottone "Avanti"
            return [False, {"display": "block", "position": "relative"}, num_vars, ""]
        except:
            return [True, {"display": "none"}, None, "Inserisci un numero valido (≥ 1)"]

    @dash_app.callback(
        Output("variable-title", "children"),
        [Input("current-index", "data"),
         Input("num-variables-store", "data")]
    )
    def update_title(current_index, num_vars):
        if num_vars is None or current_index is None:
            return ""
        return f"Variabile {current_index + 1} di {num_vars}"

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
        # Salva il valore inserito per la variabile corrente
        variables_data[str(current_index)] = input_value

        new_index = current_index + 1
        if new_index < num_vars:
            # Passa alla variabile successiva e azzera il campo input
            return new_index, "", "", variables_data
        else:
            # Se tutte le variabili sono state inserite, salva i dati finali su file e mostra un messaggio di completamento
            file_handler.save_data({"variables": variables_data})
            return current_index, input_value, "Hai inserito tutte le variabili!", variables_data
