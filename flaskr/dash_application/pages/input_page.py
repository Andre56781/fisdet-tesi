from dash import dcc, html, Input, Output, State
from dash_bootstrap_components import Modal, themes, ModalHeader, ModalBody
import dash_bootstrap_components as dbc

def layout():
    return html.Div([
        dcc.Store(id='num-variables-store'),
        dcc.Store(id='current-index', data=0),
        dcc.Store(id='variables-data', data={}),
        html.Div(id='terms-list', children=[]),
        # Modal per numero variabili
        Modal(
            id="variable-modal",
            is_open=True,
            className="custom-modal",
            backdrop="static",
            children=[
                ModalHeader("Configurazione Iniziale", className="gradient-header"),
                ModalBody(
                html.Div([
                    html.H4("Seleziona il numero di variabili", style={"textAlign": "center"}),
                    dcc.Input(
                        id="num-variables-input",
                        type="number",
                        min=1,
                        value=1,
                        className="modal-input"
                    ),
                        dbc.Button("Conferma", id="modal-submit-button", color="primary", className="mt-3")
                     ], className="modal-content-wrapper")
                ),
            ]
        ),
        
        # Contenuto principale
        html.Div(id="main-content", className="content", children=[
            dbc.Progress(id="progress-bar", className="my-4 custom-progress"),
            
            dbc.Card([
                dbc.CardHeader(
                    [
                        html.H4(id="variable-title", className="card-title"),
                        dbc.Badge("Variabile Corrente", color="info", className="ml-2")
                    ],
                    className="card-header-gradient d-flex justify-content-between align-items-center"
                ),
                
                dbc.CardBody([
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Nome Variabile", html_for="variable-name"),
                                dbc.Input(id='variable-name', type='text', value='', pattern="^[a-zA-Z0-9]*$", className="mb-3 input-field", debounce=True, required=True)
                            ], md=6),
                            
                            dbc.Col([
                                dbc.Label("Dominio", className="form-label"),
                                dbc.InputGroup([
                                    dbc.Input(id='domain-min', type='number', className="input-field", value='0', debounce=True, required=True, ),
                                    dbc.Input(id='domain-max', type='number', className="input-field", value='', debounce=True, required=True, )
                                ], className="domain-input-group")
                            ], md=6)
                        ], className="mb-4"),

                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Tipo Funzione Fuzzy"),
                                dcc.Dropdown(
                                    id='function-type',
                                    options=[
                                        {'label': 'Triangolare', 'value': 'Triangolare'},
                                        {'label': 'Gaussiana', 'value': 'Gaussian'},
                                        {'label': 'Trapezoidale', 'value': 'Trapezoidale'}
                                    ],
                                    className="custom-dropdown"
                                )
                            ], md=6),
                            
                            dbc.Col([
                                dbc.Label("Nome Termine Fuzzy"),
                                dbc.Input(id='term-name', type='text', value='', pattern="^[a-zA-Z0-9]*$", className="input-field", debounce=True, required=True)
                            ], md=6)
                        ], className="mb-4"),

                        html.Div(id='params-container', className="params-container"),
                        
                        dbc.ButtonGroup([
                            dbc.Button(
                                [html.I(className="fas fa-plus mr-2"), " Crea Termine"],
                                id='create-term-btn',
                                color="success",
                                className="action-btn"
                            ),
                            dbc.Button(
                                "Resetta Campi",
                                id="reset-fields",
                                color="secondary",
                                className="action-btn"
                            )
                        ], className="mb-4"),
                        
                        dcc.Graph(id='graph', className="custom-graph"),
                        html.Div(id='message', className="alert-message")
                    ])
                ]),
                
                dbc.CardFooter([
                    dbc.ButtonGroup([
                        dbc.Button(
                            [html.I(className="fas fa-arrow-left mr-2"), "Indietro"],
                            id="back-button",
                            color="light",
                            className="nav-btn"
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-arrow-right mr-2"), "Avanti"],
                            id="next-button",
                            color="primary",
                            className="nav-btn"
                        )
                    ], className="float-right")
                ], className="card-footer-gradient")
            ], className="main-card")
        ]),

        # Riepilogo finale
        html.Div(id="summary-section", className="summary-section", children=[
            dbc.Card([
                dbc.CardHeader("Riepilogo Finale", className="summary-header"),
                dbc.CardBody(id="summary-content", className="summary-body"),
                dbc.CardFooter(
                    dbc.Button(
                        [html.I(className="fas fa-save mr-2"), "Salva Configurazione"],
                        id="save-config",
                        color="success",
                        className="save-btn"
                    )
                )
            ])
        ])
    ])