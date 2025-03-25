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
                            html.H4(
                                [
                                    "Welcome to the World of Fuzzy Intelligence!",
                                    html.Br(),
                                    html.Span(
                                        "Create, import, optimize and test your Fuzzy Inference System.",
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
                            
                            # Contenitore pulsanti verticale
                            html.Div(
                                className="d-flex flex-column justify-content-center gap-4",
                                children=[
                                    # Pulsante Crea
                                    dcc.Link(
                                        dbc.Button(
                                            [
                                                html.I(className="fas fa-plus-circle me-2"),
                                                html.Span(
                                                    "Create Your FIS",
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

                                    # Gruppo Importa + testo (CORRETTO QUI)
                                    html.Div(
                                        className="d-flex flex-column align-items-center gap-2",
                                        children=[
                                            dcc.Upload(
                                                id='upload-fis',
                                                children=dbc.Button(
                                                    [
                                                        html.I(className="fas fa-file-import me-2"),
                                                        html.Span(
                                                            "Import your FIS",
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
                                                accept='.json',
                                                multiple=False
                                            ),
                                            # Testo trascinamento file
                                            html.Div(id="import-feedback", className="mt-3"),                         
                                            html.Span(
                                                "Drag and drop your file or click here to import your FIS",
                                                style={
                                                    "color": "#6c757d",
                                                    "fontSize": "0.9rem",
                                                    "fontStyle": "italic",
                                                    "maxWidth": "300px"
                                                }
                                            ),
                                            html.Span(
                                                "(Supported formats: .json)",
                                                style={
                                                    "color": "#6c757d",
                                                    "fontSize": "0.8rem",
                                                    "fontStyle": "italic"
                                                }
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )