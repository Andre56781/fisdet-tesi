import os
import dash
from dash import dcc, html
from flask import Flask
from .layout import serve_layout
from .pages import home, input, output, rules

def create_dash_application(flask_app):
    # Percorso relativo affidabile per tutti i sistemi
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(base_dir, '..', 'assets')
    
    dash_app = dash.Dash(
        server=flask_app,
        name="Dashboard",
        url_base_pathname="/",
        assets_folder=assets_path,
        assets_url_path="/assets",
        serve_locally=True  # Importante per la portabilità
    )

    dash_app.layout = serve_layout()

    # Callback con gestione errori migliorata
    @dash_app.callback(
        dash.Output("page-content", "children"),
        dash.Input("url", "pathname")
    )
    def render_page_content(pathname):
        return {
            "/input": input.layout(),
            "/output": output.layout(),
            "/rules": rules.layout(),
        }.get(pathname, home.layout())

    return dash_app