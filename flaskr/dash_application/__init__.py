import os

import dash
from dash import dcc, html
from flask import Flask
from .layout import serve_layout
from .pages import home, input, output, rules

def create_dash_application(flask_app):
    # Percorso assoluto indipendente dal sistema operativo
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_path = os.path.join(base_dir, 'flaskr', 'assets')
    
    dash_app = dash.Dash(
        server=flask_app,
        name="Dashboard",
        url_base_pathname="/",
        assets_folder=assets_path,
        assets_url_path="/assets"  # URL pubblico per gli assets
    )

    dash_app.layout = serve_layout()

    # Definiamo le pagine
    dash_app.config.suppress_callback_exceptions = True
    dash_app.callback(
        dash.Output("page-content", "children"),
        [dash.Input("url", "pathname")]
    )(lambda pathname: {
        "/input": input.layout(),
        "/output": output.layout(),
        "/rules": rules.layout(),
    }.get(pathname, home.layout()))  # Default: Homepage

    return dash_app
