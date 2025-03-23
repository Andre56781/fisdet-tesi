from dash import html, dcc
import dash_bootstrap_components as dbc
import requests
from ..callbacks import fetch_data, generate_variable_section, generate_rules_section

def layout():
    """Main function that generates the page layout."""
    # Fetch data from the backend
    data = fetch_data()

    # If data is not available, show an error message
    if not data:
        return html.Div("Error while loading data.", className="text-danger")

    terms = data.get("terms", {})
    rules = data.get("rules", [])

    # Generate layout sections
    input_children = generate_variable_section(terms.get("input", {}), "input")
    output_children = generate_variable_section(terms.get("output", {}), "output")
    rules_children = generate_rules_section(rules)

    return html.Div(
        className="container-fluid p-4",
        children=[
            dcc.Store(id='report-data-store', data=data),  # Store data in the Store
            dcc.Download(id="download-json"),
            dcc.Loading(
                id="export-loading",
                type="circle",
                children=[html.Div(id="export-loading-output")]
            ),
            
            html.Div(
                className="content",
                children=[
                    dbc.Card([
                        # Header with title
                        dbc.CardHeader(
                            [
                                html.H3("Fuzzy System Report", className="mb-0"),
                                dbc.Badge("Complete", color="success", className="ml-2")
                            ],
                            className="card-header-gradient d-flex justify-content-between align-items-center"
                        ),
                        
                        dbc.CardBody([
                            # Input/Output Section
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardHeader("Input Variables", className="gradient-header"),
                                        dbc.CardBody(input_children)
                                    ], className="shadow-sm")
                                ], md=6),
                                
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardHeader("Output Variables", className="gradient-header"),
                                        dbc.CardBody(output_children)
                                    ], className="shadow-sm")
                                ], md=6),
                            ], className="mb-4"),
                            
                            # Rules Section
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardHeader("Fuzzy Rules", className="gradient-header"),
                                        dbc.CardBody([
                                            html.Ul(rules_children, className="list-unstyled")
                                        ])
                                    ], className="shadow-sm")
                                ]),
                            ], className="mb-4"),
                        ]),
                        
                        # Footer
                        dbc.CardFooter(
                            html.Div(
                                className="d-flex justify-content-center w-100",
                                children=[
                                    dbc.ButtonGroup([
                                        dbc.Button(
                                            [html.I(className="fas fa-home mr-2"), "Back To Home"],
                                            color="light",
                                            className="nav-btn",
                                            href="/"
                                        ),
                                        dbc.Button(
                                            [
                                                html.I(className="fas fa-file-export mr-2"), 
                                                html.Span(
                                                    "Export JSON",
                                                    id="export-text",
                                                    style={"transition": "all 0.3s ease"}
                                                )
                                            ],
                                            color="success",
                                            className="nav-btn",
                                            id="btn-json-export",
                                            n_clicks=0,
                                            style={
                                                "marginLeft": "10px",
                                                "position": "relative",
                                                "overflow": "hidden"
                                            }
                                        )
                                    ])
                                ]
                            ),
                            className="card-footer-gradient"
                        )
                    ], className="main-card")
                ]
            )
        ]
    )