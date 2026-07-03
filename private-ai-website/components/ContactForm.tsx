"use client";

import { useState, type FormEvent } from "react";

type Status = "idle" | "sending" | "sent" | "error";

const industries = [
  "Professional services",
  "Legal",
  "Finance",
  "Healthcare",
  "Media & entertainment",
  "Real estate",
  "Manufacturing",
  "Technology",
  "Other",
];

const timelines = ["As soon as possible", "1–3 months", "3–6 months", "Exploring options"];

export default function ContactForm() {
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState("");

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());
    setStatus("sending");
    setError("");
    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error || "Something went wrong. Please try again.");
      }
      setStatus("sent");
      form.reset();
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Something went wrong.");
    }
  }

  if (status === "sent") {
    return (
      <div className="card text-center">
        <h3 className="text-lg font-semibold text-white">Thank you — we received your message.</h3>
        <p className="mt-2 text-sm text-mist-300">
          We&rsquo;ll get back to you within two business days.
        </p>
        <button className="btn-secondary mt-6" onClick={() => setStatus("idle")}>
          Send another message
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <div className="grid gap-5 sm:grid-cols-2">
        <div>
          <label htmlFor="name" className="field-label">Name *</label>
          <input id="name" name="name" required autoComplete="name" className="field" placeholder="Jane Smith" />
        </div>
        <div>
          <label htmlFor="company" className="field-label">Company *</label>
          <input id="company" name="company" required autoComplete="organization" className="field" placeholder="Acme Corp" />
        </div>
        <div>
          <label htmlFor="email" className="field-label">Email *</label>
          <input id="email" name="email" type="email" required autoComplete="email" className="field" placeholder="jane@acme.com" />
        </div>
        <div>
          <label htmlFor="phone" className="field-label">Phone</label>
          <input id="phone" name="phone" type="tel" autoComplete="tel" className="field" placeholder="+1 (555) 000-0000" />
        </div>
        <div>
          <label htmlFor="industry" className="field-label">Industry</label>
          <select id="industry" name="industry" className="field" defaultValue="">
            <option value="" disabled>Select an industry</option>
            {industries.map((i) => (
              <option key={i} value={i}>{i}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="timeline" className="field-label">Estimated timeline</label>
          <select id="timeline" name="timeline" className="field" defaultValue="">
            <option value="" disabled>Select a timeline</option>
            {timelines.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div className="sm:col-span-2">
          <label htmlFor="goals" className="field-label">What do you want AI to help with? *</label>
          <textarea
            id="goals"
            name="goals"
            required
            rows={4}
            className="field resize-y"
            placeholder="e.g. We want our team to search 10 years of project documents, and automate first-draft contract summaries…"
          />
        </div>
        <fieldset className="sm:col-span-2">
          <legend className="field-label">Do you need local / private deployment?</legend>
          <div className="flex flex-wrap gap-x-6 gap-y-2 pt-1">
            {["Yes — data must stay in our environment", "Likely — we need to review", "Not sure yet"].map((opt) => (
              <label key={opt} className="flex items-center gap-2 text-sm text-mist-200">
                <input type="radio" name="deployment" value={opt} className="accent-brand-500" />
                {opt}
              </label>
            ))}
          </div>
        </fieldset>
      </div>

      {status === "error" ? (
        <p className="mt-4 text-sm text-red-400" role="alert">{error}</p>
      ) : null}

      <button type="submit" disabled={status === "sending"} className="btn-primary mt-7 w-full sm:w-auto">
        {status === "sending" ? "Sending…" : "Request a Strategy Call"}
      </button>
    </form>
  );
}
