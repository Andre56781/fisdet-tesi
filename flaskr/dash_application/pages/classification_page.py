from dash import dcc, html
import dash_bootstrap_components as dbc

def layout() -> html.Div:
    return html.Div([
        dcc.Store(id='classification-term-count', data=0),
        dcc.Store(id="classification-confirmed"),

        dbc.Card([
            dbc.CardHeader([
                html.H4("Classification Mode", className="card-title")
            ], className="card-header-gradient d-flex justify-content-between align-items-center"),

            dbc.CardBody([
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
                        ),
                        dbc.Checklist(
                            id='classification-checkbox',
                            options=[{'label': 'Classification', 'value': 'Classification'}],
                            value=['Classification'],
                            inline=True,
                            switch=True,
                            className="pt-2"
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

                html.Div(
                    dbc.Button(
                        [html.I(className="fas fa-plus mr-2"), " Create Term"],
                        id='create-term-btn',
                        color="success",
                        className="action-btn"
                    ),
                    className="d-flex justify-content-center pt-2"
                ),

                html.Div(
                    id="classification-counter",
                    className="text-center text-info mt-2",
                    style={"display": "none"}
                ),

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
                html.Div(id='message', style={'display': 'none'}),

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
                )
            ])
        ])
    ])
