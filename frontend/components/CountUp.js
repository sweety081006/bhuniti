"use client";

import { useEffect, useRef, useState } from "react";

// Animates a number from 0 to `value` once it changes. Purely cosmetic —
// renders the plain value when the browser asks for reduced motion.
export default function CountUp({ value, duration = 900, decimals = 0, prefix = "", suffix = "" }) {
  const [n, setN] = useState(0);
  const from = useRef(0);

  useEffect(() => {
    const target = Number(value);
    if (!Number.isFinite(target)) return;

    const reduce =
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    if (reduce || duration <= 0) {
      from.current = target;
      setN(target);
      return;
    }

    const start = performance.now();
    const a = from.current;
    let raf;
    const tick = (t) => {
      const p = Math.min(1, (t - start) / duration);
      const eased = 1 - Math.pow(1 - p, 3); // easeOutCubic
      setN(a + (target - a) * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
      else from.current = target;
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value, duration]);

  if (value === null || value === undefined || !Number.isFinite(Number(value))) return <>—</>;

  const shown = decimals
    ? n.toFixed(decimals)
    : new Intl.NumberFormat("en-IN").format(Math.round(n));
  return (
    <>
      {prefix}
      {shown}
      {suffix}
    </>
  );
}
