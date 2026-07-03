import Section from "./Section";
import Icon from "./Icon";

const benefits = [
  "More control over sensitive data and where it lives",
  "Lower long-term AI operating costs — no per-token metering on your own hardware",
  "Custom AI tools built around real workflows, not generic chat",
  "Better internal knowledge access for every team",
  "Faster research, document review, and reporting",
  "Improved sales and operations productivity",
  "Reduced dependence on any single AI vendor",
  "A stronger compliance and audit posture",
  "Internal AI infrastructure that scales with the business",
];

export default function Benefits() {
  return (
    <Section
      id="benefits"
      label="Enterprise Benefits"
      title="What ownership buys you"
      lead="Beyond privacy, owning your AI stack changes the economics and the strategy: costs flatten, capabilities compound, and your data advantage stays yours."
      tone="raised"
    >
      <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {benefits.map((b) => (
          <li key={b} className="flex items-start gap-3 rounded-xl border border-ink-700 bg-ink-900/70 px-5 py-4">
            <span className="mt-0.5 text-brand-400">
              <Icon name="check" className="h-5 w-5" />
            </span>
            <span className="text-sm leading-relaxed text-mist-200">{b}</span>
          </li>
        ))}
      </ul>
    </Section>
  );
}
