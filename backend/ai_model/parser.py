import re
from bs4 import BeautifulSoup


def clean_text(html):
    """
    Extract and normalize text from raw HTML content.
    - Removes scripts, styles, iframes
    - Normalizes spacing and removes unwanted symbols
    - Converts to lowercase
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove unnecessary elements
    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()

    text = soup.get_text(separator=" ")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove non-alphanumerics (keep space)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)

    return text.lower().strip()
