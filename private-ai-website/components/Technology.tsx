import Section from "./Section";

const tech = [
  {
    title: "Open-source language models",
    body: "Proven open models (Llama, Qwen, Mistral families and others) selected per task — fast models for quick work, stronger models for reasoning.",
  },
  {
    title: "Local inference",
    body: "Models run on your hardware using efficient runtimes, so prompts and answers never cross the public internet.",
  },
  {
    title: "Private-cloud deployment",
    body: "When you need more scale, the same stack runs in your own cloud tenancy — isolated, access-controlled, and yours.",
  },
  {
    title: "Retrieval-Augmented Generation",
    body: "The AI answers from your documents, quoting its sources — which keeps answers grounded and reviewable.",
  },
  {
    title: "Vector search",
    body: "Your knowledge is indexed for meaning, not just keywords, so the right context is found even when wording differs.",
  },
  {
    title: "Model routing",
    body: "Each task is matched to the right model automatically — small and fast where possible, larger where quality demands it.",
  },
  {
    title: "Workflow agents",
    body: "Multi-step assistants that can read, extract, draft, and hand off — following processes you define.",
  },
  {
    title: "Secure APIs & integrations",
    body: "A clean internal API connects the AI to the tools you already use — CRM, email, document stores — with authentication and logging.",
  },
];

export default function Technology() {
  return (
    <Section
      id="technology"
      label="Technology"
      title="Serious engineering, explained simply"
      lead="You don't need to know the internals to trust the system — but you should know what it's made of. Every component below is production-proven and runs inside your boundary."
    >
      <div className="grid gap-x-10 gap-y-8 md:grid-cols-2">
        {tech.map((t) => (
          <div key={t.title} className="border-l-2 border-brand-500/40 pl-5">
            <h3 className="text-base font-semibold text-white">{t.title}</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-mist-300">{t.body}</p>
          </div>
        ))}
      </div>
    </Section>
  );
}
