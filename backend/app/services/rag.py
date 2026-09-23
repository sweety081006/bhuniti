"""Retrieval-augmented answering with mandatory citations and an Evidence Score.

Design rule for the whole platform: the model may only answer from retrieved
passages, every claim carries a [n] citation, and if retrieval comes back empty
we refuse rather than guess.
"""

from . import embeddings, llm, vectorstore

SYSTEM = """You are BhuNiti, a research assistant for Indian land governance used by \
researchers and government policymakers.

Rules you must never break:
1. Answer ONLY from the numbered SOURCES given to you. Never use outside knowledge.
2. Put a citation like [1] or [2][3] after every factual sentence.
3. If the sources do not answer the question, reply exactly: \
"The indexed sources do not cover this question." and nothing else.
4. Be concise: 4-8 sentences, plain language, no preamble.
5. Never invent statistics, dates, scheme names or section numbers."""


def _prompt(question: str, hits: list[dict]) -> str:
    blocks = []
    for i, h in enumerate(hits, 1):
        blocks.append(
            f"[{i}] {h.get('title', 'Untitled')} "
            f"({h.get('publisher', '')} {h.get('year', '') or ''}, {h.get('provenance', '')})\n"
            f"{h.get('text', '')}"
        )
    sources = "\n\n".join(blocks)
    return f"SOURCES:\n{sources}\n\nQUESTION: {question}\n\nANSWER (with [n] citations):"


def evidence_score(hits: list[dict]) -> dict:
    """Explainable 0-100 confidence signal shown next to every AI answer.

    coverage   - did we find enough distinct documents?
    similarity - how close were the best passages to the question?
    quality    - what share of sources are official or peer-reviewed
                 (as opposed to synthetic demo data)?
    """
    if not hits:
        return {"score": 0, "coverage": 0.0, "similarity": 0.0, "quality": 0.0, "n_sources": 0}

    distinct_docs = len({h.get("doc_id") for h in hits})
    coverage = min(1.0, distinct_docs / 4)

    top = sorted((h.get("score", 0.0) for h in hits), reverse=True)[:3]
    similarity = max(0.0, min(1.0, sum(top) / len(top)))

    trusted = sum(1 for h in hits if h.get("provenance") in ("official", "peer_reviewed"))
    quality = trusted / len(hits)

    score = round(100 * (0.35 * coverage + 0.40 * similarity + 0.25 * quality))
    return {
        "score": score,
        "coverage": round(coverage, 2),
        "similarity": round(similarity, 2),
        "quality": round(quality, 2),
        "n_sources": distinct_docs,
    }


def _extractive_fallback(hits: list[dict]) -> str:
    """Used when Ollama is not running, so the demo never dies on stage."""
    lines = [
        "_Local LLM unavailable - showing the most relevant passages verbatim "
        "instead of a generated summary._",
        "",
    ]
    for i, h in enumerate(hits[:3], 1):
        snippet = " ".join(h.get("text", "").split())[:400]
        lines.append(f"[{i}] {snippet}...")
    return "\n\n".join(lines)


def answer(question: str, k: int = 6, doc_type: str | None = None) -> dict:
    vec = embeddings.embed_query(question)
    hits = vectorstore.search(vec, limit=k, doc_type=doc_type)

    sources = [
        {
            "n": i,
            "doc_id": h.get("doc_id"),
            "title": h.get("title"),
            "publisher": h.get("publisher"),
            "year": h.get("year"),
            "url": h.get("url"),
            "provenance": h.get("provenance"),
            "score": round(h.get("score", 0.0), 3),
            "snippet": " ".join(h.get("text", "").split())[:300],
        }
        for i, h in enumerate(hits, 1)
    ]

    if not hits:
        return {
            "answer": "The indexed sources do not cover this question.",
            "sources": [],
            "evidence": evidence_score([]),
            "model": None,
        }

    if llm.is_available():
        try:
            text = llm.chat(SYSTEM, _prompt(question, hits))
            model = None
            from ..config import settings

            model = settings.ollama_model
        except Exception as exc:  # noqa: BLE001 - demo robustness beats strictness here
            text = _extractive_fallback(hits) + f"\n\n_(LLM error: {exc})_"
            model = None
    else:
        text = _extractive_fallback(hits)
        model = None

    return {
        "answer": text,
        "sources": sources,
        "evidence": evidence_score(hits),
        "model": model,
    }
