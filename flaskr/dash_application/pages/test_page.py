from dash import dcc, html
import dash_bootstrap_components as dbc
from ..callbacks import fetch_data

def layout() -> html.Div:
    data = fetch_data()

    if not data:
        return html.Div("Error: no data, please add a Fuzzy set of inputs and outputs", className="text-danger")
    if "terms" not in data:
        return html.Div("Error: The key ‘terms’ is absent from the returned data.", className="text-danger")

    terms = data["terms"]
    inference_input_ids = [f"{var_name}-input" for var_name in terms.get("input", {})]

    input_controls = []
    for var_name, var_data in terms.get("input", {}).items():
        domain = var_data.get("domain")
        if not domain:
            continue
        domain_min, domain_max = domain
        input_controls.append(
            dbc.Col([
                dbc.Label(
                    f"{var_name} ({domain_min}-{domain_max})", 
                    html_for=f"{var_name}-input", 
                    className="mb-2 text-center",  
                    style={"width": "100%"}
                ),
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

    output_controls = []
    for idx, (var_name, var_data) in enumerate(terms.get("output", {}).items()):
        terms_list = var_data.get("terms", [])
        is_classification = terms_list and terms_list[0].get("function_type") == "Classification"

        output_controls.append(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        f"{'Classification Result' if is_classification else 'Result'}: {var_name}",
                        className=f"{'bg-info text-white' if is_classification else 'bg-primary text-white'} fw-medium py-2 text-center"
                    ),
                    dbc.CardBody([
                        html.H2(
                            "Classe" if is_classification else "0",
                            id={"type": "classification-output", "variable": var_name} if is_classification else {"type": "output", "variable": var_name},
                            className=f"card-text text-center {'text-info' if is_classification else 'text-primary'} mb-0",
                            style={"fontSize": "2.5rem"}
                        ),
                        html.H4(
                            id=f"winner-term-{var_name}",
                            className="text-center text-dark mt-3"
                        ) if is_classification else None
                    ])
                ], className="variable-card h-100 mx-auto"),
                md=6,
                className="pe-2" if idx % 2 == 0 else "ps-2"
            )
        )

    is_classification_global = any(
        terms_list and terms_list[0].get("function_type") == "Classification"
        for terms_list in (v.get("terms", []) for v in terms.get("output", {}).values())
    )

    return html.Div([
        dcc.Store(id='inference-data'),
        dcc.Store(id='rule-memberships', data={}),
        dcc.Store(id='is-classification', data=is_classification_global),
        dcc.Store(id="winner-term-store", data={}),
        dcc.Store(id="inference-input-ids", data=[f"{var}-input" for var in terms.get("input", {})]),

        html.Div(
            id="inference-content",
            className="content",
            style={"display": "block", "position": "relative"},
            children=[
                dbc.Row(
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader([
                                html.H4("Test Inference Fuzzy", className="card-title mb-0"),
                                dbc.Badge("Simulation", color="warning", className="ml-2")
                            ], className="card-header-gradient d-flex justify-content-between align-items-center"),
                            dbc.CardBody([
                                dbc.Form([
                                    html.Div(
                                        id="inference-inputs",
                                        children=[dbc.Row(input_controls, className="mb-4 g-3")]
                                    ),
                                    html.Div(
                                        dbc.Button([
                                            html.I(className="fas fa-calculator mr-2"), " Calculate Inference"
                                        ],
                                            id="start-inference",
                                            color="primary",
                                            className="action-btn",
                                            style={"width": "290px"}),
                                        className="d-flex justify-content-center mb-4"
                                    ),
                                    html.Div(
                                        dbc.Button([
                                            html.I(className="fas fa-chart-line mr-2"), " Visualize Plot"
                                        ],
                                            id="visualize-plot",
                                            color="success",
                                            className="action-btn",
                                            style={"width": "250px"}),
                                        className="d-flex justify-content-center mb-4"
                                    ),
                                    dbc.Modal(
                                        id="inference-plot-modal",
                                        is_open=False,
                                        size="xl",
                                        centered=True,
                                        children=[
                                            dbc.ModalHeader("Inference Result"),
                                            dbc.ModalBody(
                                                dcc.Graph(id="inference-plot")
                                            ),
                                            dbc.ModalFooter(
                                                dbc.Button("Close", id="close-inference-plot", color="secondary")
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        id="rule-membership-section",
                                        children=[
                                            html.H5(
                                                "Activation of Rules",
                                                className="mb-3 text-center",
                                                style={"color": "#2c3e50"}
                                            ),
                                            dbc.Row([
                                                dbc.Col(
                                                    html.Div(id="rules-list-membership", className="rule-membership-container"),
                                                    md=8,
                                                    className="mx-auto"
                                                )
                                            ], className="justify-content-center mb-4", style={"minHeight": "150px"}),
                                            dbc.Row([
                                                dbc.Col(
                                                    html.Div(id="membership-values", className="membership-values-container"),
                                                    md=8,
                                                    className="mx-auto"
                                                )
                                            ])
                                        ],
                                        style={
                                            "backgroundColor": "#f8f9fa", 
                                            "borderRadius": "10px", 
                                            "padding": "1.5rem", 
                                            "marginBottom": "2rem"
                                        }
                                    ),
                                    dbc.Row(output_controls, className="g-4 justify-content-center") 
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
