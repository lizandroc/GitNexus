type IconProps = { name: IconName; className?: string };

export type IconName =
  | "shield"
  | "server"
  | "wrench"
  | "workflow"
  | "document"
  | "chart"
  | "lock"
  | "key"
  | "audit"
  | "clock"
  | "route"
  | "api"
  | "search"
  | "users"
  | "check"
  | "arrow";

const paths: Record<IconName, JSX.Element> = {
  shield: (
    <path d="M12 3l7 3v5c0 4.5-3 8.5-7 10-4-1.5-7-5.5-7-10V6l7-3z" />
  ),
  server: (
    <>
      <rect x="4" y="4" width="16" height="7" rx="1.5" />
      <rect x="4" y="13" width="16" height="7" rx="1.5" />
      <path d="M8 7.5h.01M8 16.5h.01" />
    </>
  ),
  wrench: (
    <path d="M14.7 6.3a4 4 0 00-5.4 5.4L4 17v3h3l5.3-5.3a4 4 0 005.4-5.4l-2.9 2.9-2.1-2.1 2.9-2.9z" />
  ),
  workflow: (
    <>
      <rect x="3" y="3" width="6" height="6" rx="1" />
      <rect x="15" y="15" width="6" height="6" rx="1" />
      <path d="M9 6h5a2 2 0 012 2v7" />
    </>
  ),
  document: (
    <>
      <path d="M7 3h7l4 4v14H7z" />
      <path d="M14 3v4h4M10 12h5M10 16h5" />
    </>
  ),
  chart: (
    <path d="M4 20V10m6 10V4m6 16v-7m4 7H2" />
  ),
  lock: (
    <>
      <rect x="5" y="11" width="14" height="9" rx="1.5" />
      <path d="M8 11V8a4 4 0 018 0v3" />
    </>
  ),
  key: (
    <path d="M14 10a4 4 0 10-4 4l-6 6v-3h3l1-1v-2h2l1-1a4 4 0 003-3z" />
  ),
  audit: (
    <>
      <path d="M6 3h12v18H6z" />
      <path d="M9 8h6M9 12h6M9 16h3" />
    </>
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7v5l3 2" />
    </>
  ),
  route: (
    <>
      <circle cx="5" cy="19" r="2" />
      <circle cx="19" cy="5" r="2" />
      <path d="M7 19h7a4 4 0 004-4V7" />
    </>
  ),
  api: (
    <path d="M8 8l-4 4 4 4m8-8l4 4-4 4M13 5l-2 14" />
  ),
  search: (
    <>
      <circle cx="10.5" cy="10.5" r="6.5" />
      <path d="M15.5 15.5L21 21" />
    </>
  ),
  users: (
    <>
      <circle cx="9" cy="8" r="3.5" />
      <path d="M3 20a6 6 0 0112 0M16 5a3.5 3.5 0 010 7M21 20a6 6 0 00-5-5.9" />
    </>
  ),
  check: <path d="M4 12.5l5 5L20 6.5" />,
  arrow: <path d="M5 12h14m-6-6l6 6-6 6" />,
};

export default function Icon({ name, className = "h-5 w-5" }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  );
}
