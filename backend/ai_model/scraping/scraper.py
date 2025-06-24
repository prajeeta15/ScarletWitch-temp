from ..xlm_roberta_model import XLMRobertaMPNet
from transformers import XLMRobertaTokenizer
import torch
import os
import sys
import json
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from bs4 import BeautifulSoup
import re
from ..mpnet_encoder import mpnet_encode
from ..gpt_assist import gpt_refine_threat
from ..lda_model import detect_topic
from elasticsearch_ops.elastic_manager import save_entry, create_index
from ..rl_model import adjust_score


# Set up Python path first

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, PROJECT_ROOT)
BACKEND_PATH = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_PATH)

# Now import custom modules

try:
    tokenizer = XLMRobertaTokenizer.from_pretrained("xlm-roberta-base")
    model = XLMRobertaMPNet(num_labels=11)
    model.load_state_dict(torch.load(
        "./xlm_roberta_elmo_model/pytorch_model.bin", map_location=torch.device('cpu')))
    model.eval()
except Exception as e:
    print(f"❌ Model loading failed: {e}")
    sys.exit(1)

# Define paths
PREDICTIONS_FILE = os.path.join(BACKEND_PATH, "predictions.json")
TARGET_FILE = os.path.join(BACKEND_PATH, "scraping", "target_url.txt")
SCRAPED_DATA_FILE = os.path.join(BACKEND_PATH, "scraped_data.json")
GRAPH_FILE = os.path.join(BACKEND_PATH, "threat_trend.png")

# Tor setup


def get_tor_session():
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9150',
        'https': 'socks5h://127.0.0.1:9150'
    }
    return session


def clean_text(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.extract()
    text = soup.get_text()
    return re.sub(r"\s+", " ", text).strip()


def predict_threat_level(text):
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, padding=True)
    mpnet_vec = mpnet_encode([text])[0].unsqueeze(0)
    with torch.no_grad():
        outputs = model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            mpnet_emb=mpnet_vec
        )
        logits = outputs["logits"]
        return int(torch.argmax(logits, dim=1))


def scrape_page(url):
    session = get_tor_session()
    try:
        response = session.get(url, timeout=20)
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

    if response.status_code != 200:
        print(f"⚠️ {url} returned status code {response.status_code}")
        return None

    text = clean_text(response.text)
    if len(text) < 50:
        print("⚠️ Extracted text is too short, skipping...")
        return None

    print(f"📝 Cleaned Text Sample: {text[:300]}")

    try:
        score = predict_threat_level(text)
    except Exception as e:
        print(f"❌ Error during threat level prediction: {e}")
        return None

    topic = detect_topic(text)

    if score >= 6:
        try:
            score = gpt_refine_threat(text, score)
        except Exception as e:
            print(f"⚠️ GPT refinement failed: {e}")

    try:
        score = adjust_score(score, topic)
    except Exception as e:
        print(f"⚠️ RL adjustment failed: {e}")

    print(f"✅ Final Threat Score (GPT+RL): {score}, Topic: {topic}")

    return {
        "url": url,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": text[:500],
        "score": score,
        "topic": topic
    }


def save_scraped_data(entry):
    existing_data = []
    if os.path.exists(SCRAPED_DATA_FILE):
        try:
            with open(SCRAPED_DATA_FILE, "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        except json.JSONDecodeError:
            print("⚠️ JSON file is corrupted. Creating a new one.")
    existing_data.append(entry)
    with open(SCRAPED_DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, indent=4)
    print(f"📁 Saved entry to {SCRAPED_DATA_FILE}")


def save_predictions(predictions):
    with open(PREDICTIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(predictions, file, indent=4)


def generate_graph():
    if not os.path.exists(SCRAPED_DATA_FILE):
        print("⚠️ No scraped data found!")
        return

    try:
        with open(SCRAPED_DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print("❌ Error: Corrupted JSON file!")
        return

    if not data:
        print("⚠️ No data available for graph generation.")
        return

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    df.dropna(subset=["timestamp"], inplace=True)
    df["score"] = pd.to_numeric(df["score"], errors='coerce')
    df.sort_values("timestamp", inplace=True)

    if df.empty:
        print("⚠️ Not enough valid data to generate a graph.")
        return

    plt.figure(figsize=(12, 6))
    plt.plot(df["timestamp"], df["score"], marker="o",
             linestyle="-", color="red", label="Threat Score")
    plt.xlabel("Time")
    plt.ylabel("Threat Score")
    plt.title("Dark Web Threat Level Trend Over Time")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(GRAPH_FILE)
    print(f"📊 Threat trend graph updated: {GRAPH_FILE}")
    plt.close()


def load_target_urls():
    try:
        with open(TARGET_FILE, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"❌ Error: targets.txt not found at {TARGET_FILE}")
        return []
    except Exception as e:
        print(f"⚠️ Error loading URLs from file: {e}")
        return []


def start_scraping():
    create_index()
    target_urls = load_target_urls()

    if not target_urls:
        print("⚠️ No target URLs found. Please update `target_url.txt`.")
        return

    print(f"🚀 Starting scraping for {len(target_urls)} URLs...")

    while True:
        for url in target_urls:
            entry = scrape_page(url)
            if entry:
                save_scraped_data(entry)
                save_entry(entry)
        generate_graph()
        print("🔄 Waiting for next scrape cycle...")
        time.sleep(60)


if __name__ == "__main__":
    print("🚀 Starting scraper...")
    start_scraping()
