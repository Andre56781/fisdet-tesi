import os

import dash
from dash import dcc, html
from flask import Flask
from .layout import serve_layout
from .pages import home, input, output, rules

def create_dash_application(flask_app):

    assets_path = os.path.join(os.path.dirname(__file__), "..", "assets")

    dash_app = dash.Dash(
        server=flask_app,
        name="Dashboard",
        url_base_pathname="/",
        assets_folder=assets_path,
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
