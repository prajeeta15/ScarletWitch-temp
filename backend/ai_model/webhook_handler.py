from flask import Flask, request, jsonify
from predict import predict

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Receives real-time data from external sources (e.g., dark web feeds) and classifies it.
    """
    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Invalid request. 'text' field is required."}), 400

        text = data["text"]
        result = predict(text)  # Use the AI model for classification

        return jsonify({
            "original_text": text,
            "prediction": result["label"],
            "score": result["score"],
            "confidence": result["confidence"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5002)
