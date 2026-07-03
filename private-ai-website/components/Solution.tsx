import Section from "./Section";
import Icon, { type IconName } from "./Icon";

const pillars: { icon: IconName; title: string; body: string }[] = [
  {
    icon: "server",
    title: "Private AI Infrastructure",
    body: "Open-source language models deployed on your machines, your servers, or your private cloud — sized to your workloads, selected for your use cases, and operated under your policies. You choose where inference happens and who can reach it.",
  },
  {
    icon: "wrench",
    title: "Custom Business AI Tools",
    body: "Purpose-built assistants and tools shaped around how your company actually works: contract review support, sales conversation analysis, executive research, reporting. Not a generic chatbot — tools with your context built in.",
  },
  {
    icon: "workflow",
    title: "Secure Knowledge & Workflow Automation",
    body: "Your documents, emails, and operational data indexed privately so AI can answer from your knowledge with citations — and automate the repetitive workflows around it, with access controls and audit trails from day one.",
  },
];

export default function Solution() {
  return (
    <Section
      id="solution"
      label="The Solution"
      title="AI systems your company owns and operates"
      lead="We design and deploy private AI systems powered by local or privately hosted open-source models, customized around each company's documents, workflows, and operational needs. You get the capability of modern AI with the control of internal infrastructure."
    >
      <div className="grid gap-6 lg:grid-cols-3">
        {pillars.map((p) => (
          <div key={p.title} className="card">
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-500/15 text-brand-400">
              <Icon name={p.icon} className="h-6 w-6" />
            </span>
            <h3 className="mt-5 text-lg font-semibold text-white">{p.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-mist-300">{p.body}</p>
          </div>
        ))}
      </div>
    </Section>
  );
}
