import time
import json
import pandas as pd
import torch
import random
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datetime import datetime
import os

# Load trained BERT model
MODEL_DIR = "./bert_darkweb_model"
LOG_FILE = "threat_alerts.log"
# Scraper should store real-time data here
SCRAPED_DATA_FILE = "./scraped_data.json"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()  # Set model to evaluation mode


def load_real_time_data(file_path=SCRAPED_DATA_FILE):
    """Load real-time scraped data from a JSON file."""
    if not os.path.exists(file_path):
        print(f"⚠️ {file_path} not found. Waiting for scraper...")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        # Expecting a list of {"text": "scraped message", "timestamp": "YYYY-MM-DD HH:MM:SS"}
        return data
    except Exception as e:
        print(f"❌ Error loading scraped data: {e}")
        return []


def predict_threat_level(text):
    """Predicts the threat level of a given text on a scale of 0-10."""
    inputs = tokenizer(text, padding="max_length",
                       truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    # 0 = Non-threat, 1 = Threat
    prediction = torch.argmax(logits, dim=1).item()

    # Map prediction to the new scale
    if prediction == 1:
        return random.randint(5, 10)  # Threat level: 5-10
    else:
        return random.randint(0, 4)   # Normal level: 0-4


def log_prediction(data, log_file=LOG_FILE):
    """Logs the predictions into the threat_alerts.log file."""
    with open(log_file, "a") as file:
        for entry in data:
            timestamp = entry["timestamp"]
            message = entry["text"]
            score = predict_threat_level(message)

            file.write(f"{timestamp} | {message} | {score}\n")

    print(f"✅ Logged {len(data)} new real-time threats.")


def monitor_real_time_data():
    """Continuously monitors the real-time scraped data and predicts threats."""
    print("🚀 Monitoring real-time data for threats...")
    last_processed_time = None

    while True:
        scraped_data = load_real_time_data()

        if scraped_data:
            # Convert timestamps to datetime objects
            for entry in scraped_data:
                entry["timestamp"] = datetime.strptime(
                    entry["timestamp"], "%Y-%m-%d %H:%M:%S")

            # Sort data by timestamp
            scraped_data.sort(key=lambda x: x["timestamp"])

            # Filter out previously processed data
            new_data = [
                entry for entry in scraped_data if not last_processed_time or entry["timestamp"] > last_processed_time]

            if new_data:
                # Update last processed timestamp
                last_processed_time = new_data[-1]["timestamp"]
                log_prediction(new_data)

        time.sleep(10)  # Check every 10 seconds


# Start real-time monitoring
if __name__ == "__main__":
    monitor_real_time_data()
