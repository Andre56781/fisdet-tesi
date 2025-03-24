from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from ..callbacks import fetch_data

def layout() -> html.Div:
    """Main function that generates the page layout."""
    # Fetch data from the backend
    data = fetch_data()

    # If data is not available, show an error message
    if not data:
        return html.Div("Error while loading data.", className="text-danger")

    terms = data.get("terms", {})
    
    # Genera dinamicamente gli input per le variabili
    input_controls = []
    for var_name, var_data in terms.get("input", {}).items():  
        domain_min, domain_max = var_data["domain"]
        input_controls.append(
            dbc.Col([
                dbc.Label(f"{var_name} ({domain_min}-{domain_max})", html_for=f"{var_name}-input", className="mb-2"),
                dbc.Input(
                    id=f"{var_name}-input",
                    type="number",
                    min=domain_min,
                    max=domain_max,
                    step=0.1 if (domain_max - domain_min) < 10 else 1,
                    className="input-field",
                    placeholder=f"{domain_min} - {domain_max}",
                    style={"width": "100%"}
                )
            ], md=4, className="pe-2")
        )

    # Genera dinamicamente gli output
    output_controls = []
    for var_name, var_data in terms.get("output", {}).items(): 
        output_controls.append(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        f"Risultato {var_name}",
                        className="bg-light fw-medium py-2"
                    ),
                    dbc.CardBody(
                        html.H2("0",  # Valore iniziale
                            id=f"{var_name}-output",
                            className="card-text text-center text-primary mb-0",
                            style={"fontSize": "2.5rem"}
                        )
                    )
                ], className="variable-card h-100"),
                md=6,
                className="pe-2" if len(output_controls) % 2 == 0 else "ps-2"
            )
        )

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
                                            dbc.Row(
                                                input_controls,
                                                className="mb-4 g-3"
                                            )
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
                                    
                                    # Sezione Rule Membership
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
                                            dbc.Row(
                                                output_controls,
                                                className="g-4"
                                            )
                                        ]
                                    )
                                ], style={"padding": "0 2rem"})
                            ])
                        ], className="main-card"),
                        width={"size": 10, "offset": 1},
                        className="py-4"
                    )
                )
            ]
        )
    ])
