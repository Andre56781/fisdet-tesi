from dash import html, dcc
from dash_bootstrap_components import Modal

def layout():
    return html.Div([
        # Store per il numero di variabili, l'indice corrente e i dati inseriti
        dcc.Store(id='num-variables-store'),      # Numero di variabili scelto
        dcc.Store(id='current-index', data=0),      # Indice della variabile attuale (inizia da 0)
        dcc.Store(id='variables-data', data={}),    # Dati inseriti per ogni variabile

        # Modal per la selezione del numero di variabili
        Modal(
            id="variable-modal",
            is_open=True,  # Aperto al caricamento
            children=[
                html.Div([
                    html.H3("Seleziona il numero di variabili", style={"textAlign": "center"}),
                    dcc.Input(
                        id="num-variables-input",
                        type="number",
                        min=1,
                        value=1,
                        style={"margin": "10px", "width": "200px"}
                    ),
                    html.Br(),
                    html.Button("Conferma", id="modal-submit-button", n_clicks=0, style={"margin": "10px"}),
                    html.Div(id="modal-error-message", style={"color": "red"})
                ], style={"textAlign": "center", "padding": "20px"})
            ]
        ),
        
        # Contenuto principale: input per una variabile alla volta
        html.Div(id="main-content", style={"display": "none", "position": "relative"}, children=[
            # Titolo in alto a sinistra che indica quale variabile si sta inserendo
            html.Div(id="variable-title", style={"textAlign": "left", "fontWeight": "bold", "margin": "10px"}),
            # Campo di input per la variabile corrente
            dcc.Input(id="variable-input", placeholder="Inserisci il valore", style={"margin": "10px", "width": "200px"}),
            # Bottone "Avanti" posizionato in basso a destra
            html.Button("Avanti", id="next-button", style={"position": "absolute", "bottom": "10px", "right": "10px"})
        ]),
        # Un div per mostrare messaggi finali o di conferma
        html.Div(id="output-message")
    ])
