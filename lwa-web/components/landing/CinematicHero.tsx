import { LeeWuhHero } from "../brand/LeeWuhHero";

export default function CinematicHero() {
  return (
    <section className="relative min-h-[88vh] flex items-center bg-[#0A0A0B]">
      {/* Cinematic background effects */}
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

      {/* Lee-Wuh Hero - the main content */}
      <div className="relative z-10">
        <LeeWuhHero />
      </div>
    </section>
  );
}
