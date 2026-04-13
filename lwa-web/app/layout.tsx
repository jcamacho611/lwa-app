import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IWA",
  description: "Turn videos into viral clip packs with AI-powered ranking and packaging.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
