import sys
import os
import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

# Fix Python import path issue
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BACKEND_PATH)  # Add backend/ to Python path

try:
    from ai_model.predict import predict_threat_level
    from stem.control import Controller
    from stem import Signal
except ModuleNotFoundError as e:
    print(f"❌ Module Import Error: {e}")
    print("🔍 Check if ai_model.predict exists in backend/")
    sys.exit(1)  # Exit if imports fail

# Constants
SCRAPED_DATA_FILE = os.path.join(BACKEND_PATH, "scraped_data.json")


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
            # Debug extracted text
            print(f"📝 Cleaned Text Sample: {text[:500]}")

            if len(text) < 50:  # If text is too short, retry with Selenium
                print("⚠️ Extracted text is too short, switching to Selenium...")
                text = scrape_with_selenium(url)

            score = predict_threat_level(text)  # Use AI model
            print(f"✅ Scraped {len(text)} characters. Threat Score: {score}")

            return {
                "url": url,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "text": text[:500],  # Store a sample of the text
                "score": score
            }
        else:
            return {"error": f"Failed to fetch {url} (Status: {response.status_code})"}
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return {"error": str(e)}


def scrape_with_selenium(url):
    """Uses Selenium with Tor to scrape JavaScript-rendered pages."""
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options

    options = Options()
    options.add_argument("--proxy-server=socks5h://127.0.0.1:9150")  # Use Tor
    options.headless = True  # Run in headless mode

    driver = webdriver.Firefox(options=options)
    try:
        driver.get(url)
        time.sleep(5)  # Wait for JavaScript to load
        text = clean_text(driver.page_source)
        print(f"📝 Selenium Extracted Text Sample: {text[:500]}")  # Debugging
    finally:
        driver.quit()

    return text


def update_scraped_data(new_entries):
    """Appends new scraped data to `scraped_data.json`."""
    if not os.path.exists(SCRAPED_DATA_FILE):
        existing_data = []
    else:
        try:
            with open(SCRAPED_DATA_FILE, "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        except json.JSONDecodeError:
            existing_data = []

    existing_data.extend(new_entries)

    with open(SCRAPED_DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, indent=4)

    print(f"✅ {len(new_entries)} new pages scraped and logged.")


def start_scraping():
    """Continuously scrapes dark web pages and updates data in real-time."""
    target_urls = [
        "http://abacussxzkjwuzmhyusuqlx3h56bsczl2yy2bxrgujvlfnoyf7mhicad.onion/",
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
        new_entries = []

        for url in target_urls:
            result = scrape_page(url)
            if "error" not in result:
                new_entries.append(result)

        if new_entries:
            update_scraped_data(new_entries)

        print("🔄 Waiting for next scrape cycle...")
        time.sleep(60)  # Scrape every 60 seconds


if __name__ == "__main__":
    print("🚀 Starting scraper...")
    start_scraping()
