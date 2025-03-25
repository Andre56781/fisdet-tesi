from dash import dcc, html
import dash_bootstrap_components as dbc

def layout() -> html.Div:
    return html.Div([
        dcc.Store(id='num-variables-store', data=0),
        dcc.Store(id='current-index', data=0),
        dcc.Store(id='variables-data', data={}),
        dcc.Store(id='var-type-store', data="output"),
        dcc.Store(id='open-type'),
        dcc.Store(id='selected-term'),
        dcc.Store(id='selected-rule-index', data=None),
        dcc.Store(id='classification-term-count', data=0),  
        dcc.Store(id='classification-confirmed', data=False),

        dbc.Modal(
            id="classification-warning-modal",
            is_open=False,
            backdrop="static",
            centered=True,
            children=[
                dbc.ModalHeader("Warning"),
                dbc.ModalBody("Do you really want to change the type? If confirmed, you will lose all output data."),
                dbc.ModalFooter([
                    dbc.Button("Yes", id="confirm-classification", color="danger", className="mr-2"),
                    dbc.Button("No", id="cancel-classification", color="secondary")
                ])
            ]
        ),

        html.Div(
            id="main-content",
            className="content",
            style={"display": "block", "position": "relative"},
            children=[
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Output Variable", className="card-title"),
                    ], className="card-header-gradient d-flex justify-content-between align-items-center"
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

                            dbc.Col(id="dynamic-right-column", md=6)
                        ], className="mb-3"),

                        html.Div(id="output-hideable-fields", children=[
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
                                    clearable=False,
                                    persistence=True
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
                                        className="custom-dropdown mb-3",
                                        clearable=False,
                                        value='centroid'
                                    )
                                ], md=6),

                                dbc.Col([
                                    #dbc.Label("Classification", className="mb-0 d-block text-end"), MOMENTANEO
                                    dbc.Checklist(
                                        id='classification-checkbox',
                                        #options=[{'label': '', 'value': 'Classification'}], MOMENTANEO
                                        value=[],
                                        inline=True,
                                        switch=False,
                                        className="pt-2 float-end"
                                    )
                                ], md=6, className="text-end")
                            ], className="mb-3")
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

                        html.Div(id="classification-counter", style={"display": "none"}, className="text-center text-info mt-2")
                    ]),

                    dbc.Row([
                        dbc.Col([
                            html.Div(id="graph-container", children=[
                                dcc.Graph(id='graph', className="custom-graph")
                            ])
                        ], md=8),

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
                
                ])
            ])
        ])
    ])
