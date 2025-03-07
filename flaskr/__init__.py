import os
from flask import Flask
from flaskr.dash_application import create_dash_application
from dotenv import load_dotenv
from . import routes  # Importa il blueprint delle API

# Carica variabili d'ambiente dal file .env
load_dotenv()

def create_app(test_config=None):
    # Crea l'app Flask
    app = Flask(__name__, instance_relative_config=True)

    # Configurazione dell'app Flask
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)  # Carica config.py se disponibile
    else:
        app.config.from_mapping(test_config)

    # Assicura che la cartella 'instance' esista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Registra il Blueprint delle API
    app.register_blueprint(routes.bp, url_prefix='/api')

    # Crea e registra l'app Dash
    create_dash_application(app)

    return app
