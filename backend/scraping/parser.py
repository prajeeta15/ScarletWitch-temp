import re
from bs4 import BeautifulSoup


def clean_text(html):
    """Extracts and cleans text from an HTML page."""
    soup = BeautifulSoup(html, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text(separator=" ")
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text.lower().strip()
