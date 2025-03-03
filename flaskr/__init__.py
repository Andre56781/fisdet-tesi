import os
from flask import Flask, jsonify, request, send_from_directory
from flaskr.file_handler import save_data, load_data
from flaskr.dash_application import create_dash_application
from dotenv import load_dotenv

# Carica variabili d'ambiente dal file .env
load_dotenv()

def create_app(test_config=None):
    # Crea l'app Flask
    app = Flask(__name__, instance_relative_config=True)

    # Configurazione dell'app Flask
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),  # Usa variabile d'ambiente per la chiave segreta
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        # STATIC_FOLDER=os.path.join(app.root_path, 'assets')  # Se necessario per file statici
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

    # Inizializza Dash come sottodominio di Flask
    create_dash_application(app)

    # API per il salvataggio e il recupero dei dati utente
    @app.route("/api/save", methods=["POST"])
    def save():
        """API per salvare i dati utente."""
        data = request.json
        try:
            save_data(data)  # Funzione per salvare i dati
            return jsonify({"message": "Dati salvati con successo"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/load", methods=["GET"])
    def load():
        """API per caricare i dati utente."""
        try:
            data = load_data()  # Funzione per caricare i dati
            return jsonify(data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Servire file statici (opzionale, se necessario)
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        return send_from_directory(os.path.join(app.root_path, 'assets'), filename)

    return app
