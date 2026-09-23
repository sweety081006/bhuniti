"""Document ingestion: extract text -> chunk -> embed -> index in Qdrant + Postgres."""

import io
import re

from sqlalchemy.orm import Session

from ..models import Document
from . import embeddings, vectorstore

CHUNK_CHARS = 900
OVERLAP = 150


def extract_pdf_text(raw: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(raw))
    pages = [(page.extract_text() or "") for page in reader.pages]
    text = "\n".join(pages).strip()
    if len(text) < 50:
        # Scanned PDF. Wire Tesseract here for OCR (PS: "OCR Integration").
        raise ValueError(
            "No selectable text found - this looks like a scanned PDF. "
            "OCR is not enabled in the MVP; upload a text PDF or paste the text."
        )
    return text


def chunk(text: str, size: int = CHUNK_CHARS, overlap: int = OVERLAP) -> list[str]:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    out, start = [], 0
    while start < len(text):
        end = min(len(text), start + size)
        # prefer to break on a sentence boundary
        if end < len(text):
            dot = text.rfind(". ", start + size // 2, end)
            if dot != -1:
                end = dot + 1
        piece = text[start:end].strip()
        if piece:
            out.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return out


def index_document(db: Session, doc: Document) -> int:
    """(Re)index one document that is already stored in Postgres. Returns chunk count."""
    chunks = chunk(doc.body)
    if not chunks:
        return 0

    vectors = embeddings.embed_passages(chunks)
    meta = {
        "title": doc.title,
        "doc_type": doc.doc_type,
        "publisher": doc.publisher,
        "year": doc.year,
        "state": doc.state,
        "url": doc.url,
        "provenance": doc.provenance,
    }
    vectorstore.delete_doc(doc.id)
    vectorstore.upsert_chunks(doc.id, meta, chunks, vectors)

    doc.n_chunks = len(chunks)
    db.add(doc)
    db.commit()
    return len(chunks)
