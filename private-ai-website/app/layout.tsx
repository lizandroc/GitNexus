import type { Metadata } from "next";
import "./globals.css";

const siteName = "Sovereign AI Systems";
const siteDescription =
  "We help enterprises design, deploy, and own private AI systems — local and private-cloud open-source LLMs, document intelligence, and workflow automation, with sensitive data kept under your control.";

export const metadata: Metadata = {
  metadataBase: new URL("https://www.sovereignaisystems.example"),
  title: {
    default: `${siteName} — Private AI Infrastructure for Enterprises`,
    template: `%s — ${siteName}`,
  },
  description: siteDescription,
  keywords: [
    "private AI",
    "local LLM",
    "on-premise AI",
    "private cloud AI",
    "enterprise AI infrastructure",
    "RAG",
    "document intelligence",
    "AI workflow automation",
    "data sovereignty",
  ],
  openGraph: {
    title: `${siteName} — Own Your AI Infrastructure`,
    description: siteDescription,
    type: "website",
    siteName,
  },
  twitter: {
    card: "summary_large_image",
    title: `${siteName} — Private AI Infrastructure for Enterprises`,
    description: siteDescription,
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
