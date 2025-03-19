from dash import dcc, html, Input, Output, State
from dash_bootstrap_components import Modal, themes, ModalHeader, ModalBody
import dash_bootstrap_components as dbc


def layout() -> html.Div:
    return html.Div([
        dcc.Store(id='num-variables-store'),
        dcc.Store(id='current-index', data=0),
        dcc.Store(id='variables-data', data={}),
        dcc.Store(id='var-type-store', data="output"),
        dcc.Store(id='selected-term'),

        # Modal per numero variabili
        Modal(
            id="variable-modal",
            className="custom-modal",
            backdrop="static",
            size="md",
            children=[
                ModalHeader(
                    children=[
                        html.H5("Creazione Variabili di Output", className="mb-0"),
                        html.A(
                            dbc.Button(
                                html.I(className="fas fa-times"),
                                id="modal-close-button",
                                className="ml-auto",
                                color="link",
                                style={
                                    "color": "white", 
                                    "border": "none", 
                                    "background": "none",
                                    "padding": "0.3rem"
                                }
                            ),
                            href="/"
                        )
                    ],
                    className="gradient-header py-2 d-flex justify-content-between align-items-center",
                    close_button=False
                ),
                ModalBody(
                    html.Div([
                        html.Div(
                            "Seleziona il numero di variabili",
                            className="h6 text-muted mb-2"
                        ),
                        dcc.Input(
                            id="num-variables-input",
                            type="number",
                            min=1,
                            value=1,
                            className="modal-input mx-auto",
                            style={"width": "120px"}
                        ),
                        html.Div(
                            dbc.Button(
                                "Conferma", 
                                id="modal-submit-button", 
                                color="primary",
                                className="mt-2 btn-sm"
                            ),
                            className="text-center"
                        )
                    ], className="modal-content-wrapper px-3")
                ),
            ]
        ),
        
        # Contenuto principale
        html.Div(
            id="main-content",
            className="content",
            style={"display": "none", "position": "relative"},
            children=[
                
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
                            # PRIMO GRUPPO DI CAMPI
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Nome Variabile", html_for="variable-name", className="mb-0"),
                                    dbc.Input(
                                        id='variable-name',
                                        type='text',
                                        value='',
                                        pattern="^[a-zA-Z0-9]*$",
                                        className="input-field",
                                        debounce=True,
                                        required=True
                                    )
                                ], md=6),
                                
                                dbc.Col([
                                    dbc.Label("Dominio", className="form-label mb-0"),
                                    dbc.InputGroup([
                                        dbc.Input(
                                            id='domain-min',
                                            type='number',
                                            className="input-field",
                                            value='0', min='0', max='100',
                                            placeholder="0",
                                            debounce=True,
                                            required=True
                                        ),
                                        dbc.Input(
                                            id='domain-max',
                                            type='number',
                                            className="input-field",
                                            value='',
                                            min='0', max='100',
                                            placeholder="100",
                                            debounce=True,
                                            required=True
                                        )
                                    ], className="domain-input-group mb-3")
                                ], md=6)
                            ], className="mb-1"),

                            # SECONDO GRUPPO DI CAMPI
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Tipo Funzione Fuzzy", className="mb-0"),
                                    dcc.Dropdown(
                                        id='function-type',
                                        options=[
                                            {'label': 'Triangolare', 'value': 'Triangolare'},
                                            {'label': 'Gaussiana', 'value': 'Gaussian'},
                                            {'label': 'Trapezoidale', 'value': 'Trapezoidale'}
                                        ],
                                        placeholder="Seleziona...",
                                        className="custom-dropdown mb-3",
                                        clearable=False
                                    )
                                ], md=6),
                                
                                dbc.Col([
                                    dbc.Label("Nome Termine Fuzzy", className="mb-0"),
                                    dbc.Input(
                                        id='term-name',
                                        type='text',
                                        value='',
                                        pattern="^[a-zA-Z0-9]*$",
                                        className="input-field",
                                        debounce=True,
                                        required=True
                                    )
                                ], md=6)
                            ], className="mb-3"), 

                            # Contenitore parametri aggiuntivi
                            html.Div(id='params-container', className="params-container"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Metodo di Defuzzy", className="mb-0"),
                                    dcc.Dropdown(
                                        id='defuzzy-type',
                                        options=[
                                            {'label': 'centroid', 'value': 'centroid'},
                                            {'label': 'bisector', 'value': 'bisector'},
                                            {'label': 'mom', 'value': 'mom'},
                                            {'label': 'som', 'value': 'som'},
                                            {'label': 'lom', 'value': 'lom'}
                                        ],
                                        placeholder="Seleziona...",
                                        className="custom-dropdown mb-3 pt-2",
                                        clearable=False,
                                        value='centroid'
                                    )
                                ], md=6),
                            ]), 
                            # BOTTONE "CREA TERMINE"
                            html.Div(
                                dbc.Button(
                                    [html.I(className="fas fa-plus mr-2"), " Crea Termine"],
                                    id='create-term-btn',   
                                    color="success",
                                    className="action-btn"
                                ),
                                className="d-flex justify-content-center pt-2",
                            ),
                        ]),
                        
                        # GRAFICO (a sinistra) E LISTA TERMINI (a destra)
                        dbc.Row([
                            # Grafico a sinistra
                            dbc.Col([
                                dcc.Graph(id='graph', className="custom-graph")
                            ], md=8),

                            # Lista dei termini a destra
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Lista dei Termini"),
                                    dbc.CardBody(
                                        dbc.ListGroup(
                                            id='terms-list',
                                            children=[
                                                dbc.ListGroupItem("Nessun termine presente", style={"textAlign": "center"})
                                            ]
                                        )
                                    ),
                                    dbc.CardFooter(
                                        dbc.ButtonGroup([
                                            dbc.Button("Modifica", id="modify-term-btn", color="primary", disabled=True),
                                            dbc.Button("Elimina", id="delete-term-btn", color="danger", disabled=True)
                                        ], size="sm", className="d-flex justify-content-end")
                                    )
                                ])
                            ], md=4)
                        ], className="mt-4"),

                        # MESSAGGI
                        html.Div(id='message', className="alert-message")
                    ]),
                    
                    # FOOTER CON I PULSANTI ALLINEATI A DESTRA
                    dbc.CardFooter(
                        html.Div([
                            dbc.ButtonGroup([
                                dbc.Button(
                                    [html.I(className="fas fa-arrow-left mr-2"), "Indietro"],
                                    id="back-button",
                                    color="light",
                                    className="nav-btn",
                                    style={"display": "inline-block"}
                                ),
                                dbc.Button(
                                    [html.I(className="fas fa-arrow-right mr-2"), "Avanti"],
                                    id="next-button",
                                    color="primary",
                                    className="nav-btn",
                                    style={"display": "inline-block"}
                                )
                            ])
                        ], className="d-flex justify-content-end"),
                        className="card-footer-gradient"
                    )
                ])
            ]
        )
    ])