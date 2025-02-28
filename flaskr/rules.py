from flask import Blueprint, render_template


# Crea il blueprint per la pagina di input
rules_bp = Blueprint('rules', __name__, url_prefix='/rules')

# Route per la pagina di input
@rules_bp.route('/')
def rules():
    return render_template('rules.html')