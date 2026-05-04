"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Clapperboard,
  Gamepad2,
  Store,
  Target,
  Wallet,
  Upload,
  History,
  Settings,
} from "lucide-react";

/**
 * PlatformNavigation - Lee-Wuh Platform Navigation
 * 
 * Connects all 7 core platform routes:
 * - Dashboard (decision command center)
 * - Generate (clip creation)
 * - Game (realm/world)
 * - Marketplace (content market)
 * - Campaigns (management)
 * - Wallet (earnings)
 * - Upload (content ingestion)
 * - History (past work)
 */

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/generate", label: "Generate", icon: Clapperboard },
  { href: "/realm", label: "Game", icon: Gamepad2 },
  { href: "/marketplace", label: "Marketplace", icon: Store },
  { href: "/campaigns", label: "Campaigns", icon: Target },
  { href: "/wallet", label: "Wallet", icon: Wallet },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/history", label: "History", icon: History },
];

export function PlatformNavigation() {
  const pathname = usePathname();

  return (
    <nav className="fixed left-0 top-0 z-50 h-full w-64 border-r border-white/5 bg-[#0A0A0A]/80 backdrop-blur-xl">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#C9A24A] to-[#9333EA]">
          <span className="text-lg font-bold text-white">L</span>
        </div>
        <div>
          <h1 className="text-lg font-bold text-white">LWA</h1>
          <p className="text-xs text-white/40">Lee-Wuh Arts</p>
        </div>
      </div>

      {/* Nav Links */}
      <div className="space-y-1 px-4 py-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200
                ${isActive 
                  ? "bg-gradient-to-r from-[#C9A24A]/20 to-transparent text-[#C9A24A] border-r-2 border-[#C9A24A]" 
                  : "text-white/60 hover:bg-white/5 hover:text-white"
                }
              `}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}
      </div>

      {/* Bottom Section */}
      <div className="absolute bottom-0 left-0 right-0 border-t border-white/5 p-4">
        <Link
          href="/settings"
          className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-white/40 transition-all duration-200 hover:bg-white/5 hover:text-white"
        >
          <Settings className="h-5 w-5" />
          Settings
        </Link>
      </div>
    </nav>
  );
}
