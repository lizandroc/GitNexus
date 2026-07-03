export default function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div className="hero-grid absolute inset-0" />
      <div className="container-content relative py-24 text-center md:py-36">
        <p className="mx-auto inline-flex items-center gap-2 rounded-full border border-ink-700 bg-ink-900/70 px-4 py-1.5 text-xs font-medium text-mist-300">
          <span className="h-1.5 w-1.5 rounded-full bg-brand-400" />
          Private AI infrastructure · Local &amp; private-cloud deployment
        </p>

        <h1 className="mx-auto mt-6 max-w-4xl text-4xl font-semibold leading-tight tracking-tight text-white md:text-6xl">
          Private AI Infrastructure for Companies That Cannot Risk Their Data
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-mist-300">
          Deploy local or private-cloud AI systems that power internal tools,
          automate workflows, and keep sensitive business knowledge under your
          control — built on open-source models you own and operate.
        </p>

        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <a href="#contact" className="btn-primary">
            Book a Private AI Strategy Call
          </a>
          <a href="#use-cases" className="btn-secondary">
            See Use Cases
          </a>
        </div>

        <div className="mx-auto mt-16 grid max-w-3xl grid-cols-1 gap-px overflow-hidden rounded-2xl border border-ink-700 bg-ink-700 sm:grid-cols-3">
          {[
            ["Your hardware or private cloud", "Deployment you control"],
            ["Open-source models", "No black-box dependency"],
            ["Local-first by default", "Data stays inside"],
          ].map(([title, sub]) => (
            <div key={title} className="bg-ink-900/90 px-6 py-5 text-left">
              <p className="text-sm font-semibold text-white">{title}</p>
              <p className="mt-1 text-xs text-mist-400">{sub}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
