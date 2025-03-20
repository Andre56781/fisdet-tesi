from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
import json

def layout():
    return html.Div(
        className="container-fluid p-4",
        children=[
            dcc.Store(id='report-data-store'),
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
                        # Header con titolo
                        dbc.CardHeader(
                            [
                                html.H3("Report Sistema Fuzzy", className="mb-0"),
                                dbc.Badge("Completo", color="success", className="ml-2")
                            ],
                            className="card-header-gradient d-flex justify-content-between align-items-center"
                        ),
                        
                        dbc.CardBody([
                            # Sezione Input/Output
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardHeader("Variabili di Input", className="gradient-header"),
                                        dbc.CardBody([
                                            html.Div(
                                                className="variable-card mb-3 p-3",
                                                children=[
                                                    html.H5("Temperatura", className="text-primary mb-2"),
                                                    dbc.Row([
                                                        dbc.Col("Dominio: 0-100 °C", width=6),
                                                        dbc.Col("Tipo: Input", width=6),
                                                    ]),
                                                    html.Div(
                                                        className="mt-2",
                                                        children=[
                                                            html.Small("Funzioni di Appartenenza:", className="text-muted"),
                                                            html.Div([
                                                                dbc.Badge("Freddo", color="info", className="me-1"),
                                                                dbc.Badge("Caldo", className="me-1", style={"background": "#52b2cf"}),
                                                                dbc.Badge("Bollente", color="danger")
                                                            ], className="mt-1")
                                                        ]
                                                    )
                                                ]
                                            ),
                                        ])
                                    ], className="shadow-sm")
                                ], md=6),
                                
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardHeader("Variabili di Output", className="gradient-header"),
                                        dbc.CardBody([
                                            html.Div(
                                                className="variable-card mb-3 p-3",
                                                children=[
                                                    html.H5("Potenza Riscaldamento", className="text-success mb-2"),
                                                    dbc.Row([
                                                        dbc.Col("Dominio: 0-100%", width=6),
                                                        dbc.Col("Tipo: Output", width=6),
                                                    ]),
                                                    html.Div(
                                                        className="mt-2",
                                                        children=[
                                                            html.Small("Funzioni di Appartenenza:", className="text-muted"),
                                                            html.Div([
                                                                dbc.Badge("Basso", color="secondary", className="me-1"),
                                                                dbc.Badge("Medio", className="me-1", style={"background": "#3a8ba3"}),
                                                                dbc.Badge("Alto", color="success")
                                                            ], className="mt-1")
                                                        ]
                                                    )
                                                ]
                                            ),
                                        ])
                                    ], className="shadow-sm")
                                ], md=6),
                            ], className="mb-4"),
                            
                            # Sezione Regole
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardHeader("Regole Fuzzy", className="gradient-header"),
                                        dbc.CardBody([
                                            html.Ul([
                                                html.Li(
                                                    "IF Temperatura IS Freddo AND Pressione IS Bassa THEN Potenza IS Alta",
                                                    className="rule-item mb-2 p-2"
                                                ),
                                                html.Li(
                                                    "IF Temperatura IS Caldo AND Pressione IS Media THEN Potenza IS Media",
                                                    className="rule-item mb-2 p-2"
                                                ),
                                                html.Li(
                                                    "IF Temperatura IS Bollente AND Pressione IS Alta THEN Potenza IS Bassa",
                                                    className="rule-item mb-2 p-2"
                                                ),
                                            ], className="list-unstyled")
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
                                            [html.I(className="fas fa-home mr-2"), "Torna alla Home Page"],
                                            color="light",
                                            className="nav-btn",
                                            href="/home"
                                        ),
                                        dbc.Button(
                                            [
                                                html.I(className="fas fa-file-export mr-2"), 
                                                html.Span(
                                                    "Esporta JSON",
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