import torch
import random
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

# Define model directory (Ensure this path is correct)
MODEL_DIR = os.path.abspath(
    "C:/Users/Prajeeta/Documents/GitHub/dark-web-intelligence/bert_darkweb_model")

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()  # Set model to evaluation mode


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
