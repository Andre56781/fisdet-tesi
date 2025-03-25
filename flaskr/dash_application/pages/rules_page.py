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
                    dbc.CardHeader([
                        html.H4("Creation of Rules", className="card-title"),
                        dbc.Badge("Fuzzy Rules", color="info", className="ml-2")
                    ], className="card-header-gradient d-flex justify-content-between align-items-center"),
                    dbc.CardBody([
                        dbc.Form([
                            html.Div(
                                id="input-container",
                                className="d-flex flex-wrap gap-3",
                                children=[]
                            ),
                            html.Div(
                                dbc.Button(
                                    [html.I(className="fas fa-plus mr-2"), " Aggiungi Input"],
                                    id="add-input",
                                    color="primary",
                                    className="action-btn"
                                ),
                                className="d-flex justify-content-center pt-1"
                            ),
                            # Sezione THEN (output)
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

                            html.Div(id="rules-list", children=[], style={"border": "1px solid #ccc", "minHeight": "100px", "padding": "10px", "marginTop": "20px", "backgroundColor": "#fff", "width": "80%", "maxWidth": "800px", "marginLeft": "auto", "marginRight": "auto"}),

                            html.Div(id="error-message", style={"color": "red", "fontWeight": "bold", "textAlign": "center", "marginTop": "10px"}),

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
                    ])
                ], className="main-card mx-auto")
            ]
        )
    ])