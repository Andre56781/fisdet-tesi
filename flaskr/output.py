from flask import Blueprint, render_template


# Crea il blueprint per la pagina di input
output_bp = Blueprint('output', __name__, url_prefix='/output')

# Route per la pagina di input
@output_bp.route('/')
def output():
    return render_template('output.html')