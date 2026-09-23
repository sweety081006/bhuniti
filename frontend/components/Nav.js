"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { currentUser, logout } from "../lib/api";
import { ROLE_LABEL } from "../lib/roles";

const LINKS = [
  ["/search", "AI Search", "◆"],
  ["/map", "GIS Studio", "◈"],
  ["/simulate", "Policy Sandbox", "◇"],
  ["/dashboard", "Dashboards", "▤"],
];

const initials = (name = "") =>
  name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("") || "U";

// Pages other than the login page require a signed-in user.
export default function Nav() {
  const path = usePathname();
  const router = useRouter();
  const [user, setUser] = useState(undefined); // undefined = not checked yet

  useEffect(() => {
    const u = currentUser();
    setUser(u);
    if (!u && path !== "/") router.replace("/");
  }, [path, router]);

  if (path === "/") return null; // login page has its own header

  return (
    <nav className="nav">
      <Link href="/search" className="brand">
        <span className="brand-mark">भू</span>
        Bhu<span>Niti</span>
      </Link>

      <div className="nav-links">
        {LINKS.map(([href, label, icon]) => (
          <Link key={href} href={href} className={`nav-link ${path === href ? "active" : ""}`}>
            <span style={{ opacity: 0.7, marginRight: 6, fontSize: 11 }}>{icon}</span>
            {label}
          </Link>
        ))}
      </div>

      <div className="spacer" />

      {user && (
        <>
          <span className="role">
            <span className="avatar">{initials(user.name)}</span>
            <span className="who">
              {user.name} · {ROLE_LABEL[user.role] || user.role}
            </span>
          </span>
          <button
            className="ghost"
            onClick={() => {
              logout();
              router.replace("/");
            }}
          >
            Sign out
          </button>
        </>
      )}
    </nav>
  );
}
