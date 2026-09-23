"use client";

import { useEffect, useRef, useState } from "react";

import CountUp from "../../components/CountUp";
import { post } from "../../lib/api";

const STEPS = [
  "Retrieving passages from the index",
  "Ranking by semantic similarity",
  "Scoring evidence & provenance",
  "Composing a cited answer",
];

function scoreClass(n) {
  if (n >= 70) return "ring";
  if (n >= 45) return "ring low";
  return "ring bad";
}

// Progressive reveal of the answer — makes the response feel generated live.
function useTypewriter(text) {
  const [shown, setShown] = useState("");
  const [done, setDone] = useState(true);
  const timer = useRef(null);

  useEffect(() => {
    clearInterval(timer.current);
    if (!text) {
      setShown("");
      setDone(true);
      return;
    }
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      setShown(text);
      setDone(true);
      return;
    }
    // always finish in ~1.4s regardless of answer length
    const step = Math.max(2, Math.ceil(text.length / 88));
    let i = 0;
    setShown("");
    setDone(false);
    timer.current = setInterval(() => {
      i += step;
      if (i >= text.length) {
        setShown(text);
        setDone(true);
        clearInterval(timer.current);
      } else {
        setShown(text.slice(0, i));
      }
    }, 16);
    return () => clearInterval(timer.current);
  }, [text]);

  const finish = () => {
    clearInterval(timer.current);
    setShown(text || "");
    setDone(true);
  };

  return { shown, done, finish };
}

// Highlights inline citation markers such as [2] inside the answer text.
function withCitations(text) {
  return text.split(/(\[\d+\])/g).map((part, i) =>
    /^\[\d+\]$/.test(part) ? (
      <mark className="cite" key={i}>
        {part}
      </mark>
    ) : (
      part
    )
  );
}

export default function Search() {
  const [q, setQ] = useState("");
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [step, setStep] = useState(0);
  const [err, setErr] = useState("");
  const [asked, setAsked] = useState("");
  const boxRef = useRef(null);

  const type = useTypewriter(res?.answer || "");

  // cycle the "thinking" pipeline while the request is in flight
  useEffect(() => {
    if (!busy) return;
    setStep(0);
    const t = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), 620);
    return () => clearInterval(t);
  }, [busy]);

  async function ask() {
    const text = q.trim();
    if (text.length < 3) return;
    setBusy(true);
    setErr("");
    setRes(null);
    setAsked(text);
    try {
      setRes(await post("/api/search/ask", { question: text, k: 4 }));
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  }

  const ev = res?.evidence;

  return (
    <>
      <div className="page-head">
        <span className="eyebrow">
          <span className="dot" /> Retrieval-augmented · on-premise
        </span>
        <h1 className="page-title">AI Search &amp; Cited Q&amp;A</h1>
        <p className="page-sub">
          Answers come only from indexed documents. Every claim is cited, and the Evidence Score
          shows how well the corpus actually supports the answer.
        </p>
      </div>

      <div className="ask-box reveal reveal-1">
        <label>Your question</label>
        <textarea
          ref={boxRef}
          rows={2}
          value={q}
          placeholder="Ask anything about land records, tenure, disputes, law or land policy…"
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              ask();
            }
          }}
        />
        <div className="ask-bar">
          <button onClick={ask} disabled={busy || q.trim().length < 3}>
            {busy ? "Searching…" : "Ask BhuNiti  ↵"}
          </button>
          {q && !busy && (
            <button
              className="chip"
              onClick={() => {
                setQ("");
                boxRef.current?.focus();
              }}
            >
              Clear
            </button>
          )}
          <div className="spacer" style={{ flex: 1 }} />
          <span className="ask-hint">
            <kbd>Enter</kbd> to ask · <kbd>Shift</kbd>+<kbd>Enter</kbd> for a new line
          </span>
        </div>
        {err && <p className="err">{err}</p>}
      </div>

      {busy && (
        <div className="grid c2" style={{ marginTop: 18, gridTemplateColumns: "1.25fr 1fr" }}>
          <div className="card">
            <div className="card-head">
              <h3>
                Working on it
                <span className="equalizer" style={{ marginLeft: 10 }}>
                  <i />
                  <i />
                  <i />
                  <i />
                </span>
              </h3>
            </div>
            <div className="pipeline">
              {STEPS.map((s, i) => (
                <div
                  key={s}
                  className={`pipe-step ${i === step ? "on" : ""} ${i < step ? "done" : ""}`}
                >
                  <span className="pipe-dot">{i < step ? "✓" : ""}</span>
                  {s}
                </div>
              ))}
            </div>
            <div style={{ marginTop: 18 }}>
              <div className="sk lg w70" />
              <div className="sk w90" />
              <div className="sk" />
              <div className="sk w45" />
            </div>
          </div>
          <div className="card">
            <h3>Sources</h3>
            {[0, 1, 2].map((i) => (
              <div key={i} style={{ marginBottom: 16 }}>
                <div className="sk lg w70" />
                <div className="sk w45" />
                <div className="sk" />
              </div>
            ))}
          </div>
        </div>
      )}

      {!busy && !res && !err && (
        <div className="card reveal reveal-2" style={{ marginTop: 18 }}>
          <div className="empty">
            <div className="ico">🔎</div>
            <h3>Ask a question to begin</h3>
            <p>
              BhuNiti searches the indexed corpus of land laws, judgments, survey reports and policy
              documents, then answers with numbered citations and a transparent Evidence Score.
            </p>
          </div>
        </div>
      )}

      {!busy && res && (
        <div className="grid c2" style={{ marginTop: 18, gridTemplateColumns: "1.25fr 1fr" }}>
          <div>
            <div className="hint" style={{ marginBottom: 8 }}>
              Answering: <strong style={{ color: "var(--ink)" }}>{asked}</strong>
            </div>

            <div className="answer" onClick={type.finish} title={type.done ? "" : "Click to reveal instantly"}>
              {withCitations(type.shown)}
              {!type.done && <span className="caret" />}
            </div>

            {ev && (
              <div className="evidence">
                <div className={scoreClass(ev.score)} style={{ "--p": ev.score }}>
                  <span className="v">
                    <CountUp value={ev.score} duration={1100} />
                  </span>
                </div>
                <div className="why" style={{ flex: 1 }}>
                  <strong>Evidence Score</strong>
                  <div style={{ display: "grid", gap: 6, margin: "8px 0 6px" }}>
                    {[
                      ["coverage", ev.coverage],
                      ["similarity", ev.similarity],
                      ["source quality", ev.quality],
                    ].map(([k, v]) => (
                      <div className="metric-row" key={k}>
                        <span>{k}</span>
                        <span className="meter">
                          {/* coverage / similarity / quality are all 0–1 */}
                          <i style={{ width: `${Math.max(0, Math.min(100, Number(v) * 100))}%` }} />
                        </span>
                        <b>{v}</b>
                      </div>
                    ))}
                  </div>
                  {ev.n_sources} distinct documents ·{" "}
                  {res.model
                    ? "generated on-premise — no data leaves the platform"
                    : "showing matching passages"}
                </div>
              </div>
            )}
          </div>

          <div>
            <div className="card-head">
              <h3>Sources the answer may cite</h3>
              <span className="badge">{res.sources.length}</span>
            </div>
            {res.sources.map((s, i) => (
              <div className="source" key={s.n} style={{ animationDelay: `${i * 90}ms` }}>
                <div className="t">
                  <span className="num">{s.n}</span>
                  <span>{s.title}</span>
                </div>
                <div className="m">
                  <span>
                    {s.publisher}
                    {s.year ? ` · ${s.year}` : ""}
                  </span>
                  <span className={`badge ${s.provenance}`}>{s.provenance}</span>
                  <span className="badge">similarity {s.score}</span>
                </div>
                <div className="s">{s.snippet}…</div>
                {s.url && (
                  <div style={{ marginTop: 8 }}>
                    <a href={s.url} target="_blank" rel="noreferrer">
                      open source ↗
                    </a>
                  </div>
                )}
              </div>
            ))}
            {res.sources.length === 0 && <p className="hint">Nothing relevant was retrieved.</p>}
          </div>
        </div>
      )}
    </>
  );
}
