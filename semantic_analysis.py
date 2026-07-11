"""
semantic_analysis.py
---------------------
Compares a user's spoken explanation against a reference concept definition
using Sentence-BERT embeddings and cosine similarity.
"""

import streamlit as st


@st.cache_resource(show_spinner=False)
def _load_sentence_model(model_name: str = "all-MiniLM-L6-v2"):
    """Load and cache the Sentence-BERT model."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def compute_semantic_similarity(user_text: str, reference_text: str) -> float:
    """
    Compute cosine similarity between the user's explanation and the
    reference concept definition using Sentence-BERT embeddings.

    Returns a float between 0.0 and 1.0.
    """
    if not user_text or not user_text.strip():
        return 0.0

    from sentence_transformers import util

    model = _load_sentence_model()
    embeddings = model.encode([user_text, reference_text], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()

    # Clamp to [0, 1] since cosine similarity of normalized sentence
    # embeddings can occasionally be slightly outside this range.
    return max(0.0, min(1.0, similarity))


def classify_understanding(similarity_score: float) -> str:
    """
    Map a semantic similarity score to a qualitative understanding label.
    """
    if similarity_score >= 0.75:
        return "Strong Understanding"
    elif similarity_score >= 0.50:
        return "Moderate Understanding"
    elif similarity_score >= 0.25:
        return "Weak Understanding"
    else:
        return "Poor Understanding"
