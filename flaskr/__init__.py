import os

from flask import Flask
from flaskr.index import index_bp
from flaskr.input import input_bp
from flaskr.output import output_bp
from flaskr.rules import rules_bp


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #Blueprints
    app.register_blueprint(index_bp)
    app.register_blueprint(input_bp)
    app.register_blueprint(output_bp)
    app.register_blueprint(rules_bp)
    


    return app