from flask import Blueprint, jsonify

bp = Blueprint('sample', __name__)

@bp.route("/")
def index():
    return jsonify({"message": "Backend is running!"})
