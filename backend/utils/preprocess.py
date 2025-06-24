import pandas as pd
import re

# Default dataset path
EXCEL_PATH = "C:/Users/Prajeeta/Documents/GitHub/dark-web-intelligence/backend/data/darkweb_dataset.xlsx"

# Load dataset from Excel


def load_illicit_words(excel_path=EXCEL_PATH):
    try:
        df = pd.read_excel(excel_path, sheet_name="Sheet1")
        word_pairs = {}

        for _, row in df.iterrows():
            activity = str(row["activity"]).strip(
            ).lower() if pd.notna(row["activity"]) else ""
            sub_activity = str(
                row["sub-activity"]).strip().lower() if pd.notna(row["sub-activity"]) else ""
            word_pairs[sub_activity] = activity

        return word_pairs
    except FileNotFoundError:
        print(f"Error: The file {excel_path} was not found.")
        return {}
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return {}

# Process scraped sentences


def compute_threat_score(sentence, word_pairs):
    words = sentence.lower().split()
    score = 0
    for i, word in enumerate(words):
        if word in word_pairs:
            prev_word = words[i - 1] if i > 0 else ""
            if word_pairs[word] == prev_word or word_pairs[word] == "":
                score += 1
    return score

# Classify text based on threat score


def classify_text(sentence, word_pairs):
    score = compute_threat_score(sentence, word_pairs)
    return {"score": score, "label": "Threat" if score >= 5 else "Normal"}


# Example Usage
if __name__ == "__main__":
    word_pairs = load_illicit_words()
    text = "This is a sample threat conversation"
    result = classify_text(text, word_pairs)
    print(result)
