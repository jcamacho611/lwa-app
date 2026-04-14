import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IWA",
  description: "Turn videos into viral clips with AI-powered packaging in seconds.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-bgDark text-white">{children}</body>
    </html>
  );
}
