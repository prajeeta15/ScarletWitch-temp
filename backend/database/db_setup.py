from pymongo import MongoClient

# MongoDB connection URI
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "darkweb_intelligence"


def get_db():
    """Returns a database connection instance."""
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]


if __name__ == "__main__":
    db = get_db()
    print(f"[✓] Connected to MongoDB: {DB_NAME}")
