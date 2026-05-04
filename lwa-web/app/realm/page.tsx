import type { Metadata } from "next";
import { PlatformShell } from "../../components/platform/PlatformShell";
import { PlatformCard } from "../../components/platform/PlatformCard";
import { buildPageMetadata } from "../../lib/seo";
import { Sword, Shield, Scroll, Crown } from "lucide-react";

export const metadata: Metadata = buildPageMetadata({
  title: "Game Realm | LWA",
  description: "Enter the Lee-Wuh world. Creator progression system.",
  path: "/realm",
  keywords: ["game realm", "creator progression", "LWA world"],
});

const classes = [
  { name: "Hookwright", icon: Sword, description: "Master of viral hooks" },
  { name: "Captioneer", icon: Scroll, description: "Caption craftsman" },
  { name: "Reframer", icon: Shield, description: "Content strategist" },
  { name: "Trendseer", icon: Crown, description: "Pattern predictor" },
];

export default function RealmPage() {
  return (
    <PlatformShell
      title="Game Realm"
      subtitle="Enter the Lee-Wuh world"
      variant="game"
    >
      {/* Hero Section */}
      <PlatformCard variant="purple" className="mb-6">
        <div className="text-center py-8">
          <h2 className="text-3xl font-bold text-white mb-4">The Signal Realms</h2>
          <p className="text-white/60 max-w-2xl mx-auto">
            A creator progression system where skill earns status. 
            No purchases. Only proof of work.
          </p>
        </div>
      </PlatformCard>

      {/* Classes Grid */}
      <h3 className="text-xl font-semibold text-white mb-4">Creator Classes</h3>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {classes.map((cls) => {
          const Icon = cls.icon;
          return (
            <PlatformCard
              key={cls.name}
              title={cls.name}
              subtitle={cls.description}
              variant="highlight"
              className="text-center"
            >
              <Icon className="h-12 w-12 text-[#C9A24A] mx-auto mb-2" />
            </PlatformCard>
          );
        })}
      </div>

      {/* Factions Section */}
      <h3 className="text-xl font-semibold text-white mt-8 mb-4">The Twelve Factions</h3>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {[
          "Crimson Court", "Black Loom", "Verdant Pact",
          "Iron Choir", "Saffron Wake", "Glass Synod",
        ].map((faction) => (
          <PlatformCard key={faction} variant="default" className="py-3">
            <span className="text-white font-medium">{faction}</span>
          </PlatformCard>
        ))}
      </div>
    </PlatformShell>
  );
}
