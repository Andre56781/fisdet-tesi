from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import requests

def layout() -> html.Div:
    return html.Div([
        dcc.Location(id='url_rules', refresh=False),  
        dcc.Store(id='rules-store', data=[]),  
        dcc.Store(id='variables-data', data={}),  
        html.Div(id='rules-list'),

        html.Div(
            id="main-content",
            className="content",
            style={"display": "block", "position": "relative"},
            children=[
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Creation of Rules", className="card-title"),
                        dbc.Badge("Fuzzy Rules", color="info", className="ml-2")
                    ], className="card-header-gradient d-flex justify-content-between align-items-center"),
                    
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("IF", html_for="if-dropdown", className="w-100 text-center mb-0"),
                                    dcc.Dropdown(
                                        id="if-dropdown",
                                        options=[],
                                        placeholder="Select Input Variable",
                                        className="custom-dropdown mb-2",
                                        style={"width": "300px"}  
                                    ),
                                    dbc.Label("Term", html_for="if-term-dropdown", className="w-100 text-center mb-0"),
                                    dcc.Dropdown(
                                        id="if-term-dropdown",
                                        options=[],
                                        placeholder="Select Term",
                                        className="custom-dropdown",
                                        style={"width": "300px"}  
                                    ),
                                ], md=6, className="d-flex flex-column align-items-center pe-2"),  
                                
                                dbc.Col([
                                    dbc.Label("THEN", html_for="then-dropdown", className="w-100 text-center mb-0"),
                                    dcc.Dropdown(
                                        id="then-dropdown",
                                        options=[],
                                        placeholder="Select Output Variable",
                                        className="custom-dropdown mb-2",
                                        style={"width": "300px"}  
                                    ),
                                    dbc.Label("Term", html_for="then-term-dropdown", className="w-100 text-center mb-0"),
                                    dcc.Dropdown(
                                        id="then-term-dropdown",
                                        options=[],
                                        placeholder="Select Term",
                                        className="custom-dropdown",
                                        style={"width": "300px"}  
                                    ),
                                ], md=6, className="d-flex flex-column align-items-center ps-2"),  
                            ], className="mb-3 g-3"),  
                            
                            html.Div(
                                dbc.Button(
                                    [html.I(className="fas fa-plus mr-2"), " Create Rule"],
                                    id="create-rule",
                                    color="success",
                                    className="action-btn"
                                ),
                                className="d-flex justify-content-center pt-1"
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

                            # Div for displaying error message
                            html.Div(
                                id="error-message",
                                children="",
                                style={
                                    "color": "red",
                                    "fontWeight": "bold",
                                    "textAlign": "center",
                                    "marginTop": "10px"
                                }
                            ),

                            html.Div(
                                dbc.Button(
                                    [html.I(className="fas fa-trash mr-2"), "Delete Rule"],
                                    id="delete-rule",
                                    color="danger",
                                    className="action-btn"
                                ),
                                className="d-flex justify-content-center pt-3"
                            )
                        ])
                    ]),
                ], className="main-card mx-auto")
            ]
        )
    ])
