"""Local multilingual embeddings - no API key, downloaded once from HuggingFace."""

from functools import lru_cache

from ..config import settings


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


# e5-family models expect these prefixes; harmless for other models.
def embed_passages(texts: list[str]) -> list[list[float]]:
    prefixed = [f"passage: {t}" for t in texts]
    return _model().encode(prefixed, normalize_embeddings=True).tolist()


def embed_query(text: str) -> list[float]:
    return _model().encode(f"query: {text}", normalize_embeddings=True).tolist()
