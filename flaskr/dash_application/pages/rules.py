from dash import html, dcc

def layout():
    return html.Div([
        html.H1("Inserisci Dati"),
        dcc.Input(id="user-input", type="text", placeholder="Scrivi qui..."),
        html.Button("Invia", id="submit-button"),
        html.Div(id="output-message"),
    ])