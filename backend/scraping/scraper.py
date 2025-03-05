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

# Fix Python import path issue
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BACKEND_PATH)
PREDICTIONS_FILE = os.path.join(BACKEND_PATH, "predictions.json")

# Constants
SCRAPED_DATA_FILE = os.path.join(BACKEND_PATH, "scraped_data.json")
GRAPH_FILE = os.path.abspath("threat_trend.png")

try:
    from ai_model.model import predict_threat_level
except ModuleNotFoundError as e:
    print(f"❌ Module Import Error: {e}")
    print("🔍 Check if ai_model.model exists in backend/")
    sys.exit(1)  # Exit if imports fail


def get_tor_session():
    """Creates a session routed through the Tor network."""
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9150',
        'https': 'socks5h://127.0.0.1:9150'
    }
    return session


def clean_text(html_content):
    """Extracts readable text from raw HTML."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove scripts, styles, and other non-text elements
    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.extract()

    text = soup.get_text()
    text = re.sub(r"\s+", " ", text).strip()

    return text


def scrape_page(url):
    """Scrapes a dark web page and predicts its threat level."""
    print(f"🌍 Scraping: {url}")  # Debug log
    session = get_tor_session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = session.get(url, headers=headers, timeout=30)
        print(f"🔍 Response Status: {response.status_code}")  # Debugging

        if response.status_code == 200:
            text = clean_text(response.text)
            print(f"📝 Cleaned Text Sample: {text[:500]}")

            if len(text) < 50:
                print("⚠️ Extracted text is too short, skipping...")
                return None  # Skip if text is too short

            score = predict_threat_level(text)
            print(f"✅ Scraped {len(text)} characters. Threat Score: {score}")

            return {
                "url": url,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "text": text[:500],
                "score": score
            }
        else:
            print(f"❌ Failed to fetch {url} (Status: {response.status_code})")
            return None
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None


def save_scraped_data(entry):
    """Saves scraped data incrementally to prevent loss."""
    existing_data = []

    # Load existing data if the file exists
    if os.path.exists(SCRAPED_DATA_FILE):
        try:
            with open(SCRAPED_DATA_FILE, "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        except json.JSONDecodeError:
            print("⚠️ JSON file is corrupted. Creating a new one.")

    existing_data.append(entry)

    # Save updated data back to file
    with open(SCRAPED_DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, indent=4)

    print(f"📁 Saved entry to {SCRAPED_DATA_FILE}")


def save_predictions(predictions):
    """Save predictions to a JSON file."""
    with open(PREDICTIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(predictions, file, indent=4)


def generate_graph():
    """Generate a threat trend graph from scraped_data.json."""
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
    df.sort_values("timestamp", inplace=True)

    df["score"] = pd.to_numeric(df["score"], errors='coerce')

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

    os.makedirs(os.path.dirname(GRAPH_FILE), exist_ok=True)
    plt.savefig(GRAPH_FILE)
    print(f"📊 Threat trend graph updated: {GRAPH_FILE}")
    plt.close()


def start_scraping():
    """Continuously scrapes dark web pages and updates data in real-time."""
    target_urls = [
        "abacus23ucanifgq7uyqevbiufvace7ibhjtmp6svffvdfdink7z6lad.onion",
        "abacus23ucanifgq7uyqevbiufvace7ibhjtmp6svffvdfdink7z6lad.onion",
        "abacuszbjvzqxbqfn57q6rcb26kqtw4x4r7ysbz2tklln4khpydvlaqd.onion",
        "http://styxmarket.com/",
        "https://access-bidencash.com/",
        "https://russiamarket.to/",
        "https://bclubs.com/",
        "https://vicecity-market.io/",
        "https://wethenorth-marketplace.io/",
        "https://wethenorth-market-2.com/",
        "https://official.wethenorthmarket.net",
        "https://official.wethenorth-darknet.net",
        "https://vicecity.pw/",
        "https://russiamarket.com/",
        "https://market-abacus.org/",
        "https://www.abacus-market.io/index.html",
        "https://vicecitymarket.org/"
    ]

    while True:
        for url in target_urls:
            entry = scrape_page(url)
            if entry:
                save_scraped_data(entry)
        generate_graph()

        print("🔄 Waiting for next scrape cycle...")
        time.sleep(60)  # Scrape every 60 seconds


if __name__ == "__main__":
    print("🚀 Starting scraper...")
    start_scraping()
