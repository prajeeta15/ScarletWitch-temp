import torch
import os
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Define model directory (Ensure this path is correct)
MODEL_DIR = os.path.abspath(
    "C:/Users/Prajeeta/Documents/GitHub/dark-web-intelligence/bert_darkweb_model")

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()  # Set model to evaluation mode


def predict_threat_level(text):
    """Predict threat score for given text."""
    inputs = tokenizer(text, padding="max_length",
                       truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    probabilities = F.softmax(logits, dim=1)  # Convert logits to probabilities

    # Probability of being malicious (Class 1)
    threat_prob = probabilities[0][1].item()

    # Scale scores: Normal (0-4), Malicious (5-10)
    score = (threat_prob * 5) + 5 if threat_prob > 0.5 else threat_prob * 4
    score = round(score, 2)  # Keep 2 decimal places for consistency

    print(
        f"🟢 Text: {text[:50]}... |  Threat Probability: {threat_prob:.2f} |  Score: {score}")
    return score
