"use client";

import { usePathname } from "next/navigation";

import Nav from "./Nav";

// The login page is full-bleed; every other page sits inside the padded wrap.
export default function Shell({ children }) {
  const bare = usePathname() === "/";
  return (
    <>
      <Nav />
      {bare ? children : <main className="wrap">{children}</main>}
    </>
  );
}
