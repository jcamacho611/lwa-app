"use client";

/**
 * LeeWuhWorldBackground - Atmospheric World Layer
 * 
 * Design Philosophy:
 * - World exists as mood, not content
 * - Purple/gold energy and aura
 * - Blurred, darkened, atmospheric
 * - Lee-Wuh character presence at edges
 * - Never blocks foreground UI
 * 
 * Based on Lee-Wuh image: world, aura, purple/gold energy
 * NOT the text/caption-heavy poster layout
 */

interface LeeWuhWorldBackgroundProps {
  variant?: "default" | "dashboard" | "generate" | "game" | "marketplace";
}

export function LeeWuhWorldBackground({ variant = "default" }: LeeWuhWorldBackgroundProps) {
  // Variant-based color intensities
  const variants = {
    default: { gold: 0.3, purple: 0.2, blue: 0.1 },
    dashboard: { gold: 0.4, purple: 0.3, blue: 0.2 },
    generate: { gold: 0.5, purple: 0.4, blue: 0.2 },
    game: { gold: 0.6, purple: 0.5, blue: 0.3 },
    marketplace: { gold: 0.35, purple: 0.25, blue: 0.15 },
  };

  const intensity = variants[variant];

  return (
    <>
      {/* Base dark layer */}
      <div className="fixed inset-0 z-0 bg-[#0A0A0A]" />
      
      {/* Purple/Gold Aura Gradient */}
      <div 
        className="fixed inset-0 z-[1]"
        style={{
          background: `
            radial-gradient(ellipse 80% 50% at 50% 0%, rgba(147, 51, 234, ${intensity.purple}) 0%, transparent 50%),
            radial-gradient(ellipse 60% 40% at 80% 80%, rgba(201, 162, 74, ${intensity.gold}) 0%, transparent 40%),
            radial-gradient(ellipse 40% 30% at 20% 60%, rgba(59, 130, 246, ${intensity.blue}) 0%, transparent 30%)
          `,
        }}
      />
      
      {/* Lee-Wuh Energy Grid (subtle) */}
      <div 
        className="fixed inset-0 z-[2] opacity-[0.03]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(201, 162, 74, 0.5) 1px, transparent 1px),
            linear-gradient(90deg, rgba(201, 162, 74, 0.5) 1px, transparent 1px)
          `,
          backgroundSize: '100px 100px',
        }}
      />
      
      {/* Character Presence - Bottom Right (subtle glow) */}
      <div 
        className="fixed bottom-0 right-0 z-[3] pointer-events-none hidden lg:block"
        style={{
          width: '300px',
          height: '400px',
          transform: 'translate(20%, 30%)',
        }}
      >
        {/* Lee-Wuh silhouette/aura glow */}
        <div 
          className="absolute inset-0"
          style={{
            background: `
              radial-gradient(ellipse 50% 70% at 60% 40%, rgba(201, 162, 74, 0.15) 0%, transparent 60%),
              radial-gradient(ellipse 40% 60% at 70% 50%, rgba(147, 51, 234, 0.1) 0%, transparent 50%)
            `,
            animation: 'leeWuhPulse 6s ease-in-out infinite',
          }}
        />
        
        {/* Gold accent ring */}
        <div 
          className="absolute bottom-1/4 left-1/4 w-32 h-32 rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(201, 162, 74, 0.2) 0%, transparent 70%)',
            filter: 'blur(20px)',
            animation: 'leeWuhGlow 4s ease-in-out infinite alternate',
          }}
        />
      </div>
      
      {/* Top-left energy accent */}
      <div 
        className="fixed top-0 left-0 z-[3] pointer-events-none"
        style={{
          width: '200px',
          height: '200px',
          background: 'radial-gradient(circle at 30% 30%, rgba(147, 51, 234, 0.1) 0%, transparent 60%)',
        }}
      />
      
      {/* Vignette overlay for depth */}
      <div 
        className="fixed inset-0 z-[4] pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 80% 80% at 50% 50%, transparent 0%, rgba(10, 10, 10, 0.4) 100%)',
        }}
      />
      
      {/* Styles */}
      <style jsx>{`
        @keyframes leeWuhPulse {
          0%, 100% { opacity: 0.8; transform: translate(20%, 30%) scale(1); }
          50% { opacity: 1; transform: translate(20%, 30%) scale(1.05); }
        }
        @keyframes leeWuhGlow {
          0% { opacity: 0.5; transform: scale(1); }
          100% { opacity: 0.8; transform: scale(1.2); }
        }
      `}</style>
    </>
  );
}
