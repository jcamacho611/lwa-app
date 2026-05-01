import type { Metadata } from "next";
import CinematicHero from "../components/landing/CinematicHero";
import PathPortal from "../components/landing/PathPortal";
import ClipEnginePreview from "../components/landing/ClipEnginePreview";
import SevenAgentsReveal from "../components/landing/SevenAgentsReveal";
import CouncilSection from "../components/landing/CouncilSection";
import Footer from "../components/landing/Footer";
import { buildPageMetadata } from "../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "LWA — The Creator Engine",
  description:
    "LWA (lee-wuh) is the AI clipping and creator workflow platform. One source in. Best clip first. Rendered proof over vague strategy.",
  path: "/",
  keywords: [
    "lwa",
    "afro-futurist creator engine",
    "ai clipping engine",
    "rendered clips",
    "seven agents",
    "signal relics",
  ],
});

export default function HomePage() {
  return (
    <main className="relative bg-[#0A0A0B] text-[#F5F1E8] min-h-screen overflow-hidden">
      {/* Cinematic stage — pure CSS, zero WebGL, zero JS cost */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 z-0 overflow-hidden"
      >
        <div
          className="absolute -inset-[10%]"
          style={{
            background:
              "radial-gradient(60% 50% at 50% 30%, rgba(201,162,74,0.10), transparent 60%)," +
              "radial-gradient(50% 40% at 80% 70%, rgba(75,58,140,0.12), transparent 65%)," +
              "radial-gradient(120% 80% at 50% 110%, rgba(0,0,0,0.9), transparent 60%)",
            filter: "blur(40px)",
          }}
        />
        <div
          className="absolute inset-0 mix-blend-overlay opacity-50"
          style={{
            backgroundImage:
              "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/><feColorMatrix values='0 0 0 0 0.96 0 0 0 0 0.94 0 0 0 0 0.91 0 0 0 0.06 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>\")",
          }}
        />
      </div>

      <div className="relative z-10">
        <CinematicHero />
        <PathPortal />
        <ClipEnginePreview />
        <SevenAgentsReveal />
        <CouncilSection />
        <Footer />
      </div>
    </main>
  );
}
