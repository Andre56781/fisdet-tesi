import os
import dash
import dash_bootstrap_components as dbc
from flask import current_app
from .layout import serve_layout
from .router import register_routing

def create_dash_application(flask_app):
    # Configurazione percorsi
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(base_dir, '..', 'assets')

    dash_app = dash.Dash(
        server=flask_app,
        name="Dashboard",
        url_base_pathname="/",
        assets_folder=assets_path,
        assets_url_path="/assets",
        serve_locally=True,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
    )

    # Non accedere direttamente a current_app in modo errato, ma usa flask_app.config
    if flask_app.config['DEBUG']:  # Usa flask_app invece di current_app
        print("App in modalità debug.")

    dash_app.layout = serve_layout()

    register_routing(dash_app)
    
    # Registra i callback
    from . import callbacks
    callbacks.register_callbacks(dash_app)

    return dash_app
