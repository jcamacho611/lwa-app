import { PRODUCTION_COUNCIL } from "../../lib/production-council";

export default function CouncilSection() {
  const members = Object.values(PRODUCTION_COUNCIL);

  return (
    <section className="relative py-24 border-t border-[#23232C]">
      <div className="mx-auto max-w-6xl px-6 grid grid-cols-1 lg:grid-cols-12 gap-10">
        <div className="lg:col-span-5">
          <div className="font-mono text-[0.7rem] uppercase tracking-[0.18em] text-[#7A7568]">
            Production Council
          </div>
          <h2 className="mt-2 text-[clamp(2rem,4vw,3.25rem)] font-semibold leading-[1.05] tracking-[-0.015em] text-[#F5F1E8] text-balance">
            The Council builds the system.
            <span className="block text-[#C9A24A]">
              The characters guide the world.
            </span>
          </h2>
          <p className="mt-6 leading-relaxed text-[#B8B3A7]">
            LWA is shipped by people, not by lore. The Seven Agents are the
            in-world voice. The Council is the build crew that wires the
            engine, holds the line on contracts, and keeps rendered proof
            above vague strategy.
          </p>
        </div>

        <ul className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-3">
          {members.map((m) => (
            <li
              key={m.id}
              className="rounded-[14px] p-4 bg-[#16161B] ring-1 ring-[#23232C]"
            >
              <div className="font-mono text-[0.65rem] uppercase tracking-[0.18em] text-[#7A7568]">
                {m.realTitle}
              </div>
              <div className="mt-1 text-xl font-semibold tracking-[-0.01em] text-[#F5F1E8]">
                {m.mythicTitle}
              </div>
              <p className="mt-1 text-sm leading-relaxed text-[#B8B3A7]">
                {m.owns}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
