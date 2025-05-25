"""
Text embedding functionality for the hotel recommendation system.
"""
import numpy as np
from typing import Dict, List, Union
from sentence_transformers import SentenceTransformer

from config import VECTOR_CONFIG

# Initialize the embedding model (lazy loading)
_model = None


def get_embedding_model() -> SentenceTransformer:
    """
    Get the embedding model, loading it if necessary.

    Returns:
        SentenceTransformer: The sentence transformer model
    """
    global _model

    if _model is None:
        model_name = VECTOR_CONFIG["embedding_model"]
        _model = SentenceTransformer(model_name)

    return _model


def embed_text(text: str) -> np.ndarray:
    """
    Embed a text string using the sentence transformer model.

    Args:
        text: The text to embed

    Returns:
        np.ndarray: The embedding vector
    """
    model = get_embedding_model()

    # Generate embedding
    embedding = model.encode(text, normalize_embeddings=True)

    return embedding


def embed_batch(texts: List[str]) -> np.ndarray:
    """
    Embed a batch of text strings.

    Args:
        texts: List of text strings to embed

    Returns:
        np.ndarray: Matrix of embedding vectors
    """
    model = get_embedding_model()

    # Generate embeddings
    embeddings = model.encode(texts, normalize_embeddings=True)

    return embeddings


def similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two embeddings.

    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector

    Returns:
        float: Cosine similarity (-1 to 1, higher is more similar)
    """
    # Calculate cosine similarity
    similarity = np.dot(embedding1, embedding2)

    return float(similarity)
