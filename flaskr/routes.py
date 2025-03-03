from flask import Blueprint, request, jsonify, send_file
import os
from flaskr.file_handler import save_data, load_data, get_user_file

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.route("/save", methods=["POST"])
def save():
    data = request.json
    save_data(data)
    return jsonify({"status": "success"})

@bp.route("/load", methods=["GET"])
def load():
    data = load_data()
    return jsonify(data)

@bp.route("/export", methods=["GET"])
def export():
    user_file = get_user_file()
    if os.path.exists(user_file):
        return send_file(user_file, as_attachment=True, download_name="data.json")
    return jsonify({"error": "No data found"}), 404
