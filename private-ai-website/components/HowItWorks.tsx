import Section from "./Section";

const steps = [
  {
    title: "Discovery & workflow mapping",
    body: "We sit with your teams to map where AI creates real value: which documents, workflows, and decisions matter, and what privacy constraints apply.",
  },
  {
    title: "Private model & infrastructure setup",
    body: "We select and deploy the right open-source models for your workloads — on your hardware, on-premise servers, or your private cloud.",
  },
  {
    title: "Document & data ingestion",
    body: "Your internal knowledge is indexed privately: chunked, embedded, and made searchable inside your environment. Nothing is sent out.",
  },
  {
    title: "Custom tool & automation buildout",
    body: "We build the assistants and workflow tools your teams will actually use, connected to your knowledge bases and business systems.",
  },
  {
    title: "Testing, deployment & team training",
    body: "We validate accuracy and safety with your team, deploy to production, and train your people so adoption sticks.",
  },
  {
    title: "Ongoing optimization",
    body: "Models improve, your business changes. We tune retrieval, refresh models, and expand tools as your needs grow.",
  },
];

export default function HowItWorks() {
  return (
    <Section
      id="how-it-works"
      label="How It Works"
      title="From strategy to a running private AI system"
      lead="A structured, low-risk path from first conversation to production deployment — with your team in control at every step."
    >
      <ol className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {steps.map((s, i) => (
          <li key={s.title} className="card relative">
            <span className="text-sm font-semibold text-brand-400">
              Step {i + 1}
            </span>
            <h3 className="mt-2 text-base font-semibold text-white">{s.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-mist-300">{s.body}</p>
          </li>
        ))}
      </ol>
    </Section>
  );
}
