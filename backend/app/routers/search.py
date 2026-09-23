from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..services import embeddings, llm, rag, vectorstore

router = APIRouter(prefix="/api/search", tags=["ai-search"])


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    k: int = 6
    doc_type: str | None = None


@router.post("/ask")
def ask(req: AskRequest):
    """AI-powered search with mandatory citations + Evidence Score (PS points 8 & 14)."""
    return rag.answer(req.question, k=req.k, doc_type=req.doc_type)


@router.get("/semantic")
def semantic(q: str, k: int = 8, doc_type: str | None = None):
    """Raw semantic retrieval - no generation. Useful to show what the AI actually saw."""
    hits = vectorstore.search(embeddings.embed_query(q), limit=k, doc_type=doc_type)
    return [
        {
            "doc_id": h.get("doc_id"), "title": h.get("title"), "publisher": h.get("publisher"),
            "year": h.get("year"), "url": h.get("url"), "provenance": h.get("provenance"),
            "score": round(h.get("score", 0.0), 3),
            "snippet": " ".join(h.get("text", "").split())[:350],
        }
        for h in hits
    ]


@router.get("/status")
def status():
    return {
        "indexed_chunks": vectorstore.count(),
        "llm_available": llm.is_available(),
        "llm_models": llm.installed_models(),
    }
