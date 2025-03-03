def get_collections(db):
    """Returns references to database collections."""
    return {
        "scraped_data": db["scraped_data"],  # Stores raw Dark Web data
        "parsed_data": db["parsed_data"],  # Stores cleaned & structured data
        # Stores AI-generated threat analysis
        "ai_predictions": db["ai_predictions"],
        # Stores labeled data for model training
        "training_data": db["training_data"],
    }
