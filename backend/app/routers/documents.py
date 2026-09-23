from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Document, User
from ..security import require_roles
from ..services import ingest

router = APIRouter(prefix="/api/documents", tags=["repository"])


@router.get("")
def list_documents(
    q: str | None = None,
    doc_type: str | None = None,
    state: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(Document)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Document.title.ilike(like), Document.publisher.ilike(like)))
    if doc_type:
        query = query.filter(Document.doc_type == doc_type)
    if state:
        query = query.filter(Document.state == state)
    rows = query.order_by(Document.year.desc().nullslast(), Document.id.desc()).limit(limit).all()
    return [
        {
            "id": d.id, "title": d.title, "doc_type": d.doc_type, "publisher": d.publisher,
            "year": d.year, "state": d.state, "url": d.url, "provenance": d.provenance,
            "n_chunks": d.n_chunks,
        }
        for d in rows
    ]


@router.get("/facets")
def facets(db: Session = Depends(get_db)):
    types = [r[0] for r in db.query(Document.doc_type).distinct().all()]
    states = [r[0] for r in db.query(Document.state).distinct().all()]
    return {"doc_types": sorted(types), "states": sorted(states),
            "total": db.query(Document).count()}


@router.get("/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    d = db.get(Document, doc_id)
    if not d:
        raise HTTPException(404, "Document not found")
    return {
        "id": d.id, "title": d.title, "doc_type": d.doc_type, "publisher": d.publisher,
        "year": d.year, "state": d.state, "url": d.url, "provenance": d.provenance,
        "body": d.body,
    }


@router.post("", status_code=201)
async def upload_document(
    title: str = Form(...),
    doc_type: str = Form("research"),
    publisher: str = Form(""),
    year: int | None = Form(None),
    state: str = Form("India"),
    url: str = Form(""),
    provenance: str = Form("official"),
    text: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("researcher", "legal", "official", "institution")),
):
    """Add a document to the repository. Accepts a text PDF or pasted text."""
    body = (text or "").strip()
    if file is not None:
        raw = await file.read()
        if file.filename.lower().endswith(".pdf"):
            try:
                body = ingest.extract_pdf_text(raw)
            except ValueError as exc:
                raise HTTPException(422, str(exc))
        else:
            body = raw.decode("utf-8", errors="ignore")

    if len(body) < 100:
        raise HTTPException(422, "Document body is too short to index (need ~100+ characters).")

    doc = Document(
        title=title, doc_type=doc_type, publisher=publisher, year=year, state=state,
        url=url, provenance=provenance, body=body,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    n = ingest.index_document(db, doc)
    return {"id": doc.id, "title": doc.title, "chunks_indexed": n,
            "uploaded_by": user.email if user else None}
