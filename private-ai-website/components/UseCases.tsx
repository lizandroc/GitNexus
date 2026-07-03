import Section from "./Section";
import Icon, { type IconName } from "./Icon";

const useCases: { icon: IconName; title: string; body: string }[] = [
  { icon: "document", title: "Internal Document Q&A", body: "Ask questions across policies, reports, and archives — answered with citations from your own files." },
  { icon: "audit", title: "Contract & Legal Review Support", body: "Surface key terms, obligations, and unusual clauses to speed up attorney and deal-desk review." },
  { icon: "chart", title: "Sales Conversation Analysis", body: "Turn call notes and email threads into deal signals, objections, and next-step recommendations." },
  { icon: "route", title: "Lead Recovery & Follow-Up", body: "Analyze stalled pipeline and generate tailored, context-aware re-engagement strategies." },
  { icon: "users", title: "CRM Intelligence", body: "Draft activity notes, enrich records, and keep account context current — automatically." },
  { icon: "search", title: "Executive Research Assistant", body: "Brief leadership from internal knowledge and curated sources without exposing the questions being asked." },
  { icon: "api", title: "Email & Communication Analysis", body: "Summarize threads, extract action items, and draft replies inside your privacy boundary." },
  { icon: "shield", title: "Customer Support Knowledge Assistant", body: "Give support teams grounded answers from manuals, tickets, and internal runbooks." },
  { icon: "workflow", title: "Operations Workflow Automation", body: "Automate intake, triage, data extraction, and report generation across departments." },
  { icon: "chart", title: "Financial Document Summarization", body: "Digest statements, filings, and budget packs into concise, verifiable summaries." },
  { icon: "document", title: "HR Policy Assistant", body: "Answer employee policy questions consistently, with sources, and without exposing personnel data." },
  { icon: "users", title: "Training & Onboarding Assistant", body: "Turn institutional knowledge into an always-available guide for new team members." },
];

export default function UseCases() {
  return (
    <Section
      id="use-cases"
      label="Use Cases"
      title="Where private AI earns its keep"
      lead="Every use case below runs against your internal knowledge, inside your deployment boundary. These aren't hypotheticals — they're the workflows enterprises automate first."
      tone="raised"
    >
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {useCases.map((u) => (
          <div key={u.title} className="card !p-5">
            <div className="flex items-start gap-3">
              <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-500/15 text-brand-400">
                <Icon name={u.icon} className="h-4.5 w-4.5" />
              </span>
              <div>
                <h3 className="text-sm font-semibold text-white">{u.title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-mist-400">{u.body}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Section>
  );
}
