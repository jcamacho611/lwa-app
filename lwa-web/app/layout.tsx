import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "LWA",
    template: "%s · LWA",
  },
  description: "AI clipping engine for ranked short-form outputs, hooks, captions, packaging, and creator workflow.",
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
