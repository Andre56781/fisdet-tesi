from dash import dcc, html, Input, Output, State
from dash_bootstrap_components import Modal, ModalHeader, ModalBody
import dash_bootstrap_components as dbc

def layout() -> html.Div:
    return html.Div([
        dcc.Store(id='num-variables-store'),
        dcc.Store(id='current-index', data=0),
        dcc.Store(id='variables-data', data={}),
        dcc.Store(id='var-type-store', data="input"),
        dcc.Store(id='open-type'),
        dcc.Store(id='selected-term'),
        dcc.Store(id='defuzzy-type', data="default_value"),

        Modal(
            id="variable-modal",
            className="custom-modal",
            backdrop="static",
            size="md",
            children=[
                ModalHeader(
                    children=[
                        html.H5("Creation of Input Variables", className="mb-0"),
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
                            "Choose the number of variables",
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
                                "Submit", 
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

                            html.Div(id='params-container', className="params-container", children=[
                                dbc.RadioItems(
                                    id='open-type-radio', 
                                    options=[
                                        {'label': 'Left open', 'value': 'left'},
                                        {'label': 'Right open', 'value': 'right'}
                                    ],
                                    inline=True,
                                )
                            ]),
                            
                            html.Div(
                                dbc.Button(
                                    [html.I(className="fas fa-plus mr-2"), " Create Term"],
                                    id='create-term-btn',
                                    color="success",
                                    className="action-btn"
                                ),
                                className="d-flex justify-content-center pt-2"
                            ),
                        ]),
                        
                        dbc.Row([
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
                                                dbc.ListGroupItem("No Terms Present", style={"textAlign": "center"})
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
                    dbc.Modal(
                                id="error-modal",
                                is_open=False,
                                size="md",
                                children=[
                                    dbc.ModalHeader("Errore"),
                                    dbc.ModalBody(id="error-modal-body"),
                                ],
                                centered=True,
                                backdrop="static"
                            ),
                    ]),
                    
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
