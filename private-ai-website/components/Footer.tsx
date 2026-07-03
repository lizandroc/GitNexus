import Icon from "./Icon";

export default function Footer() {
  return (
    <footer className="border-t border-ink-800 py-12">
      <div className="container-content flex flex-col items-start justify-between gap-8 md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-500/15 text-brand-400">
              <Icon name="shield" className="h-4 w-4" />
            </span>
            <span className="text-sm font-semibold text-white">Sovereign AI Systems</span>
          </div>
          <p className="mt-3 max-w-sm text-xs leading-relaxed text-mist-500">
            Private AI infrastructure, custom business tools, and secure
            knowledge automation — built on open-source models you own.
          </p>
        </div>
        <nav className="flex flex-wrap gap-x-8 gap-y-3 text-sm text-mist-400">
          <a href="#solution" className="hover:text-white">What We Do</a>
          <a href="#use-cases" className="hover:text-white">Use Cases</a>
          <a href="#privacy" className="hover:text-white">Privacy</a>
          <a href="#packages" className="hover:text-white">Engagements</a>
          <a href="#contact" className="hover:text-white">Contact</a>
        </nav>
      </div>
      <div className="container-content mt-10 border-t border-ink-800 pt-6 text-xs text-mist-500">
        © {new Date().getFullYear()} Sovereign AI Systems. All rights reserved.
        Placeholder branding — replace with final company details.
      </div>
    </footer>
  );
}
