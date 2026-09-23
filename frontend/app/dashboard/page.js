"use client";

import { useEffect, useState } from "react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import CountUp from "../../components/CountUp";
import { get } from "../../lib/api";

const PALETTE = ["#0070c0", "#e87a1e", "#1e8a4c", "#1f3864", "#7b61a8", "#3aa8a0", "#b3261e"];

const AXIS = { fontSize: 12, fill: "#61708a" };

const tooltipStyle = {
  contentStyle: {
    borderRadius: 12,
    border: "1px solid #e2e9f3",
    boxShadow: "0 12px 32px rgba(18,35,74,.12)",
    fontSize: 12,
    padding: "8px 12px",
  },
  cursor: { fill: "rgba(0,112,192,.06)" },
};

export default function Dashboard() {
  const [o, setO] = useState(null);
  const [disputes, setDisputes] = useState([]);
  const [docs, setDocs] = useState([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    get("/api/dashboard/overview").then(setO).catch(() => {});
    get("/api/dashboard/disputes").then(setDisputes).catch(() => {});
    get("/api/documents?limit=100").then(setDocs).catch(() => {});
  }, []);

  const landUse = Object.entries(o?.parcels_by_land_use || {}).map(([name, value]) => ({ name, value }));
  const byType = Object.entries(o?.documents_by_type || {}).map(([name, value]) => ({ name, value }));

  const years = [...new Set(disputes.map((d) => d.year))].sort();
  const districts = [...new Set(disputes.map((d) => d.district))];
  const trend = years.map((year) => {
    const row = { year };
    districts.forEach((d) => {
      const hit = disputes.find((x) => x.year === year && x.district === d);
      row[d] = hit ? hit.pending_cases : null;
    });
    row.total = districts.reduce((sum, d) => sum + (row[d] || 0), 0);
    return row;
  });

  // headline movement across the dispute series, for the KPI strip
  const first = trend[0]?.total || 0;
  const last = trend[trend.length - 1]?.total || 0;
  const delta = first ? Math.round(((last - first) / first) * 100) : 0;

  const provenances = ["all", ...new Set(docs.map((d) => d.provenance))];
  const shownDocs = filter === "all" ? docs : docs.filter((d) => d.provenance === filter);

  const KPIS = [
    { v: o?.documents, l: "Documents", cls: "" },
    { v: o?.indexed_chunks, l: "Indexed passages", cls: "" },
    { v: o?.parcels, l: "Parcels", cls: "good" },
    { v: o?.parcels_by_dispute_status?.pending, l: "Parcels under dispute", cls: "warm" },
  ];

  return (
    <>
      <div className="page-head">
        <span className="eyebrow">
          <span className="dot" /> Live from the platform index
        </span>
        <h1 className="page-title">Dashboards</h1>
        <p className="page-sub">
          Research output, land-use composition, dispute trends and policy indicators —{" "}
          {o?.pilot_state || "Bihar"}.
        </p>
      </div>

      <div className="grid c4 stagger">
        {KPIS.map((k) => (
          <div className={`card hover stat ${k.cls}`} key={k.l}>
            <div className="n">
              <CountUp value={k.v} />
            </div>
            <div className="l">{k.l}</div>
          </div>
        ))}
      </div>

      <div className="grid c2 stagger" style={{ marginTop: 16 }}>
        <div className="card hover">
          <div className="card-head">
            <h3>Pending land disputes by district</h3>
            {trend.length > 1 && (
              <span className={`badge ${delta <= 0 ? "peer_reviewed" : "synthetic"}`}>
                {delta <= 0 ? "▼" : "▲"} {Math.abs(delta)}% since {trend[0].year}
              </span>
            )}
          </div>
          <div style={{ height: 280 }}>
            <ResponsiveContainer>
              <LineChart data={trend}>
                <CartesianGrid stroke="#eef2f7" vertical={false} />
                <XAxis dataKey="year" tick={AXIS} axisLine={false} tickLine={false} />
                <YAxis tick={AXIS} axisLine={false} tickLine={false} />
                <Tooltip {...tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                {districts.map((d, i) => (
                  <Line
                    key={d}
                    dataKey={d}
                    stroke={PALETTE[i % PALETTE.length]}
                    strokeWidth={2.5}
                    dot={{ r: 0 }}
                    activeDot={{ r: 5, strokeWidth: 2, stroke: "#fff" }}
                    animationDuration={1100}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card hover">
          <div className="card-head">
            <h3>Land use composition</h3>
            <span className="badge">{landUse.length} classes</span>
          </div>
          <div style={{ height: 280 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={landUse}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={52}
                  outerRadius={95}
                  paddingAngle={3}
                  animationDuration={1100}
                  label={({ name, percent }) => `${name} ${Math.round(percent * 100)}%`}
                  labelLine={false}
                >
                  {landUse.map((_, i) => (
                    <Cell key={i} fill={PALETTE[i % PALETTE.length]} stroke="#fff" strokeWidth={2} />
                  ))}
                </Pie>
                <Tooltip {...tooltipStyle} cursor={false} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card hover">
          <div className="card-head">
            <h3>Repository by document type</h3>
          </div>
          <div style={{ height: 250 }}>
            <ResponsiveContainer>
              <BarChart data={byType}>
                <defs>
                  <linearGradient id="barBlue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#2f97e8" />
                    <stop offset="100%" stopColor="#0070c0" />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#eef2f7" vertical={false} />
                <XAxis dataKey="name" tick={AXIS} axisLine={false} tickLine={false} />
                <YAxis allowDecimals={false} tick={AXIS} axisLine={false} tickLine={false} />
                <Tooltip {...tooltipStyle} />
                <Bar dataKey="value" fill="url(#barBlue)" radius={[6, 6, 0, 0]} animationDuration={1000} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card hover">
          <div className="card-head">
            <h3>Total pending disputes — all districts</h3>
          </div>
          <div style={{ height: 250 }}>
            <ResponsiveContainer>
              <AreaChart data={trend}>
                <defs>
                  <linearGradient id="areaWarm" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#e87a1e" stopOpacity={0.55} />
                    <stop offset="100%" stopColor="#e87a1e" stopOpacity={0.04} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#eef2f7" vertical={false} />
                <XAxis dataKey="year" tick={AXIS} axisLine={false} tickLine={false} />
                <YAxis tick={AXIS} axisLine={false} tickLine={false} />
                <Tooltip {...tooltipStyle} />
                <Area
                  dataKey="total"
                  name="pending cases"
                  stroke="#e87a1e"
                  strokeWidth={2.5}
                  fill="url(#areaWarm)"
                  animationDuration={1100}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card hover" style={{ marginTop: 16 }}>
        <div className="card-head">
          <h3>Repository</h3>
          <div className="row wrap">
            {provenances.map((p) => (
              <button
                key={p}
                className={`chip ${filter === p ? "on" : ""}`}
                onClick={() => setFilter(p)}
              >
                {p === "all" ? `All (${docs.length})` : p.replace(/_/g, " ")}
              </button>
            ))}
          </div>
        </div>
        <div style={{ maxHeight: 340, overflow: "auto" }}>
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Type</th>
                <th>Provenance</th>
              </tr>
            </thead>
            <tbody>
              {shownDocs.map((d) => (
                <tr key={d.id}>
                  <td>
                    {d.url ? (
                      <a href={d.url} target="_blank" rel="noreferrer">
                        {d.title}
                      </a>
                    ) : (
                      d.title
                    )}
                  </td>
                  <td>{d.doc_type}</td>
                  <td>
                    <span className={`badge ${d.provenance}`}>{d.provenance}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {shownDocs.length === 0 && <p className="hint" style={{ padding: 14 }}>No documents in this category.</p>}
        </div>
      </div>
    </>
  );
}
