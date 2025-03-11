from flask import Flask
from flaskr.dash_application import create_dash_application
from flaskr import routes

# Crea l'app Flask
print("Creazione dell'app Flask...")
flask_app = Flask(__name__)

# Registra le route delle API
print("Registrazione delle route...")
flask_app.register_blueprint(routes.bp, url_prefix='/api')

# Crea l'app Dash, collegata all'app Flask
print("Creazione dell'app Dash...")
dash_app = create_dash_application(flask_app)

if __name__ == '__main__':
    print("Avvio del server Flask...")
    flask_app.run(debug=True, port=5000)
