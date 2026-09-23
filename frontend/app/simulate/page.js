"use client";

import { useEffect, useState } from "react";
import { Area, CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import CountUp from "../../components/CountUp";
import { get, inr, post } from "../../lib/api";

const AXIS = { fontSize: 12, fill: "#61708a" };

const tooltipStyle = {
  contentStyle: {
    borderRadius: 12,
    border: "1px solid #e2e9f3",
    boxShadow: "0 12px 32px rgba(18,35,74,.12)",
    fontSize: 12,
    padding: "8px 12px",
  },
};

const KNOBS = [
  ["consolidation_rate", "Consolidation rate / yr", 0, 1, 0.05, (v) => `${Math.round(v * 100)}%`],
  ["adoption_rate", "Adoption rate", 0, 1, 0.05, (v) => `${Math.round(v * 100)}%`],
  ["dispute_elasticity", "Dispute elasticity", 0, 1, 0.05, (v) => v.toFixed(2)],
  ["cost_per_ha", "Cost per ha (₹)", 0, 20000, 100, (v) => `₹${inr(v)}`],
];

// Named starting points a presenter can flip between mid-demo.
const PRESETS = {
  "Business as usual": { consolidation_rate: 0.05, adoption_rate: 0.35, dispute_elasticity: 0.45, cost_per_ha: 2600 },
  "Balanced reform": { consolidation_rate: 0.15, adoption_rate: 0.6, dispute_elasticity: 0.45, cost_per_ha: 4200 },
  "Accelerated drive": { consolidation_rate: 0.35, adoption_rate: 0.85, dispute_elasticity: 0.6, cost_per_ha: 7800 },
};

const pct = (v, min, max) => `${((v - min) / (max - min)) * 100}%`;

export default function Simulate() {
  const [districts, setDistricts] = useState([]);
  const [district, setDistrict] = useState("Patna");
  const [years, setYears] = useState(5);
  const [p, setP] = useState(PRESETS["Balanced reform"]);
  const [preset, setPreset] = useState("Balanced reform");
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    get("/api/gis/districts").then(setDistricts).catch(() => {});
  }, []);

  function setKnob(k, v) {
    setP({ ...p, [k]: v });
    setPreset("");
  }

  function applyPreset(name) {
    setP(PRESETS[name]);
    setPreset(name);
  }

  async function run() {
    setBusy(true);
    try {
      setRes(await post("/api/simulation/run", { district, years, ...p }));
    } finally {
      setBusy(false);
    }
  }

  const band = (res?.series || []).map((r) => ({
    ...r,
    range: [r.disputes_pending_low, r.disputes_pending_high],
  }));

  return (
    <>
      <div className="page-head">
        <span className="eyebrow">
          <span className="dot" /> What-if engine · transparent assumptions
        </span>
        <h1 className="page-title">Policy Sandbox — land consolidation</h1>
        <p className="page-sub">
          Test a reform before rolling it out. Every parameter is visible and every result carries an
          uncertainty band — this is a transparent projection, not a prediction.
        </p>
      </div>

      <div className="card reveal reveal-1">
        <div className="card-head">
          <h3>Scenario</h3>
          <div className="row wrap">
            {Object.keys(PRESETS).map((name) => (
              <button
                key={name}
                className={`chip ${preset === name ? "on" : ""}`}
                onClick={() => applyPreset(name)}
              >
                {name}
              </button>
            ))}
          </div>
        </div>

        <div className="grid c3">
          <div>
            <label>District</label>
            <select value={district} onChange={(e) => setDistrict(e.target.value)}>
              {districts.map((d) => (
                <option key={d.district}>{d.district}</option>
              ))}
            </select>
          </div>
          <div>
            <label>
              Horizon — <strong style={{ color: "var(--blue)" }}>{years} years</strong>
            </label>
            <input
              type="range"
              min={1}
              max={15}
              value={years}
              onChange={(e) => setYears(+e.target.value)}
              style={{ "--fill": pct(years, 1, 15) }}
            />
          </div>
          <div style={{ alignSelf: "end" }}>
            <button onClick={run} disabled={busy} style={{ width: "100%" }}>
              {busy ? "Running…" : "▶  Run scenario"}
            </button>
          </div>
        </div>

        <div className="grid c4" style={{ marginTop: 16 }}>
          {KNOBS.map(([k, label, min, max, step, fmt]) => (
            <div key={k}>
              <label>
                {label} — <strong style={{ color: "var(--blue)" }}>{fmt(p[k])}</strong>
              </label>
              <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={p[k]}
                onChange={(e) => setKnob(k, +e.target.value)}
                style={{ "--fill": pct(p[k], min, max) }}
              />
            </div>
          ))}
        </div>
      </div>

      {res?.error && <p className="err">{res.error}</p>}

      {!res && !busy && (
        <div className="card reveal reveal-2" style={{ marginTop: 18 }}>
          <div className="empty">
            <div className="ico">⚗️</div>
            <h3>Pick a scenario and run it</h3>
            <p>
              The sandbox projects pending disputes, parcel consolidation and programme cost over
              your chosen horizon, with an explicit uncertainty band around every estimate.
            </p>
          </div>
        </div>
      )}

      {res?.series?.length > 0 && (
        <>
          <div className="grid c4 stagger" style={{ marginTop: 18 }}>
            <div className="card hover stat good">
              <div className="n">
                <CountUp value={res.summary.disputes_avoided} />
              </div>
              <div className="l">Disputes avoided by yr {years}</div>
              <div className="hint" style={{ marginTop: 6 }}>
                range {res.summary.disputes_avoided_range[0]}–{res.summary.disputes_avoided_range[1]}
              </div>
            </div>
            <div className="card hover stat">
              <div className="n">
                <CountUp value={res.summary.avg_parcel_ha_change_pct} decimals={1} prefix="+" suffix="%" />
              </div>
              <div className="l">Avg parcel size</div>
              <div className="hint" style={{ marginTop: 6 }}>from {res.baseline.avg_parcel_ha} ha</div>
            </div>
            <div className="card hover stat warm">
              <div className="n">₹{inr(res.summary.total_cost_inr)}</div>
              <div className="l">Cumulative cost</div>
              <div className="hint" style={{ marginTop: 6 }}>over {years} years</div>
            </div>
            <div className="card hover stat">
              <div className="n">
                <CountUp value={res.baseline.fragmented_parcels} />
              </div>
              <div className="l">Fragmented parcels at start</div>
              <div className="hint" style={{ marginTop: 6 }}>
                of {res.baseline.parcels} in {district}
              </div>
            </div>
          </div>

          <div className="card hover reveal reveal-2" style={{ marginTop: 16 }}>
            <div className="card-head">
              <h3>Projected pending land disputes</h3>
              <span className="badge official">{district} · {years}-year horizon</span>
            </div>
            <div style={{ height: 340 }}>
              <ResponsiveContainer>
                <ComposedChart data={band}>
                  <defs>
                    <linearGradient id="bandFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#0070c0" stopOpacity={0.28} />
                      <stop offset="100%" stopColor="#0070c0" stopOpacity={0.06} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="#eef2f7" vertical={false} />
                  <XAxis
                    dataKey="year"
                    tick={AXIS}
                    axisLine={false}
                    tickLine={false}
                    label={{ value: "year", position: "insideBottom", offset: -2, fontSize: 12, fill: "#61708a" }}
                  />
                  <YAxis tick={AXIS} axisLine={false} tickLine={false} />
                  <Tooltip {...tooltipStyle} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Area dataKey="range" name="uncertainty band" fill="url(#bandFill)" stroke="none" animationDuration={900} />
                  <Line
                    dataKey="disputes_pending"
                    name="central estimate"
                    stroke="#0070c0"
                    strokeWidth={3}
                    dot={{ r: 0 }}
                    activeDot={{ r: 6, strokeWidth: 2, stroke: "#fff" }}
                    animationDuration={1200}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="note reveal reveal-3" style={{ marginTop: 14 }}>
            <strong>Assumptions used:</strong>{" "}
            {Object.entries(res.assumptions)
              .map(([k, v]) => `${k.replace(/_/g, " ")} = ${v}`)
              .join(" · ")}
            <br />
            {res.caveat}
          </div>
        </>
      )}
    </>
  );
}
