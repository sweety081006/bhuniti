// One card per user type. Selecting a card pre-fills the demo account for that role.
export const ROLES = [
  { key: "researcher", label: "Researcher", email: "researcher@bhuniti.in", color: "#0070c0", icon: "🎓",
    desc: "Academic & think-tank users: search, synthesise, run scenarios, publish." },
  { key: "legal", label: "Legal Authority", email: "legal@bhuniti.in", color: "#7b61a8", icon: "⚖️",
    desc: "Tribunals, courts & legal cells: judgments, dispute analytics, legal documents." },
  { key: "official", label: "Government Official", email: "official@bhuniti.in", color: "#e87a1e", icon: "🏛️",
    desc: "MoRD / DoLR & State revenue officers: policy dashboards, sandbox, KPIs." },
  { key: "institution", label: "Institution / Survey Agency", email: "institution@bhuniti.in", color: "#1e8a4c", icon: "🛰️",
    desc: "State survey directorates & research organisations: upload datasets, workspaces." },
];

export const ROLE_LABEL = Object.fromEntries(ROLES.map((r) => [r.key, r.label]));
ROLE_LABEL.public = "Public";
