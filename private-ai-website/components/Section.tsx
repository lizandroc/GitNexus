import type { ReactNode } from "react";

type SectionProps = {
  id?: string;
  label: string;
  title: string;
  lead?: string;
  children: ReactNode;
  tone?: "default" | "raised";
};

/** Shared section shell: consistent spacing, label, title, and lead. */
export default function Section({
  id,
  label,
  title,
  lead,
  children,
  tone = "default",
}: SectionProps) {
  return (
    <section
      id={id}
      className={`py-20 md:py-28 ${tone === "raised" ? "bg-ink-900/50" : ""}`}
    >
      <div className="container-content">
        <p className="section-label">{label}</p>
        <h2 className="section-title">{title}</h2>
        {lead ? <p className="section-lead">{lead}</p> : null}
        <div className="mt-12">{children}</div>
      </div>
    </section>
  );
}
