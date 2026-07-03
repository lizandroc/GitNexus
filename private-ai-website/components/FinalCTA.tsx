export default function FinalCTA() {
  return (
    <section className="relative overflow-hidden border-y border-ink-800 bg-ink-900/60">
      <div className="hero-grid absolute inset-0" />
      <div className="container-content relative py-20 text-center md:py-28">
        <h2 className="mx-auto max-w-3xl text-3xl font-semibold tracking-tight text-white md:text-5xl">
          Build a private AI system your company actually owns.
        </h2>
        <p className="mx-auto mt-5 max-w-xl text-base leading-relaxed text-mist-300">
          One conversation is enough to map your highest-value use case and the
          right deployment path. No pitch deck, no obligation.
        </p>
        <div className="mt-9 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <a href="#contact" className="btn-primary">
            Schedule a Strategy Call
          </a>
          <a href="#contact" className="btn-secondary">
            Request an AI Infrastructure Blueprint
          </a>
        </div>
      </div>
    </section>
  );
}
