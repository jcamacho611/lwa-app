"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import { Logo } from "./brand/Logo";

type NavItem = {
  href: string;
  label: string;
};

type NavbarProps = {
  items: NavItem[];
  rightSlot?: ReactNode;
  showTagline?: boolean;
  compactLogo?: boolean;
};

export default function Navbar({ items, rightSlot, showTagline = false, compactLogo = false }: NavbarProps) {
  const pathname = usePathname();

  return (
    <header className="glass-panel sticky top-4 z-40 rounded-[30px] border-[rgba(217,181,109,0.12)] px-4 py-3 sm:px-5">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Logo compact={compactLogo} showTagline={showTagline} />

        <nav className="order-3 flex w-full gap-2 overflow-x-auto pb-1 md:order-2 md:w-auto md:flex-1 md:justify-center md:pb-0">
          {items.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={[
                  "nav-pill whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium",
                  active ? "nav-pill-active" : "",
                ].join(" ")}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="order-2 flex items-center gap-2 md:order-3">{rightSlot}</div>
      </div>
    </header>
  );
}
