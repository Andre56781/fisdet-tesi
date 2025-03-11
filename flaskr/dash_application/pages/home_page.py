from dash import html, dcc
import dash_bootstrap_components as dbc

def layout() -> html.Div:
    return html.Div(
        id="home-page",
        className="vh-100",
        children=[
            html.Div(
                className="container h-100 d-flex flex-column justify-content-center",
                style={"position": "relative", "zIndex": 1},
                children=[
                    html.Div(
                        className="text-center animate__animated animate__fadeIn",
                        children=[
                            html.H1(
                                "FUZZY INFERENCE SYSTEM",
                                className="display-3 mb-4",  
                                style={
                                    "color": "#2c3e50",
                                    "fontWeight": "700", 
                                    "letterSpacing": "-0.05em",  
                                    "fontSize": "calc(2rem + 1.5vw)",  
                                    "lineHeight": "1.2"  
                                }
                            ),
                            html.P(
                                [
                                    "Benvenuto nel mondo dell'intelligenza fuzzy! ",
                                    html.Br(),
                                    html.Span(
                                        "Crea, importa e ottimizza i tuoi sistemi di inferenza.",
                                        style={
                                            "color": "#6c757d", 
                                            "fontSize": "1.25rem",  
                                            "fontWeight": "400",  
                                            "lineHeight": "1.8"  
                                        }
                                    )
                                ],
                                style={
                                    "fontSize": "1.3rem",
                                    "letterSpacing": "0.03em",
                                    "marginBottom": "2rem"
                                },
                                className="mb-5"  
                            ),
                            
                            # Pulsanti
                            html.Div(
                                className="d-flex flex-column flex-md-row justify-content-center gap-4",
                                children=[
                                    dcc.Link(
                                        dbc.Button(
                                            [
                                                html.I(className="fas fa-plus-circle me-2"),
                                                html.Span(
                                                    "Crea Nuovo FIS",
                                                    style={
                                                        "fontSize": "1.2rem",  
                                                        "letterSpacing": "0.03em" 
                                                    }
                                                )
                                            ],
                                            color="primary",
                                            className="fw-bold py-3 px-5 rounded-pill",
                                            style={
                                                "transition": "all 0.3s ease",
                                                "background": "linear-gradient(45deg, #4a90e2, #6c5ce7)",
                                                "border": "none",
                                                "boxShadow": "0 4px 6px rgba(0,0,0,0.1)" 
                                            }
                                        ),
                                        href="/input",
                                        id="home-to-input-link"
                                    ),
                                    dcc.Link(
                                        dbc.Button(
                                            [
                                                html.I(className="fas fa-file-import me-2"),
                                                html.Span(
                                                    "Importa FIS",
                                                    style={
                                                        "fontSize": "1.2rem",
                                                        "letterSpacing": "0.03em"
                                                    }
                                                )
                                            ],
                                            color="secondary",
                                            className="fw-bold py-3 px-5 rounded-pill",
                                            style={
                                                "transition": "all 0.3s ease",
                                                "background": "linear-gradient(45deg, #00b894, #55efc4)",
                                                "border": "none",
                                                "boxShadow": "0 4px 6px rgba(0,0,0,0.1)"
                                            }
                                        ),
                                        href="/import",
                                        id="home-to-import-link"
                                    ),
                                ]
                            )
                        ]
                    )
                ]
            ),
        ]
    )