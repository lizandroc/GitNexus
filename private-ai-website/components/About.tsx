import Section from "./Section";

const strengths = [
  ["AI strategy", "Prioritizing where AI creates measurable value — and where it doesn't belong yet."],
  ["Product development", "Shipping working software, not slide decks: dashboards, tools, and APIs teams actually use."],
  ["Workflow automation", "Mapping real operational processes before automating them, so tools fit the work."],
  ["Enterprise thinking", "Permissions, audit trails, retention, and deployment boundaries treated as first-class requirements."],
  ["Cross-industry fluency", "Backgrounds spanning media, sales, operations, and technology — we speak both boardroom and terminal."],
  ["Translation", "Turning business needs into working AI systems — and explaining technical trade-offs in plain language."],
];

export default function About() {
  return (
    <Section
      id="about"
      label="Who You're Working With"
      title="A strategic AI partner, not just a development shop"
      lead="Placeholder copy — personalize with your story. The through-line: we've built products, run revenue operations, and shipped automation for real businesses. We know that an AI system succeeds when it fits the workflow, respects the data, and earns the team's trust."
    >
      <div className="grid gap-x-10 gap-y-8 sm:grid-cols-2 lg:grid-cols-3">
        {strengths.map(([title, body]) => (
          <div key={title}>
            <h3 className="text-base font-semibold text-white">{title}</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-mist-300">{body}</p>
          </div>
        ))}
      </div>
    </Section>
  );
}
