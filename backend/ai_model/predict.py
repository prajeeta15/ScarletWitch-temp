import os
import json
import time
from datetime import datetime
from model import predict_threat_level

# Fix Python import path issue
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_FILE = os.path.join(BACKEND_PATH, "predictions.log")
SCRAPED_DATA_FILE = os.path.join(BACKEND_PATH, "scraped_data.json")


def log_prediction(url, text, score):
    """Logs AI predictions with timestamps in UTF-8 encoding to avoid errors."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "url": url,
        "text": text[:500],  # Store a sample of the text
        "score": score
    }

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(json.dumps(log_entry) + "\n")
        print(f"✅ Logged: {log_entry}")
    except Exception as e:
        print(f"❌ Log Writing Error: {e}")


def monitor_real_time_data():
    """Reads the scraped data and makes threat predictions."""
    if not os.path.exists(SCRAPED_DATA_FILE):
        print("⚠️ No scraped data found.")
        return

    try:
        with open(SCRAPED_DATA_FILE, "r", encoding="utf-8") as file:
            scraped_data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        return

    for entry in scraped_data:
        url = entry.get("url", "Unknown URL")
        text = entry.get("text", "")

        if text:
            score = predict_threat_level(text)  # Run prediction
            log_prediction(url, text, score)  # Log prediction

    print("✅ All predictions logged successfully.")


if __name__ == "__main__":
    print("🚀 Starting real-time threat monitoring...")
    while True:
        monitor_real_time_data()
        print("🔄 Waiting for next cycle...")
        time.sleep(60)  # Process new data every 60 seconds
