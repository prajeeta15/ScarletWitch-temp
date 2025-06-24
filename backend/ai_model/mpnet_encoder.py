from sentence_transformers import SentenceTransformer
import torch

# Load once
mpnet_model = SentenceTransformer('all-mpnet-base-v2')


def mpnet_encode(texts):
    """
    Returns averaged MPNet embeddings (768-dim).
    """
    embeddings = mpnet_model.encode(
        texts, convert_to_tensor=True, normalize_embeddings=True)
    return embeddings  # shape: (batch_size, 768)
