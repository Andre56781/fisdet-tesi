from dash import dash, dcc, html, Input, Output, State
from dash_bootstrap_components import Modal


def layout():
    return html.Div([
        # Store per il numero di variabili, l'indice corrente e i dati inseriti
        dcc.Store(id='num-variables-store'),      # Numero di variabili scelto
        dcc.Store(id='current-index', data=0),      # Indice della variabile attuale (inizia da 0)
        dcc.Store(id='variables-data', data={}),    # Dati inseriti per ogni variabile

        # Modal per la selezione del numero di variabili POPUP VAR
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
        html.H1("Gestione Termini Fuzzy"),
        html.Div(id="variable-title", style={"textAlign": "left", "fontWeight": "bold", "margin": "10px"}), #N var da x su x
            
            # Input per il nome della variabile
        html.Label("Nome Variabile:"),
        dcc.Input(id='variable-name', type='text',pattern="^[a-zA-Z0-9]*$", value='', debounce=True, required=True),

        # Input per il dominio minimo e massimo
        html.Label("Dominio Minimo:"),
        dcc.Input(id='domain-min', type='number', value=0, debounce=True, required=True),

        html.Label("Dominio Massimo:"),
        dcc.Input(id='domain-max', type='number', value='', debounce=True, required=True),

        # Dropdown per selezionare la funzione fuzzy
        html.Label("Tipo di Funzione Fuzzy:"),
        dcc.Dropdown(
            id='function-type',
            options=[
                {'label': 'Triangolare', 'value': 'Triangolare'},
                {'label': 'Gaussiana', 'value': 'Gaussian'},
                {'label': 'Trapezoidale', 'value': 'Trapezoidale'}
            ],
            value=''
        ),

        # Input per il nome del termine
        html.Label("Nome del Termine Fuzzy:"),
        dcc.Input(id='term-name', type='text', value='', pattern="^[a-zA-Z0-9]*$", debounce=True, required=True),

        # Contenitore per i parametri della funzione fuzzy
        html.Label("Parametri Funzione Fuzzy:"),
        html.Div(id='params-container'),

        # Bottone per creare il termine fuzzy
        html.Button('Crea Termine', id='create-term-btn', n_clicks=0),

        # Area per visualizzare il grafico del termine fuzzy
        dcc.Graph(id='graph'),

        # Messaggio di conferma
        html.Div(id='message', style={'marginTop': '20px'}),

        # Componente Store per mantenere i parametri
        dcc.Store(id='params-store'),

        # Lista dei termini (aggiunto per esempio)
        html.Div(id='terms-list'),

            html.Button("Avanti", id="next-button", style={"position": "absolute", "bottom": "10px", "right": "10px"}) #bottone avanti di var
        ]),
        # Un div per mostrare messaggi finali o di conferma
        html.Div(id="output-message")
    ])
