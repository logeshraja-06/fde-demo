"""
services/embedding_service.py
------------------------------
The Embedding Service for Phase 3.

WHAT IS AN EMBEDDING?
---------------------
An embedding is a way of converting human language into a list of numbers
(called a vector) that computers can compare mathematically.

For example, the text:
  "Employees are entitled to 12 casual leaves"
might become a vector of 384 numbers:
  [0.024, -0.051, 0.129, ..., -0.082]

WHY CONVERT TEXT TO NUMBERS?
----------------------------
Computers cannot directly understand meaning or synonyms. But in vector space,
sentences with similar meanings end up close together geometrically.

For example:
  "How many casual leaves can I take?"
  "Employees get 12 days of casual leave"
These two sentences use different words, but their embedding vectors will point
in almost the same direction!

WHAT MODEL ARE WE USING?
------------------------
We use `sentence-transformers/all-MiniLM-L6-v2`:
- Free, open-source, and runs 100% locally on your machine.
- 384-dimensional vector output.
- Fast and lightweight (~80MB model size).
- Zero external API keys or cloud costs required.
"""

from typing import List
import threading

# Lazy-loaded singleton model to avoid reloading on every request
_model_instance = None
_model_lock = threading.Lock()
MODEL_NAME = "all-MiniLM-L6-v2"


def get_model():
    """
    Load and return the SentenceTransformer model singleton.
    Lazy-loads on first call to keep startup fast.
    """
    global _model_instance
    if _model_instance is None:
        with _model_lock:
            if _model_instance is None:
                from sentence_transformers import SentenceTransformer
                # Load model onto CPU
                _model_instance = SentenceTransformer(MODEL_NAME)
    return _model_instance


def get_embedding(text: str) -> List[float]:
    """
    Generate a 384-dimensional vector embedding for a single string of text.

    Args:
        text: The input query or chunk text.

    Returns:
        A list of floats representing the embedding vector.
    """
    if not text or not text.strip():
        raise ValueError("Cannot generate embedding for empty text.")

    model = get_model()
    # encode returns numpy ndarray or tensor, convert to standard Python float list
    vector = model.encode(text.strip(), convert_to_numpy=True, normalize_embeddings=True)
    return vector.tolist()


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embedding vectors for a batch of text strings efficiently.

    Args:
        texts: A list of text chunks.

    Returns:
        A list of embedding vectors (one per input text).
    """
    if not texts:
        return []

    cleaned_texts = [t.strip() for t in texts if t and t.strip()]
    if not cleaned_texts:
        return []

    model = get_model()
    vectors = model.encode(cleaned_texts, batch_size=32, convert_to_numpy=True, normalize_embeddings=True)
    return vectors.tolist()


def get_model_info() -> dict:
    """Return metadata about the current embedding model."""
    return {
        "model_name": MODEL_NAME,
        "dimensions": 384,
        "is_local": True,
        "provider": "sentence-transformers",
    }
