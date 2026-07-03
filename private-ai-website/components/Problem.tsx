import Section from "./Section";

const problems = [
  {
    title: "AI is now a business requirement",
    body: "Your teams already want AI for research, drafting, analysis, and automation. The question is no longer whether to use it — it's how to use it without giving up control.",
  },
  {
    title: "Sensitive data can't always leave",
    body: "Contracts, financials, client records, HR files, and deal pipelines often can't be pasted into public AI platforms — for legal, contractual, or competitive reasons.",
  },
  {
    title: "Generic tools don't know your business",
    body: "Off-the-shelf assistants haven't read your documents, your emails, or your playbooks. Without your private knowledge, their answers stay generic.",
  },
  {
    title: "Enterprises need control and auditability",
    body: "Who accessed what, which model answered, where the data lives, and how long it's retained — leadership and compliance need real answers, not vendor assurances.",
  },
];

export default function Problem() {
  return (
    <Section
      id="problem"
      label="The Problem"
      title="Your teams need AI. Your data needs protection."
      lead="Most companies are stuck between two bad options: adopt public AI tools and accept the data exposure, or hold back and fall behind. There is a third option — run the AI yourself."
      tone="raised"
    >
      <div className="grid gap-6 md:grid-cols-2">
        {problems.map((p) => (
          <div key={p.title} className="card">
            <h3 className="text-lg font-semibold text-white">{p.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-mist-300">{p.body}</p>
          </div>
        ))}
      </div>
    </Section>
  );
}
