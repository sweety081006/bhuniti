"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import CountUp from "../components/CountUp";
import { currentUser, login } from "../lib/api";
import { ROLES } from "../lib/roles";

const HERO_STATS = [
  { n: 4, label: "Integrated modules" },
  { n: 4, label: "Role-based workspaces" },
  { n: 100, suffix: "%", label: "Cited answers" },
  { text: "On-prem", label: "Zero data egress" },
];

export default function Login() {
  const router = useRouter();
  const [role, setRole] = useState(ROLES[0]);
  const [email, setEmail] = useState(ROLES[0].email);
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  // already signed in -> straight to the AI page
  useEffect(() => {
    if (currentUser()) router.replace("/search");
  }, [router]);

  function pick(r) {
    setRole(r);
    setEmail(r.email);
    setErr("");
  }

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setErr("");
    try {
      await login(email, password);
      router.push("/search");
    } catch (e2) {
      setErr(e2.message);
      setBusy(false);
    }
  }

  return (
    <div className="login-shell">
      <div className="blob b1" />
      <div className="blob b2" />
      <div className="blob b3" />

      <div className="login">
        <div className="login-hero reveal">
          <div className="login-brand">
            <span className="brand-mark">भू</span>
            Bhu<span>Niti</span>
          </div>

          <h1>
            National Land Governance <em>Research &amp; Policy</em> Platform
          </h1>
          <p>
            Evidence-based land governance for India — one place for land data, research, law and
            maps, with an AI layer that turns them into cited answers and policy simulations.
          </p>

          <div className="hero-stats stagger">
            {HERO_STATS.map((s) => (
              <div className="hero-stat" key={s.label}>
                <div className="hn">
                  {s.text ?? <CountUp value={s.n} suffix={s.suffix || ""} duration={1100} />}
                </div>
                <div className="hl">{s.label}</div>
              </div>
            ))}
          </div>
        </div>

        <form className="login-card" onSubmit={submit}>
          <h2>Sign in</h2>
          <p className="sub">Choose the workspace that matches your role.</p>

          <div className="role-grid">
            {ROLES.map((r) => (
              <button
                type="button"
                key={r.key}
                className={`role-card ${role.key === r.key ? "on" : ""}`}
                style={{ "--c": r.color }}
                onClick={() => pick(r)}
              >
                <div className="role-ico">{r.icon}</div>
                <div className="role-name">{r.label}</div>
                <div className="role-desc">{r.desc}</div>
              </button>
            ))}
          </div>

          <div className="grid c2" style={{ marginTop: 18 }}>
            <div>
              <label>Email</label>
              <input
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="username"
              />
            </div>
            <div>
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </div>
          </div>

          <div className="row" style={{ marginTop: 16 }}>
            <button
              type="submit"
              disabled={busy}
              style={{
                width: "100%",
                background: `linear-gradient(135deg, ${role.color}, color-mix(in srgb, ${role.color} 55%, #ffffff))`,
                boxShadow: `0 6px 18px color-mix(in srgb, ${role.color} 40%, transparent)`,
              }}
            >
              {busy ? "Signing in…" : `Continue as ${role.label} →`}
            </button>
          </div>

          {err && <p className="err">{err}</p>}

          <div className="login-foot">
            <span>🔒 Role-based access</span>
            <span>🇮🇳 DPDP-aligned</span>
            <span>⚙️ Runs on-premise</span>
          </div>
        </form>
      </div>
    </div>
  );
}
