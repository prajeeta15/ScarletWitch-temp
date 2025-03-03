from flask import Blueprint, request, jsonify
from ai_model.predict import predict

api_bp = Blueprint("api", __name__)


@api_bp.route("/predict", methods=["POST"])
def predict_text():
    data = request.get_json()
    if "text" not in data:
        return jsonify({"error": "No text provided"}), 400
    result = predict(data["text"])
    return jsonify(result)
