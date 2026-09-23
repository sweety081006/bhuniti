# BhuNiti — SIH 2026, PS 26019

National Digital Platform for Research, Policy Innovation and Evidence-Based Land Governance
(Ministry of Rural Development, Department of Land Resources — PME Division).

**Pilot state: Bihar** — the statewide Special Survey & Settlement is running now, Bihar scores
low on record quality (NCAER N-LRSI), and its dispute load is among the heaviest.

Everything runs locally and free: **Ollama** for the LLM, **sentence-transformers** for
embeddings, open-source infrastructure in Docker. No paid API is used anywhere.

## Run it (Windows PowerShell)

```powershell
# 0. one-time: model for the local LLM (~4.7 GB)
ollama pull llama3.2:3b

# 1. infrastructure
copy .env.example .env          # paste your MapTiler / data.gov.in / Bhashini keys
docker compose up -d            # postgres+postgis, qdrant, minio

# 2. backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python -m backend.seed.seed     # users + corpus + synthetic Bihar parcels (first run downloads the embedding model, ~470 MB)
uvicorn backend.app.main:app --reload --port 8000

# 3. frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open <http://localhost:3000>. API docs at <http://localhost:8000/docs>.

The home page is the login page. Pick a role — Researcher, Legal Authority, Government
Official, Institution — and sign in (password `demo1234` for all); you land on AI Search.
Demo accounts: `researcher@`, `legal@`, `official@`, `institution@bhuniti.in`.

## What is built (MVP scope)

| Module | PS point | Status |
|---|---|---|
| Repository + upload & index | 7 | done (text PDF / pasted text) |
| AI search, cited Q&A, Evidence Score | 8, 14 | done |
| GIS Studio (parcels + Bhuvan WMS) | 10, 13 | done |
| Policy Sandbox (land consolidation) | 12 | done |
| Dashboards | 11, 16 | done |
| Role-based access | 17 | done (JWT; Keycloak is the production path) |
| REST APIs | 18 | done (`/docs`) |
| Collaborative workspaces | 9 | model only, no UI |
| Innovation portal | 15 | not in MVP |
| OCR for scanned PDFs | — | **stub only** — returns a clear "not supported" message. Tesseract drops in at `backend/app/services/ingest.py`. |

## Data honesty (say this to the jury)

- **Real:** ISRO Bhuvan LULC open WMS; every document URL; data.gov.in as the socio-economic source.
- **Synthetic:** parcel geometries, dispute counts, indicators. DILRMP / Bhunaksha / NJDG have no
  public bulk API, so these are labelled `source: "synthetic"` in the database and in the UI.
- **Seed corpus:** team-written summaries, each marked `[SEED SUMMARY …]` in its body. Upload the
  real PDFs via `POST /api/documents` to replace them — the Evidence Score rewards real
  `official` / `peer_reviewed` sources over stubs.

## Anti-hallucination design

The assistant answers only from retrieved passages, must cite `[n]` for every claim, and refuses
outright when retrieval returns nothing. The **Evidence Score** (0–100) is
`0.35 × coverage + 0.40 × similarity + 0.25 × source quality`, shown with its components next to
every answer. If Ollama is not running the app falls back to showing the retrieved passages
verbatim, so a demo never dies on stage.

## Layout

```
backend/app/routers/    auth, documents, search, gis, simulation, dashboard
backend/app/services/   embeddings, vectorstore, llm, rag, ingest, simulate
backend/seed/           seed.py + corpus.py
frontend/app/           /, /search, /map, /simulate, /dashboard
```
