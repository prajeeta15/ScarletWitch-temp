import requests
from stem.control import Controller
from stem import Signal
from bs4 import BeautifulSoup
import re


def get_tor_session():
    """Creates a session routed through the Tor network."""
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9150',
        'https': 'socks5h://127.0.0.1:9150'
    }
    return session


def renew_tor_ip():
    """Renews Tor IP address using the Tor control port."""
    try:
        with Controller.from_port(port=9051) as controller:
            controller.signal(Signal.NEWNYM)
            print("✅ Tor IP renewed!")
    except Exception as e:
        print(f"❌ Error renewing Tor IP: {e}")


def clean_text(html_content):
    """Cleans raw HTML content and extracts readable text."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove scripts and styles
    for script in soup(["script", "style"]):
        script.decompose()

    text = soup.get_text()
    text = re.sub(r"\s+", " ", text).strip()
    return text


session = get_tor_session()
response = session.get("http://check.torproject.org")
text = clean_text(response.text)
print(f"📝 Cleaned Text Preview: {text[:500]}")
