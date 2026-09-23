"use client";

import "maplibre-gl/dist/maplibre-gl.css";

import { useEffect, useRef, useState } from "react";

import { API, get } from "../../lib/api";

const COLORS = { none: "#1e8a4c", pending: "#e87a1e", resolved: "#0070c0" };
const KEY = process.env.NEXT_PUBLIC_MAPTILER_KEY || "";

const STYLE = KEY
  ? `https://api.maptiler.com/maps/streets-v2/style.json?key=${KEY}`
  : {
      version: 8,
      sources: {
        osm: {
          type: "raster",
          tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
          tileSize: 256,
          attribution: "© OpenStreetMap contributors",
        },
      },
      layers: [{ id: "osm", type: "raster", source: "osm" }],
    };

export default function MapPage() {
  const box = useRef(null);
  const map = useRef(null);
  const [districts, setDistricts] = useState([]);
  const [district, setDistrict] = useState("");
  const [bhuvan, setBhuvan] = useState(false);
  const [info, setInfo] = useState(null);

  useEffect(() => {
    get("/api/gis/districts").then(setDistricts).catch(() => {});
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const maplibregl = (await import("maplibre-gl")).default;
      if (cancelled || map.current || !box.current) return;

      map.current = new maplibregl.Map({
        container: box.current,
        style: STYLE,
        center: [85.5, 25.6],
        zoom: 7,
      });
      map.current.addControl(new maplibregl.NavigationControl(), "top-right");

      map.current.on("load", () => {
        map.current.addSource("parcels", { type: "geojson", data: `${API}/api/gis/parcels` });
        map.current.addLayer({
          id: "parcels-fill",
          type: "fill",
          source: "parcels",
          paint: {
            "fill-color": [
              "match",
              ["get", "dispute_status"],
              "pending", COLORS.pending,
              "resolved", COLORS.resolved,
              COLORS.none,
            ],
            "fill-opacity": 0.55,
          },
        });
        map.current.addLayer({
          id: "parcels-line",
          type: "line",
          source: "parcels",
          paint: { "line-color": "#22303d", "line-width": 0.4 },
        });

        map.current.addSource("bhuvan", {
          type: "raster",
          tiles: [
            "https://bhuvan-vec1.nrsc.gov.in/bhuvan/wms?service=WMS&version=1.1.1&request=GetMap" +
              "&layers=lulc:LULC50K_1516&styles=&format=image/png&transparent=true" +
              "&srs=EPSG:3857&width=256&height=256&bbox={bbox-epsg-3857}",
          ],
          tileSize: 256,
          attribution: "ISRO / NRSC Bhuvan",
        });
        map.current.addLayer(
          { id: "bhuvan-lulc", type: "raster", source: "bhuvan", layout: { visibility: "none" }, paint: { "raster-opacity": 0.6 } },
          "parcels-fill"
        );

        map.current.on("click", "parcels-fill", (e) => setInfo(e.features[0].properties));
        map.current.on("mouseenter", "parcels-fill", () => (map.current.getCanvas().style.cursor = "pointer"));
        map.current.on("mouseleave", "parcels-fill", () => (map.current.getCanvas().style.cursor = ""));
      });
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const m = map.current;
    if (!m || !m.getSource || !m.isStyleLoaded?.()) return;
    const src = m.getSource("parcels");
    if (src) src.setData(`${API}/api/gis/parcels${district ? `?district=${district}` : ""}`);
    const d = districts.find((x) => x.district === district);
    if (d) {
      const centres = { Patna: [85.137, 25.594], Muzaffarpur: [85.391, 26.122], Gaya: [85.0, 24.796], Purnia: [87.475, 25.777] };
      if (centres[district]) m.flyTo({ center: centres[district], zoom: 9.5 });
    } else {
      m.flyTo({ center: [85.5, 25.6], zoom: 7 });
    }
  }, [district, districts]);

  function toggleBhuvan() {
    const m = map.current;
    if (!m?.getLayer("bhuvan-lulc")) return;
    const next = !bhuvan;
    m.setLayoutProperty("bhuvan-lulc", "visibility", next ? "visible" : "none");
    setBhuvan(next);
  }

  return (
    <>
      <div className="page-head">
        <span className="eyebrow">
          <span className="dot" /> Cadastre × ISRO Bhuvan
        </span>
        <h1 className="page-title">GIS Studio</h1>
        <p className="page-sub">
          Cadastral parcels, disputes and climate risk over ISRO Bhuvan land-use / land-cover layers.
        </p>
      </div>

      <div className="card row wrap reveal reveal-1" style={{ marginBottom: 14 }}>
        <div style={{ minWidth: 240 }}>
          <label>District</label>
          <select value={district} onChange={(e) => setDistrict(e.target.value)}>
            <option value="">All districts (Bihar)</option>
            {districts.map((d) => (
              <option key={d.district} value={d.district}>
                {d.district} ({d.parcels})
              </option>
            ))}
          </select>
        </div>
        <div style={{ alignSelf: "flex-end" }}>
          <button className={bhuvan ? "" : "ghost"} onClick={toggleBhuvan}>
            🛰️ {bhuvan ? "Hide" : "Show"} Bhuvan LULC
          </button>
        </div>
        <div className="row wrap" style={{ alignSelf: "flex-end", marginLeft: "auto" }}>
          {Object.entries(COLORS).map(([k, c]) => (
            <span className="legend-chip" key={k}>
              <span className="legend-dot" style={{ background: c }} />
              {k} dispute
            </span>
          ))}
        </div>
      </div>

      <div className="grid c2 reveal reveal-2" style={{ gridTemplateColumns: "2.2fr 1fr" }}>
        <div className="map" ref={box} />
        <div className="card">
          <div className="card-head">
            <h3>Parcel details</h3>
            {info && (
              <span className={`badge ${info.dispute_status === "pending" ? "synthetic" : "peer_reviewed"}`}>
                {String(info.dispute_status)}
              </span>
            )}
          </div>
          {info ? (
            <table key={info.parcel_uid} className="reveal">
              <tbody>
                {["parcel_uid", "district", "block", "village", "land_use", "area_ha", "owners", "dispute_status", "climate_risk"].map((k) => (
                  <tr key={k}>
                    <th style={{ width: 120 }}>{k.replace(/_/g, " ")}</th>
                    <td>{String(info[k])}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty">
              <div className="ico">🗺️</div>
              <h3>Click any parcel</h3>
              <p>Select a parcel on the map to inspect ownership, land use, dispute status and climate risk.</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
