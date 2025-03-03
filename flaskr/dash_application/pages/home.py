from dash import html

def layout() -> html.Div:
    return html.Div([
        html.H1("Homepage"),
        html.P("Benvenuto nel sistema di acquisizione dati."),
    ])
