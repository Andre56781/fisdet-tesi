from dash import html, dcc
import dash_bootstrap_components as dbc

def layout() -> html.Div:
    return html.Div(
        id="home-page",
        children=[
            html.Div(
                className="home-header",
                children=[
                    html.H1("FUZZY INFERENCES SYSTEM", style={"textAlign": "center", "marginTop": "2rem"}),
                    html.P(
                        [
                            "Benvenuto nel mondo dei sistemi FIS.",
                            html.Br(),
                            "Esplora, crea e importa il tuo sistema di inferenza Fuzzy!"
                        ],
                        style={"textAlign": "center", "fontSize": "1.25rem"}
                    )
                ],
                style={"marginBottom": "3rem"}
            ),
            html.Div(
                className="home-buttons",
                children=[
                    dcc.Link(
                        dbc.Button(
                            "Crea FIS", 
                            color="primary", 
                            size="md", 
                            className="me-2",
                            style={"padding": "1rem 2rem", "fontSize": "1.2rem"}
                        ),
                        href="/input",
                        id="home-to-input-link"
                    ),
                    dcc.Link(
                        dbc.Button(
                            "Importa FIS", 
                            color="secondary",
                            size="md",
                            style={"padding": "1rem 2rem", "fontSize": "1.2rem"}
                        ),
                        href="/import",
                        id="home-to-import-link"
                    ),
                ],
                style={"display": "flex", "justifyContent": "center"}
            )
        ]
    )
