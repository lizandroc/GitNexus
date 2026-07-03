import Section from "./Section";
import ContactForm from "./ContactForm";

export default function ContactSection() {
  return (
    <Section
      id="contact"
      label="Contact"
      title="Start the conversation"
      lead="Tell us a little about your company and what you want AI to do. We'll reply within two business days with honest guidance on whether — and how — private AI fits."
    >
      <div className="grid gap-10 lg:grid-cols-5">
        <div className="lg:col-span-2">
          <div className="card">
            <h3 className="text-base font-semibold text-white">What happens next</h3>
            <ol className="mt-4 space-y-3 text-sm leading-relaxed text-mist-300">
              <li>1. We review your goals and privacy constraints.</li>
              <li>2. We schedule a 30-minute strategy call.</li>
              <li>3. You receive a written recommendation — use cases, models, deployment path — whether or not we work together.</li>
            </ol>
            <p className="mt-6 border-t border-ink-700 pt-4 text-xs leading-relaxed text-mist-500">
              Anything you share here is treated as confidential and is never
              used to train models or shared with third parties.
            </p>
          </div>
        </div>
        <div className="lg:col-span-3">
          <ContactForm />
        </div>
      </div>
    </Section>
  );
}
