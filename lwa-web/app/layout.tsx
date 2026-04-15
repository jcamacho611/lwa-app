import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "LWA",
    template: "%s · LWA",
  },
  description: "Turn one long-form source into ranked short-form clips, hooks, captions, timestamps, packaging angles, and workflow-ready outputs.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/favicon.svg",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-bgDark text-white antialiased">{children}</body>
    </html>
  );
}
