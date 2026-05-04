"use client";

import { useState, useEffect } from "react";

export type LeeWuhMood = "idle" | "analyzing" | "rendering" | "complete" | "victory" | "error" | "helping" | "focused" | "confident" | "playful";

interface LeeWuhCharacterProps {
  mood?: LeeWuhMood;
  size?: "sm" | "md" | "lg" | "xl";
  showMessage?: boolean;
  customMessage?: string;
  onClick?: () => void;
  className?: string;
}

const moodConfig: Record<LeeWuhMood, { emoji: string; animation: string; color: string; defaultMessage: string }> = {
  idle: {
    emoji: "🦁",
    animation: "animate-pulse",
    color: "#C9A24A",
    defaultMessage: "Ready to create. Feed me a source.",
  },
  analyzing: {
    emoji: "🧠",
    animation: "animate-bounce",
    color: "#6D3BFF",
    defaultMessage: "Analyzing content... finding the best moments.",
  },
  rendering: {
    emoji: "⚡",
    animation: "animate-spin",
    color: "#00D9FF",
    defaultMessage: "Rendering your clips... almost there.",
  },
  complete: {
    emoji: "✨",
    animation: "animate-pulse",
    color: "#C9A24A",
    defaultMessage: "Done! Your clips are ready.",
  },
  victory: {
    emoji: "🏆",
    animation: "animate-bounce",
    color: "#FFD700",
    defaultMessage: "Epic work! High engagement predicted.",
  },
  error: {
    emoji: "💫",
    animation: "animate-pulse",
    color: "#FF6B35",
    defaultMessage: "Hmm, something went wrong. Try again?",
  },
  helping: {
    emoji: "💡",
    animation: "animate-pulse",
    color: "#E9C77B",
    defaultMessage: "Here's what I recommend...",
  },
  focused: {
    emoji: "🎯",
    animation: "animate-pulse",
    color: "#00D9FF",
    defaultMessage: "Locked in. Let's get this done.",
  },
  confident: {
    emoji: "😎",
    animation: "animate-bounce",
    color: "#C9A24A",
    defaultMessage: "I know exactly what to do.",
  },
  playful: {
    emoji: "🎮",
    animation: "animate-bounce",
    color: "#6D3BFF",
    defaultMessage: "Let's have some fun with this!",
  },
};

const sizeConfig = {
  sm: { container: "w-12 h-12", emoji: "text-2xl", badge: "w-3 h-3" },
  md: { container: "w-16 h-16", emoji: "text-3xl", badge: "w-4 h-4" },
  lg: { container: "w-24 h-24", emoji: "text-5xl", badge: "w-5 h-5" },
  xl: { container: "w-32 h-32", emoji: "text-6xl", badge: "w-6 h-6" },
};

export function LeeWuhCharacter({
  mood = "idle",
  size = "md",
  showMessage = true,
  customMessage,
  onClick,
  className = "",
}: LeeWuhCharacterProps) {
  const config = moodConfig[mood];
  const sizeStyles = sizeConfig[size];
  const [displayMessage, setDisplayMessage] = useState(customMessage || config.defaultMessage);

  useEffect(() => {
    setDisplayMessage(customMessage || config.defaultMessage);
  }, [mood, customMessage, config.defaultMessage]);

  return (
    <div className={`flex flex-col items-center gap-3 ${className}`}>
      {/* Character Container */}
      <div
        onClick={onClick}
        className={`
          relative ${sizeStyles.container} 
          rounded-full flex items-center justify-center
          cursor-pointer transition-all duration-300
          hover:scale-110 active:scale-95
          ${onClick ? "hover:ring-4 hover:ring-[#C9A24A]/30" : ""}
        `}
        style={{
          background: `radial-gradient(circle at 30% 30%, ${config.color}40, ${config.color}20, transparent)`,
          boxShadow: `0 0 30px ${config.color}30, inset 0 0 20px ${config.color}10`,
        }}
      >
        {/* Aura Ring */}
        <div
          className={`absolute inset-0 rounded-full border-2 ${config.animation}`}
          style={{
            borderColor: `${config.color}50`,
            animationDuration: mood === "analyzing" ? "1s" : mood === "rendering" ? "2s" : "3s",
          }}
        />
        
        {/* Character Emoji */}
        <span className={`${sizeStyles.emoji} ${config.animation}`} style={{ animationDuration: "2s" }}>
          {config.emoji}
        </span>

        {/* Status Badge */}
        <div
          className={`absolute -top-1 -right-1 ${sizeStyles.badge} rounded-full border-2 border-black`}
          style={{ backgroundColor: config.color }}
        />
      </div>

      {/* Message Bubble */}
      {showMessage && (
        <div
          className="max-w-xs rounded-2xl px-4 py-3 text-center"
          style={{
            background: `linear-gradient(135deg, ${config.color}20, ${config.color}10)`,
            border: `1px solid ${config.color}30`,
          }}
        >
          <p className="text-sm text-white/90 font-medium">{displayMessage}</p>
        </div>
      )}
    </div>
  );
}

// Compact version for small spaces
export function LeeWuhAvatar({ mood = "idle", size = "sm" }: { mood?: LeeWuhMood; size?: "xs" | "sm" | "md" }) {
  const config = moodConfig[mood];
  const sizeClasses = {
    xs: "w-6 h-6 text-base",
    sm: "w-8 h-8 text-lg",
    md: "w-10 h-10 text-xl",
  };

  return (
    <div
      className={`${sizeClasses[size]} rounded-full flex items-center justify-center`}
      style={{
        background: `radial-gradient(circle, ${config.color}30, transparent)`,
        boxShadow: `0 0 15px ${config.color}20`,
      }}
    >
      {config.emoji}
    </div>
  );
}

// Loading state wrapper
export function LeeWuhLoading({ message = "Lee-Wuh is thinking..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center gap-4 p-8">
      <LeeWuhCharacter mood="analyzing" size="lg" showMessage={false} />
      <p className="text-white/60 text-sm animate-pulse">{message}</p>
    </div>
  );
}

// Guide/helper tooltip
export function LeeWuhGuide({
  tip,
  position = "bottom",
  children
}: {
  tip: string;
  position?: "top" | "bottom" | "left" | "right";
  children: React.ReactNode;
}) {
  const [showTip, setShowTip] = useState(false);

  const positionClasses = {
    top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
    left: "right-full top-1/2 -translate-y-1/2 mr-2",
    right: "left-full top-1/2 -translate-y-1/2 ml-2",
  };

  return (
    <div
      className="relative inline-block"
      onMouseEnter={() => setShowTip(true)}
      onMouseLeave={() => setShowTip(false)}
    >
      {children}

      {showTip && (
        <div className={`absolute ${positionClasses[position]} z-50 w-64`}>
          <div className="flex items-start gap-2 rounded-xl bg-[#16161B] border border-[#C9A24A]/30 p-3 shadow-lg">
            <LeeWuhAvatar mood="helping" size="xs" />
            <p className="text-xs text-white/80">{tip}</p>
          </div>
        </div>
      )}
    </div>
  );
}

// Large mascot card for prominent display
export function LeeWuhMascotCard({
  mood = "idle",
  title = "Lee-Wuh",
  message,
  cta = "Your AI clipping mascot is watching the signal.",
  className = "",
}: {
  mood?: LeeWuhMood;
  title?: string;
  message?: string;
  cta?: string;
  className?: string;
}) {
  const config = moodConfig[mood];

  return (
    <div
      className={`relative overflow-hidden rounded-[32px] border border-[#C9A24A]/25 bg-[#09090d] p-5 shadow-2xl shadow-black/30 ${className}`}
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_15%,rgba(201,162,74,0.24),transparent_34%),radial-gradient(circle_at_80%_10%,rgba(109,59,255,0.18),transparent_30%)]" />

      <div className="relative z-10 grid gap-5 md:grid-cols-[0.8fr_1.2fr] md:items-center">
        <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-black/35">
          <img
            src="/brand/lee-wuh-hero-16x9.svg"
            alt="Lee-Wuh LWA mascot"
            className="aspect-video w-full object-cover"
            onError={(event) => {
              event.currentTarget.style.display = "none";
            }}
          />
          <div className="absolute bottom-3 left-3 rounded-full border border-[#C9A24A]/30 bg-black/70 px-3 py-1 text-xs font-bold text-[#E9C77B]">
            {config.emoji} {mood}
          </div>
        </div>

        <div>
          <p className="text-xs font-black uppercase tracking-[0.24em] text-[#E9C77B]/80">
            LWA Mascot
          </p>
          <h3 className="mt-2 text-3xl font-black text-white">{title}</h3>
          <p className="mt-3 text-sm leading-7 text-white/66">
            {message || config.defaultMessage}
          </p>
          <p className="mt-4 rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-sm font-semibold leading-6 text-white/78">
            {cta}
          </p>
        </div>
      </div>
    </div>
  );
}
