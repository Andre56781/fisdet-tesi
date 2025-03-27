from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import requests

def layout() -> html.Div:
    return html.Div([
        dcc.Location(id='url_rules', refresh=False),  
        dcc.Store(id='rules-store', data=[]),  
        dcc.Store(id='input-variables', data=[]),  
        dcc.Store(id='input-count', data=0),       
        dcc.Store(id='variables-data', data={}),
        dcc.Store(id="selected-rule-id", data=None),

        html.Div(
            id="main-content",
            className="content",
            style={"display": "block", "position": "relative"},
            children=[
                dbc.Card([
                    dbc.CardHeader(
                        [
                            html.H4("Creation of Rules", className="card-title text-center"),
                            dbc.Badge("Fuzzy Rules", color="info", className="ml-2")
                        ],
                        className="card-header-gradient d-flex justify-content-between align-items-center"
                    ),
                    dbc.CardBody([
                        dbc.Form([
                            # Contenitore degli IF (input)
                            html.Div(
                                id="input-container",
                                className="d-flex flex-wrap gap-3 justify-content-center",
                                children=[]
                            ),
                            html.Div(
                                dbc.Button(
                                    [html.I(className="fas fa-plus", style={"marginRight": "8px"}), "Add Input"],
                                    id="add-input",
                                    color="primary",
                                    className="action-btn"
                                ),
                                className="d-flex justify-content-center pt-3 mb-3"
                            ),
                            # Contenitore dei THEN centrato
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("THEN Variable", html_for="then-dropdown", className="w-100 text-center mb-0"),
                                    dcc.Dropdown(
                                        id="then-dropdown",
                                        options=[],
                                        value=None,
                                        disabled=True,
                                        className="custom-dropdown mb-2",
                                        style={"width": "300px"}
                                    ),
                                    dbc.Label("THEN Term", html_for="then-term-dropdown", className="w-100 text-center mb-0"),
                                    dcc.Dropdown(
                                        id="then-term-dropdown",
                                        options=[],
                                        placeholder="Select Term",
                                        className="custom-dropdown",
                                        style={"width": "300px"}
                                    ),
                                ], md=6, className="d-flex flex-column align-items-center")
                            ], className="mb-3 g-3 justify-content-center"),
                            
                            html.Div(
                                dbc.Button(
                                    [html.I(className="fas fa-plus", style={"marginRight": "8px"}), "Create Rule"],
                                    id="create-rule",
                                    color="success",
                                    className="action-btn"
                                ),
                                className="d-flex justify-content-center pt-3"
                            ),
                            
                            html.Div(
                                id="rules-list", 
                                children=[], 
                                style={
                                    "border": "1px solid #ccc", 
                                    "minHeight": "100px", 
                                    "padding": "10px", 
                                    "marginTop": "20px", 
                                    "backgroundColor": "#fff", 
                                    "width": "80%", 
                                    "maxWidth": "800px", 
                                    "marginLeft": "auto", 
                                    "marginRight": "auto"
                                }
                            ),
                            
                            html.Div(
                                id="error-message", 
                                style={
                                    "color": "red", 
                                    "fontWeight": "bold", 
                                    "textAlign": "center", 
                                    "marginTop": "10px"
                                }
                            ),
                            
                            html.Div(
                                dbc.Button(
                                    [html.I(className="fas fa-trash", style={"marginRight": "8px"}), "Delete Rule"],
                                    id="delete-rule",
                                    color="danger",
                                    className="action-btn"
                                ),
                                className="d-flex justify-content-center pt-3"
                            ),
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
                    ]),
                    dbc.CardFooter(
                        className="d-flex justify-content-center gap-2",
                        children=[
                            dbc.Button(
                                [html.I(className="fas fa-list-check mr-2", style={"marginRight": "8px"}), "Test"],
                                href="/test",
                                color="primary",
                                size="md",
                                style={
                                    "minWidth": "120px",
                                    "minHeight": "40px",
                                    "borderRadius": "8px",
                                    "fontWeight": "500",
                                    "boxShadow": "0px 2px 4px rgba(0, 0, 0, 0.1)"
                                },
                                className="footer-btn"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-chart-bar mr-2", style={"marginRight": "8px"}), "Report"],
                                href="/report",
                                color="info",
                                size="md",
                                style={
                                    "minWidth": "120px",
                                    "minHeight": "40px",
                                    "borderRadius": "8px",
                                    "fontWeight": "500",
                                    "boxShadow": "0px 2px 4px rgba(0, 0, 0, 0.1)"
                                },
                                className="footer-btn"
                            )
                        ]
                    )
                ], className="main-card mx-auto", style={"maxWidth": "900px", "boxShadow": "0 4px 8px rgba(0,0,0,0.1)"})
            ]
        )
    ])
