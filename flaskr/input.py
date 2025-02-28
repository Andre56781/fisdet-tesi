from flask import Blueprint, render_template


# Crea il blueprint per la pagina di input
input_bp = Blueprint('input', __name__, url_prefix='/input')

# Route per la pagina di input
@input_bp.route('/')
def input():
    return render_template('input.html')