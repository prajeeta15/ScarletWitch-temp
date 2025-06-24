import logging

# Configure logging for alerts
logging.basicConfig(filename="threat_alerts.log",
                    level=logging.WARNING, format="%(asctime)s - %(message)s")


def send_alert(sentence, score):
    """Sends an alert if a high-risk threat is detected."""
    message = f"⚠️ ALERT: High-Risk Threat Detected! Sentence: {sentence} | Score: {score}"
    logging.warning(message)
    print(message)  # Can be replaced with SMS/Email integration
