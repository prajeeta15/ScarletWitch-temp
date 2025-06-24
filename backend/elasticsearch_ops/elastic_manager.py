# backend/elasticsearch_ops/elastic_manager.py

from elasticsearch import Elasticsearch, helpers
import os

# Connect to local Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Index Name
INDEX_NAME = "darkweb-threats"

# Index Mapping (only needs to be created once)


def create_index():
    if not es.indices.exists(index=INDEX_NAME):
        mapping = {
            "mappings": {
                "properties": {
                    "url": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "text": {"type": "text"},
                    "score": {"type": "float"},
                    "topic": {"type": "keyword"}
                }
            }
        }
        es.indices.create(index=INDEX_NAME, body=mapping)
        print(f"✅ Created index: {INDEX_NAME}")
    else:
        print(f"ℹ️ Index {INDEX_NAME} already exists.")

# Save a single document


def save_entry(entry):
    es.index(index=INDEX_NAME, document=entry)
    print(f"📥 Saved entry to Elasticsearch: {entry['url']}")
