from database.db_setup import get_db
from database.models import get_collections

db = get_db()
collections = get_collections(db)

# ---- Real-Time Scraping Data Operations ----


def save_scraped_data(data):
    """Stores raw scraped data in the database."""
    collections["scraped_data"].insert_one(data)
    print(f"[✓] Scraped data stored: {data['url']}")


def fetch_new_scraped_data():
    """Fetches newly scraped data for AI processing."""
    return list(collections["scraped_data"].find().sort("_id", -1).limit(10))


def save_parsed_data(data):
    """Stores cleaned and structured data."""
    collections["parsed_data"].insert_one(data)
    print("[✓] Parsed data stored.")


def fetch_parsed_data():
    """Retrieves parsed data for analysis."""
    return list(collections["parsed_data"].find().limit(10))

# ---- AI Training Data Operations ----


def save_training_data(data):
    """Stores labeled training samples."""
    collections["training_data"].insert_one(data)
    print("[✓] Training sample stored.")


def fetch_training_data():
    """Retrieves training samples for real-time learning."""
    return list(collections["training_data"].find().limit(100))


def save_prediction(data):
    """Stores AI-generated predictions."""
    collections["ai_predictions"].insert_one(data)
    print("[✓] Prediction stored.")


def fetch_recent_predictions():
    """Fetches recent AI threat analysis results."""
    return list(collections["ai_predictions"].find().sort("_id", -1).limit(10))
