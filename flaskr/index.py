from flask import Blueprint, render_template


# Crea il blueprint per la pagina di input
index_bp = Blueprint('index', __name__, url_prefix='/')

# Route per la pagina di input
@index_bp.route('/')
def index():
    return render_template('index.html')