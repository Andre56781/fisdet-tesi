from dash import dcc, html
import dash_bootstrap_components as dbc

def layout() -> html.Div:
    return html.Div([
        dcc.Store(id='rules-data', data=[]),
        dcc.Store(id='variables-data', data={}),

        html.Div(
            id="main-content",
            className="content",
            style={"display": "block", "position": "relative"},
            children=[
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Creazione Regole", className="card-title"),
                        dbc.Badge("Regole Fuzzy", color="info", className="ml-2")
                    ], className="card-header-gradient d-flex justify-content-between align-items-center"),
                    
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("IF", html_for="if-dropdown", className="w-100 text-center mb-0"),
                                    dcc.Dropdown(
                                        id="if-dropdown",
                                        options=[],
                                        placeholder="Seleziona Variabile di Input",
                                        className="custom-dropdown mb-2",
                                        style={"width": "300px"}  
                                    ),
                                    dbc.Label("Termine", html_for="if-term-dropdown", className="w-100 text-center mb-0"),
                                    dcc.Dropdown(
                                        id="if-term-dropdown",
                                        options=[],
                                        placeholder="Seleziona Termine",
                                        className="custom-dropdown",
                                        style={"width": "300px"}  
                                    ),
                                ], md=6, className="d-flex flex-column align-items-center pe-2"),  
                                
                                dbc.Col([
                                    dbc.Label("THEN", html_for="then-dropdown", className="w-100 text-center mb-0"),
                                    dcc.Dropdown(
                                        id="then-dropdown",
                                        options=[],
                                        placeholder="Seleziona Variabile di Output",
                                        className="custom-dropdown mb-2",
                                        style={"width": "300px"}  
                                    ),
                                    dbc.Label("Termine", html_for="then-term-dropdown", className="w-100 text-center mb-0"),
                                    dcc.Dropdown(
                                        id="then-term-dropdown",
                                        options=[],
                                        placeholder="Seleziona Termine",
                                        className="custom-dropdown",
                                        style={"width": "300px"}  
                                    ),
                                ], md=6, className="d-flex flex-column align-items-center ps-2"),  
                            ], className="mb-3 g-3"),  
                            
                            html.Div(
                                dbc.Button(
                                    [html.I(className="fas fa-plus mr-2"), " Crea Regola"],
                                    id="create-rule",
                                    color="success",
                                    className="action-btn"
                                ),
                                className="d-flex justify-content-center pt-1"
                            ),
                            
                            html.Div(
                                id="rules-list",
                                children=[
                                    html.P(
                                        "IF (Variabile Input Is Termine) THEN (Variabile Output IS Termine)",
                                        className="rule-item text-muted fst-italic",
                                        style={"fontSize": "0.9em"}
                                    )
                                ],
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
                                dbc.Button(
                                    [html.I(className="fas fa-trash mr-2"), " Elimina Regola"],
                                    id="delete-rule",
                                    color="danger",
                                    className="action-btn"
                                ),
                                className="d-flex justify-content-center pt-3"
                            )
                        ])
                    ]),
                    
                    dbc.CardFooter(
                        html.Div([
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
                        ], className="d-flex justify-content-end")
                    )
                ], className="main-card mx-auto")
            ]
        )
    ])