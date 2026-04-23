"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import { Logo } from "./brand/Logo";
import { rewriteSurfaceLabel } from "../lib/brand-voice";

type NavItem = {
  href: string;
  label: string;
};

type NavbarProps = {
  items: NavItem[];
  rightSlot?: ReactNode;
  showTagline?: boolean;
  compactLogo?: boolean;
  variant?: "home" | "workspace";
};

export default function Navbar({
  items,
  rightSlot,
  showTagline = false,
  compactLogo = false,
  variant = "workspace",
}: NavbarProps) {
  const pathname = usePathname();
  const primaryItems = ["/generate", "/dashboard", "/campaigns", "/wallet"]
    .map((href) => items.find((item) => item.href === href))
    .filter(Boolean) as NavItem[];
  const visibleItems = primaryItems.length ? primaryItems : items.slice(0, 4);

  return (
    <header
      className={[
        "glass-panel sticky top-4 z-40 rounded-[28px] border-white/8 px-4 py-3 sm:px-5",
        variant === "home" ? "navbar-home" : "navbar-workspace",
      ].join(" ")}
    >
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Logo compact={compactLogo} showTagline={showTagline} animated={variant === "home"} />

        <nav className="order-3 flex w-full gap-1.5 overflow-x-auto pb-1 md:order-2 md:w-auto md:flex-1 md:justify-center md:pb-0">
          {visibleItems.map((item) => {
            const active = pathname === item.href;
            const label = item.href === "/dashboard" ? "Queue" : rewriteSurfaceLabel(item.label);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={[
                  "nav-pill whitespace-nowrap rounded-full px-3.5 py-2 text-sm font-medium",
                  active ? "nav-pill-active" : "",
                ].join(" ")}
              >
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="order-2 flex items-center gap-2 md:order-3">{rightSlot}</div>
      </div>
    </header>
  );
}
