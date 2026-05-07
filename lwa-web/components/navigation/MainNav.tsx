"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Clapperboard, 
  Gamepad2, 
  Sparkles,
  Store, 
  Target, 
  History, 
  Wallet,
  Upload,
  Command
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/generate", label: "Generate", icon: Clapperboard },
  { href: "/demo", label: "Demo", icon: Sparkles },
  { href: "/realm", label: "Game", icon: Gamepad2 },
  { href: "/marketplace", label: "Market", icon: Store },
  { href: "/campaigns", label: "Campaigns", icon: Target },
  { href: "/history", label: "History", icon: History },
  { href: "/wallet", label: "Wallet", icon: Wallet },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/command-center", label: "Command", icon: Command },
];

export function MainNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed left-0 top-0 h-full w-64 bg-[#1A1A1A] border-r border-white/10 p-4">
      <div className="mb-8">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-xl font-bold text-[#C9A24A]">LWA</span>
        </Link>
      </div>

      <ul className="space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
          const Icon = item.icon;

          return (
            <li key={item.href}>
              <Link
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                  isActive
                    ? "bg-[#C9A24A]/20 text-[#C9A24A]"
                    : "text-white/60 hover:bg-white/5 hover:text-white"
                }`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
