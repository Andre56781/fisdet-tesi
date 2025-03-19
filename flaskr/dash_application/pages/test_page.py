from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

def layout() -> html.Div:
    return html.Div([
        dcc.Store(id='inference-data'),
        dcc.Store(id='rule-memberships', data={}),
        
        html.Div(
            id="inference-content",
            className="content",
            style={
                "display": "block",
                "position": "relative"
            },
            children=[
                dbc.Row(
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader(
                                [
                                    html.H4("Test Inferenza Fuzzy", className="card-title mb-0"),
                                    dbc.Badge("Simulazione", color="warning", className="ml-2")
                                ],
                                className="card-header-gradient d-flex justify-content-between align-items-center"
                            ),
                            
                            dbc.CardBody([
                                dbc.Form([
                                    # Sezione Input Variabili
                                    html.Div(
                                        id="inference-inputs",
                                        children=[
                                            dbc.Row([
                                                dbc.Col([
                                                    dbc.Label("Temperatura (°C)", html_for="temp-input", className="mb-2"),
                                                    dbc.Input(
                                                        id="temp-input",
                                                        type="number",
                                                        min=0,
                                                        max=50,
                                                        step=0.1,
                                                        className="input-field",
                                                        placeholder="0 - 50",
                                                        style={"width": "100%"}
                                                    )
                                                ], md=4, className="pe-2"),
                                                
                                                dbc.Col([
                                                    dbc.Label("Umidità (%)", html_for="humidity-input", className="mb-2"),
                                                    dbc.Input(
                                                        id="humidity-input",
                                                        type="number",
                                                        min=0,
                                                        max=100,
                                                        step=1,
                                                        className="input-field",
                                                        placeholder="0 - 100",
                                                        style={"width": "100%"}
                                                    )
                                                ], md=4, className="px-2"),
                                                
                                                dbc.Col([
                                                    dbc.Label("Pressione (hPa)", html_for="pressure-input", className="mb-2"),
                                                    dbc.Input(
                                                        id="pressure-input",
                                                        type="number",
                                                        min=900,
                                                        max=1100,
                                                        step=1,
                                                        className="input-field",
                                                        placeholder="900 - 1100",
                                                        style={"width": "100%"}
                                                    )
                                                ], md=4, className="ps-2"),
                                            ], className="mb-4 g-3")
                                        ]
                                    ),
                                    
                                    # Bottone Calcola
                                    html.Div(
                                        dbc.Button(
                                            [html.I(className="fas fa-calculator mr-2"), " Calcola Inferenza"],
                                            id="start-inference",
                                            color="primary",
                                            className="action-btn",
                                            style={"width": "300px"}
                                        ),
                                        className="d-flex justify-content-center mb-4"
                                    ),
                                    
                                    # Nuova Sezione Rule Membership
                                    html.Div(
                                        id="rule-membership-section",
                                        children=[
                                            html.H5("Rule Activation Strength", 
                                                    className="mb-3 text-center",
                                                    style={"color": "#2c3e50"}),
                                            dbc.Row([
                                                dbc.Col([
                                                    html.Div(
                                                        id="rules-list-membership",
                                                        className="rule-membership-container",
                                                        style={
                                                            "borderRight": "2px solid #eee",
                                                            "paddingRight": "1.5rem"
                                                        },
                                                    )
                                                ], md=6),
                                                
                                                dbc.Col([
                                                    html.Div(
                                                        id="membership-values",
                                                        className="membership-values-container",
                                                    )
                                                ], md=6)
                                            ], className="g-3 membership-section",
                                            style={"minHeight": "250px", "maxHeight": "400px", "overflowY": "auto"})
                                        ],
                                        style={
                                            "backgroundColor": "#f8f9fa",
                                            "borderRadius": "10px",
                                            "padding": "1.5rem",
                                            "marginBottom": "2rem"
                                        }
                                    ),
                                    
                                    # Sezione Risultati
                                    html.Div(
                                        id="inference-results",
                                        children=[
                                            dbc.Row([
                                                dbc.Col(
                                                    dbc.Card([
                                                        dbc.CardHeader(
                                                            "Risultato Velocità Ventola",
                                                            className="bg-light fw-medium py-2"
                                                        ),
                                                        dbc.CardBody(
                                                            html.H2("0 RPM", 
                                                                id="fan-speed-output",
                                                                className="card-text text-center text-primary mb-0",
                                                                style={"fontSize": "2.5rem"}
                                                            )
                                                        )
                                                    ], className="variable-card h-100"),
                                                    md=6,
                                                    className="pe-2"
                                                ),
                                                
                                                dbc.Col(
                                                    dbc.Card([
                                                        dbc.CardHeader(
                                                            "Risultato Potenza",
                                                            className="bg-light fw-medium py-2"
                                                        ),
                                                        dbc.CardBody(
                                                            html.H2("0 W", 
                                                                id="power-output",
                                                                className="card-text text-center text-primary mb-0",
                                                                style={"fontSize": "2.5rem"}
                                                            )
                                                        )
                                                    ], className="variable-card h-100"),
                                                    md=6,
                                                    className="ps-2"
                                                )
                                            ], className="g-4")
                                        ]
                                    )
                                ], style={"padding": "0 2rem"})
                            ]),
                            
                            dbc.CardFooter(
                                html.Div([
                                    dbc.Button(
                                        [html.I(className="fas fa-arrow-left mr-2"), "Indietro"],
                                        id="back-inference",
                                        color="light",
                                        className="nav-btn"
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-sync-alt mr-2"), "Reset"],
                                        id="reset-inference",
                                        color="warning",
                                        className="nav-btn"
                                    )
                                ], className="d-flex justify-content-end gap-3")
                            )
                        ], className="main-card"),
                        width={"size": 10, "offset": 1},
                        className="py-4"
                    )
                )
            ]
        )
    ])