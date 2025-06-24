# backend/ai_model/lda_model.py

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

# Load on startup
vectorizer = CountVectorizer(stop_words='english', max_df=0.9, min_df=2)
lda_model = LatentDirichletAllocation(n_components=5, random_state=42)


def train_lda(text_samples):
    """Train LDA model if needed"""
    X = vectorizer.fit_transform(text_samples)
    lda_model.fit(X)


def detect_topic(text):
    """Detect most probable topic for a new text"""
    X = vectorizer.transform([text])
    topic_distribution = lda_model.transform(X)
    top_topic = topic_distribution.argmax()
    return f"Topic_{top_topic}"
