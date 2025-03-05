import os
import dash
import dash_bootstrap_components as dbc
from flask import current_app
from .layout import serve_layout
from .router import register_routing

def create_dash_application(flask_app):
    # Configurazione percorsi assets
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(base_dir, '..', 'assets')
    
    # Inizializzazione app Dash
    dash_app = dash.Dash(
        server=flask_app,
        name="FISDeT Dashboard",
        url_base_pathname="/",
        assets_folder=assets_path,
        assets_url_path="/assets",
        serve_locally=True,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            dbc.icons.FONT_AWESOME,
            "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap"
        ],
        meta_tags=[
            {'name': 'viewport', 
             'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'}
        ]
    )

    # Configurazione debug
    dash_app.config.suppress_callback_exceptions = True
    if flask_app.config.get('DEBUG'):
        dash_app.enable_dev_tools(dev_tools_ui=True, dev_tools_props_check=True)

    # Imposta il layout
    dash_app.layout = serve_layout()

    # Registra routing e callback
    register_routing(dash_app)
    
    try:
        from . import callbacks  # Registrazione callback centralizzata
        callbacks.register_callbacks(dash_app)
    except ImportError as e:
        if flask_app.config.get('DEBUG'):
            print(f"Callback registration warning: {str(e)}")

    return dash_app