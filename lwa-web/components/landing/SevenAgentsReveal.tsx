import { getAllLwaAgents } from "../../lib/lwa-agents";

export default function SevenAgentsReveal() {
  const agents = getAllLwaAgents();

  return (
    <section className="relative py-24 border-t border-[#23232C]">
      <div className="mx-auto max-w-6xl px-6">
        <div className="font-mono text-[0.7rem] uppercase tracking-[0.18em] text-[#7A7568]">
          The Realm
        </div>
        <h2 className="mt-2 text-[clamp(2rem,4vw,3.25rem)] font-semibold leading-[1.05] tracking-[-0.015em] text-[#F5F1E8] text-balance">
          Seven agents guide the work.
          <span className="block text-[#B8B3A7]">
            Tomorrow, you train your own on top of them.
          </span>
        </h2>

        <p className="mt-4 max-w-2xl text-sm leading-relaxed text-[#B8B3A7]">
          African / Black anime / Afro-futurist mythic sci-fi character
          foundation. Each agent stewards a layer of the creator workflow.
          Avatar editor, payouts, NFTs, and game economy are{" "}
          <span className="text-[#F5F1E8]/80">not live</span> — these are the
          structural roots for what ships next.
        </p>

        <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {agents.map((agent) => (
            <article
              key={agent.id}
              className="rounded-[14px] p-5 bg-[#16161B] ring-1 ring-[#23232C] transition-colors duration-200 hover:ring-[#C9A24A]/30"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-[0.65rem] uppercase tracking-[0.18em] text-[#7A7568]">
                  {agent.title}
                </span>
                <span className="font-mono text-[0.65rem] text-[#C9A24A] uppercase tracking-[0.14em]">
                  {agent.questRole ?? "guide"}
                </span>
              </div>
              <h3 className="mt-4 text-2xl font-semibold tracking-[-0.01em] text-[#F5F1E8]">
                {agent.name}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-[#B8B3A7] italic">
                {agent.tagline}
              </p>
              <p className="mt-3 text-xs leading-relaxed text-[#7A7568]">
                {agent.productArea}
              </p>
              <div className="mt-4 flex items-center justify-between text-[0.65rem] font-mono uppercase tracking-[0.16em] text-[#7A7568]">
                <span>Future base model</span>
                <span className="text-[#5BA88A]">customizable</span>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
