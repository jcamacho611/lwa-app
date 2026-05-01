import Link from "next/link";

const links: ReadonlyArray<{ href: string; label: string; external?: boolean }> = [
  { href: "/generate", label: "Generate" },
  { href: "/realm", label: "Realm" },
  { href: "/opportunities", label: "Opportunities" },
  { href: "/marketplace", label: "Marketplace" },
  { href: "/proof", label: "Proof" },
  { href: "https://whop.com/lwa-app/lwa-ai-content-repurposer/", label: "Whop", external: true },
] as const;

export default function Footer() {
  return (
    <footer className="border-t border-[#23232C] py-12 mt-16">
      <div className="mx-auto max-w-6xl px-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
        <div>
          <div className="text-2xl font-semibold tracking-[-0.01em] text-[#F5F1E8]">
            LWA{" "}
            <span className="ml-2 inline-flex items-baseline gap-1.5 px-2.5 py-1 rounded-full bg-[#C9A24A]/8 text-[#E9C77B] ring-1 ring-[#C9A24A]/20 font-mono text-[0.72rem] tracking-[0.05em] align-middle">
              lee-wuh
            </span>
          </div>
          <p className="mt-1 text-sm text-[#7A7568]">
            The Council builds the system. The characters guide the world.
          </p>
        </div>

        <nav className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-[#B8B3A7]">
          {links.map((link) =>
            link.external ? (
              <a
                key={link.href}
                href={link.href}
                target="_blank"
                rel="noreferrer"
                className="transition-colors duration-200 hover:text-[#F5F1E8]"
              >
                {link.label}
              </a>
            ) : (
              <Link
                key={link.href}
                href={link.href}
                className="transition-colors duration-200 hover:text-[#F5F1E8]"
              >
                {link.label}
              </Link>
            ),
          )}
        </nav>
      </div>

      <div className="mx-auto max-w-6xl px-6 mt-8">
        <p className="text-xs leading-relaxed text-[#7A7568]">
          No guaranteed virality or income claims. No live marketplace
          payouts, live social posting, or live blockchain economy. Marketplace
          participation is application-based and subject to approval. All
          investment, equity, crypto, and revenue-share discussions require
          legal/compliance review before any transaction.
        </p>
      </div>
    </footer>
  );
}
