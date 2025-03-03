import requests

proxies = {
    "http": "socks5h://127.0.0.1:9150",  # Change to 9050 if needed
    "https": "socks5h://127.0.0.1:9150",
}

try:
    response = requests.get("http://check.torproject.org",
                            proxies=proxies, timeout=10)
    print(response.text)
except Exception as e:
    print(f"❌ Error: {e}")
