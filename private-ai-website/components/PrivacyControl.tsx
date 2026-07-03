import Section from "./Section";
import Icon, { type IconName } from "./Icon";

const controls: { icon: IconName; title: string; body: string }[] = [
  { icon: "server", title: "Local-first architecture", body: "Inference and document indexing run inside your environment by default — a design choice, not a policy promise." },
  { icon: "shield", title: "Private cloud or on-premise", body: "Deploy on your workstations, your data center, or a private cloud tenancy you control." },
  { icon: "lock", title: "Customer-controlled data", body: "Your documents, embeddings, and logs live on infrastructure you own. Leaving is as simple as keeping your servers." },
  { icon: "key", title: "Role-based access", body: "Permissions decide who can query which knowledge bases and use which tools." },
  { icon: "audit", title: "Audit logs", body: "Every AI interaction is recorded: who asked, which model answered, which sources were used." },
  { icon: "clock", title: "Data retention controls", body: "Retention windows you set — including the ability to purge documents, chats, and logs on your schedule." },
  { icon: "route", title: "Approved cloud routing only", body: "If a task ever justifies a cloud model, it routes there only under rules you approve — never by default." },
  { icon: "check", title: "No default external sharing", body: "No hidden telemetry, no training on your data, no third-party calls you didn't sign off on." },
];

export default function PrivacyControl() {
  return (
    <Section
      id="privacy"
      label="Privacy & Control"
      title="Privacy isn't a feature. It's the architecture."
      lead="We build systems where privacy claims are verifiable: you can see where the models run, where the data lives, and what leaves the building — because in most deployments, nothing does."
      tone="raised"
    >
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {controls.map((c) => (
          <div key={c.title} className="card !p-5">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-500/15 text-brand-400">
              <Icon name={c.icon} className="h-4.5 w-4.5" />
            </span>
            <h3 className="mt-4 text-sm font-semibold text-white">{c.title}</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-mist-400">{c.body}</p>
          </div>
        ))}
      </div>
      <p className="mt-8 max-w-3xl text-sm leading-relaxed text-mist-400">
        A note on honesty: &ldquo;fully private&rdquo; depends on how you deploy.
        Local and on-premise deployments keep everything inside your walls.
        Private-cloud deployments keep data inside your tenancy under your
        cloud agreements. We&rsquo;ll always be precise about which guarantee
        your architecture actually provides.
      </p>
    </Section>
  );
}
