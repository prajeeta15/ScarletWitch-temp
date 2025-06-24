import requests
import stem.process
from stem.control import Controller


def start_tor():
    """Starts Tor and establishes a new identity."""
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="your_password")
        controller.signal(stem.Signal.NEWNYM)


def get_tor_session():
    """Returns a session routed through Tor."""
    session = requests.Session()
    session.proxies = {"http": "socks5h://127.0.0.1:9050",
                       "https": "socks5h://127.0.0.1:9050"}
    return session
