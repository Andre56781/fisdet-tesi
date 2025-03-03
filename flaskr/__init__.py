import os
from flask import Flask, jsonify, request
from flaskr.file_handler import save_data, load_data
from flaskr.dash_application import create_dash_application

def create_app(test_config=None):
    # Crea l'app Flask
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # Inizializza Dash come sottodominio di Flask
    create_dash_application(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Assicura che la cartella 'instance' esista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # API per il salvataggio e il recupero dei dati utente
    @app.route("/api/save", methods=["POST"])
    def save():
        """API per salvare i dati utente."""
        data = request.json
        save_data(data)
        return jsonify({"message": "Dati salvati con successo"}), 200

    @app.route("/api/load", methods=["GET"])
    def load():
        """API per caricare i dati utente."""
        data = load_data()
        return jsonify(data), 200

    return app
