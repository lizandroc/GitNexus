"use client";

import { useState } from "react";
import Icon from "./Icon";

const links = [
  { href: "#solution", label: "What We Do" },
  { href: "#use-cases", label: "Use Cases" },
  { href: "#how-it-works", label: "Process" },
  { href: "#privacy", label: "Privacy" },
  { href: "#packages", label: "Engagements" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-ink-800 bg-ink-950/85 backdrop-blur">
      <div className="container-content flex h-16 items-center justify-between">
        <a href="#" className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500/15 text-brand-400">
            <Icon name="shield" className="h-5 w-5" />
          </span>
          <span className="text-sm font-semibold tracking-wide text-white">
            Sovereign AI Systems
          </span>
        </a>

        <nav className="hidden items-center gap-8 md:flex">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-sm text-mist-300 transition hover:text-white"
            >
              {l.label}
            </a>
          ))}
          <a href="#contact" className="btn-primary !px-4 !py-2">
            Book a Strategy Call
          </a>
        </nav>

        <button
          className="text-mist-200 md:hidden"
          onClick={() => setOpen(!open)}
          aria-label="Toggle navigation menu"
          aria-expanded={open}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-6 w-6">
            {open ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
          </svg>
        </button>
      </div>

      {open ? (
        <nav className="border-t border-ink-800 bg-ink-950 px-6 py-4 md:hidden">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              onClick={() => setOpen(false)}
              className="block py-2.5 text-sm text-mist-200 hover:text-white"
            >
              {l.label}
            </a>
          ))}
          <a
            href="#contact"
            onClick={() => setOpen(false)}
            className="btn-primary mt-3 w-full"
          >
            Book a Strategy Call
          </a>
        </nav>
      ) : null}
    </header>
  );
}
