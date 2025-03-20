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
                            dbc.Badge("Current Variable", color="info", className="ml-2")
                        ],
                        className="card-header-gradient d-flex justify-content-between align-items-center"
                    ),
                    
                    dbc.CardBody([
                        dbc.Form([
                            # PRIMO GRUPPO DI CAMPI
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Variable Name", html_for="variable-name", className="mb-0"),
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
                                    dbc.Label("Domain", className="form-label mb-0"),
                                    dbc.InputGroup([
                                        dbc.Input(
                                            id='domain-min',
                                            type='number',
                                            className="input-field",
                                            value='0',
                                            placeholder="0",
                                            debounce=True,
                                            required=True
                                        ),
                                        dbc.Input(
                                            id='domain-max',
                                            type='number',
                                            className="input-field",
                                            value='',
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
                                    dbc.Label("Fuzzy Function Type", className="mb-0"),
                                    dcc.Dropdown(
                                        id='function-type',
                                        options=[
                                            {'label': 'Triangular', 'value': 'Triangolare'},
                                            {'label': 'Trapezoidal', 'value': 'Trapezoidale'},
                                            {'label': 'Gaussian', 'value': 'Gaussian'},
                                        ],
                                        placeholder="Select...",
                                        className="custom-dropdown mb-3",
                                        clearable=False
                                    )
                                ], md=6),
                                
                                dbc.Col([
                                    dbc.Label("Fuzzy Term Name", className="mb-0"),
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
                                    dbc.Label("Defuzzyfication Method", className="mb-0"),
                                    dcc.Dropdown(
                                        id='defuzzy-type',
                                        options=[
                                            {'label': 'centroid', 'value': 'centroid'},
                                            {'label': 'bisector', 'value': 'bisector'},
                                            {'label': 'mom', 'value': 'mom'},
                                            {'label': 'som', 'value': 'som'},
                                            {'label': 'lom', 'value': 'lom'}
                                        ],
                                        placeholder="Select...",
                                        className="custom-dropdown mb-3 pt-2",
                                        clearable=False,
                                        value='centroid'
                                    )
                                ], md=6),
                            ]), 
                            # BOTTONE "CREA TERMINE"
                            html.Div(
                                dbc.Button(
                                    [html.I(className="fas fa-plus mr-2"), " Create Term"],
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
                                    dbc.CardHeader("Terms List"),
                                    dbc.CardBody(
                                        dbc.ListGroup(
                                            id='terms-list',
                                            children=[
                                                dbc.ListGroupItem("No terms present", style={"textAlign": "center"})
                                            ]
                                        )
                                    ),
                                    dbc.CardFooter(
                                        dbc.ButtonGroup([
                                            dbc.Button("Modify", id="modify-term-btn", color="primary", disabled=True),
                                            dbc.Button("Delete", id="delete-term-btn", color="danger", disabled=True)
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
                                    [html.I(className="fas fa-arrow-left mr-2"), "Go Back"],
                                    id="back-button",
                                    color="light",
                                    className="nav-btn",
                                    style={"display": "inline-block"}
                                ),
                                dbc.Button(
                                    [html.I(className="fas fa-arrow-right mr-2"), "Go Next"],
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