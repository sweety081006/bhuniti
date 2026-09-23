"""Qdrant vector store: one point per document chunk."""

import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from ..config import settings

_client: QdrantClient | None = None


def client() -> QdrantClient:
    """Embedded mode (a local folder) when QDRANT_PATH is set, otherwise a server."""
    global _client
    if _client is None:
        if settings.qdrant_path:
            Path(settings.qdrant_path).mkdir(parents=True, exist_ok=True)
            _client = QdrantClient(path=settings.qdrant_path)
        else:
            _client = QdrantClient(url=settings.qdrant_url, timeout=30)
    return _client


def ensure_collection() -> None:
    c = client()
    existing = {col.name for col in c.get_collections().collections}
    if settings.qdrant_collection not in existing:
        c.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=qm.VectorParams(size=settings.embedding_dim, distance=qm.Distance.COSINE),
        )


def upsert_chunks(doc_id: int, meta: dict, chunks: list[str], vectors: list[list[float]]) -> None:
    ensure_collection()
    points = [
        qm.PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={**meta, "doc_id": doc_id, "chunk_index": i, "text": chunk},
        )
        for i, (chunk, vec) in enumerate(zip(chunks, vectors))
    ]
    client().upsert(collection_name=settings.qdrant_collection, points=points)


def delete_doc(doc_id: int) -> None:
    ensure_collection()
    client().delete(
        collection_name=settings.qdrant_collection,
        points_selector=qm.FilterSelector(
            filter=qm.Filter(must=[qm.FieldCondition(key="doc_id", match=qm.MatchValue(value=doc_id))])
        ),
    )


def search(vector: list[float], limit: int = 6, doc_type: str | None = None) -> list[dict]:
    ensure_collection()
    flt = None
    if doc_type:
        flt = qm.Filter(must=[qm.FieldCondition(key="doc_type", match=qm.MatchValue(value=doc_type))])
    hits = client().search(
        collection_name=settings.qdrant_collection,
        query_vector=vector,
        limit=limit,
        query_filter=flt,
        with_payload=True,
    )
    return [{"score": float(h.score), **(h.payload or {})} for h in hits]


def count() -> int:
    ensure_collection()
    return client().count(collection_name=settings.qdrant_collection, exact=True).count
