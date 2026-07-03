import Section from "./Section";
import Icon from "./Icon";

const tiers = [
  {
    name: "Private AI Strategy Blueprint",
    audience: "For companies that need a roadmap before they build.",
    features: [
      "AI opportunity audit across your teams",
      "Data privacy and exposure review",
      "Use-case prioritization by value and risk",
      "Model and deployment recommendation",
      "Phased implementation roadmap",
    ],
    cta: "Request a Blueprint",
    highlighted: false,
  },
  {
    name: "Local AI MVP Build",
    audience: "For companies that want a working internal AI system, fast.",
    features: [
      "Local or private-cloud LLM setup",
      "Private document Q&A over your knowledge",
      "Operations dashboard with privacy status",
      "One or two custom workflow tools",
      "Team testing and feedback cycle",
    ],
    cta: "Scope an MVP",
    highlighted: true,
  },
  {
    name: "Enterprise Private AI Deployment",
    audience: "For companies ready for a production-grade private AI platform.",
    features: [
      "Custom deployment: on-premise or private cloud",
      "User permissions and role-based access",
      "Audit logs and retention controls",
      "Multiple knowledge bases and custom tools",
      "API integrations with your business systems",
      "Training, documentation, and ongoing support",
    ],
    cta: "Plan a Deployment",
    highlighted: false,
  },
];

export default function Packages() {
  return (
    <Section
      id="packages"
      label="Engagements"
      title="Three ways to start"
      lead="Every engagement is fixed-scope and outcome-defined. Start with strategy, prove value with an MVP, or go straight to a production deployment."
    >
      <div className="grid gap-6 lg:grid-cols-3">
        {tiers.map((t) => (
          <div
            key={t.name}
            className={`card flex flex-col ${
              t.highlighted ? "border-brand-500/60 bg-ink-800/80 ring-1 ring-brand-500/30" : ""
            }`}
          >
            {t.highlighted ? (
              <span className="mb-4 inline-flex w-fit rounded-full bg-brand-500/15 px-3 py-1 text-xs font-semibold text-brand-300">
                Most popular starting point
              </span>
            ) : null}
            <h3 className="text-lg font-semibold text-white">{t.name}</h3>
            <p className="mt-1.5 text-sm text-mist-400">{t.audience}</p>
            <ul className="mt-6 flex-1 space-y-3">
              {t.features.map((f) => (
                <li key={f} className="flex items-start gap-2.5 text-sm text-mist-200">
                  <span className="mt-0.5 text-brand-400">
                    <Icon name="check" className="h-4 w-4" />
                  </span>
                  {f}
                </li>
              ))}
            </ul>
            <a
              href="#contact"
              className={`${t.highlighted ? "btn-primary" : "btn-secondary"} mt-8 w-full`}
            >
              {t.cta}
            </a>
          </div>
        ))}
      </div>
    </Section>
  );
}
