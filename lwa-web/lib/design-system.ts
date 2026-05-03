/**
 * LWA Design System v0
 * 
 * Core design constants for the LWA creator operating system.
 * Premium black/gold/purple aesthetic with Lee-Wuh brand integration.
 */

export const DESIGN_SYSTEM = {
  // Colors
  colors: {
    black: "#050505",
    charcoal: "#111016", 
    gold: "#F4C45D",
    deepGold: "#B88422",
    purple: "#8B3DFF",
    violet: "#B56CFF",
    red: "#C92A2A",
    white: "#FFFFFF",
    gray50: "#F5F1E8",
    gray100: "#B8B3A7",
    gray200: "#8F897C",
    gray300: "#7A7568",
  },

  // Typography
  typography: {
    fontFamily: {
      sans: ["Inter", "system-ui", "sans-serif"],
      mono: ["JetBrains Mono", "SF Mono", "monospace"],
    },
    fontSize: {
      xs: "0.75rem",      // 12px
      sm: "0.875rem",     // 14px
      base: "1rem",       // 16px
      lg: "1.125rem",     // 18px
      xl: "1.25rem",      // 20px
      "2xl": "1.5rem",    // 24px
      "3xl": "1.875rem",  // 30px
      "4xl": "2.25rem",   // 36px
      "5xl": "3rem",      // 48px
      "6xl": "3.75rem",   // 60px
    },
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    letterSpacing: {
      tight: "-0.025em",
      normal: "0",
      wide: "0.025em",
      wider: "0.05em",
      widest: "0.1em",
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },

  // Spacing
  spacing: {
    0: "0",
    1: "0.25rem",   // 4px
    2: "0.5rem",    // 8px
    3: "0.75rem",   // 12px
    4: "1rem",      // 16px
    5: "1.25rem",   // 20px
    6: "1.5rem",    // 24px
    8: "2rem",      // 32px
    10: "2.5rem",   // 40px
    12: "3rem",     // 48px
    16: "4rem",     // 64px
    20: "5rem",     // 80px
    24: "6rem",     // 96px
  },

  // Border radius
  borderRadius: {
    none: "0",
    sm: "0.125rem",    // 2px
    base: "0.25rem",   // 4px
    md: "0.375rem",    // 6px
    lg: "0.5rem",     // 8px
    xl: "0.75rem",    // 12px
    "2xl": "1rem",    // 16px
    "3xl": "1.5rem",  // 24px
    full: "9999px",
  },

  // Shadows
  shadows: {
    sm: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    base: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
    md: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    lg: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    xl: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
    "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
    inner: "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)",
    
    // LWA-specific shadows
    gold: "0 0 0 1px rgba(201, 162, 74, 0.4) inset, 0 12px 32px -16px rgba(201, 162, 74, 0.55)",
    purple: "0 0 0 1px rgba(139, 61, 255, 0.4) inset, 0 12px 32px -16px rgba(139, 61, 255, 0.55)",
    cinematic: "0 0 0 1px rgba(201, 162, 74, 0.18), 0 18px 60px -24px rgba(201, 162, 74, 0.35)",
  },

  // Animation
  animation: {
    none: "none",
    spin: "spin 1s linear infinite",
    ping: "ping 1s cubic-bezier(0, 0, 0.2, 1) infinite",
    pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
    bounce: "bounce 1s infinite",
    
    // LWA-specific animations
    "fade-in": "fadeIn 0.5s ease-in-out",
    "slide-up": "slideUp 0.3s ease-out",
    "glow-pulse": "glowPulse 2s ease-in-out infinite",
  },

  // Breakpoints
  breakpoints: {
    sm: "640px",
    md: "768px", 
    lg: "1024px",
    xl: "1280px",
    "2xl": "1536px",
  },

  // Component-specific
  components: {
    // Button styles
    button: {
      primary: {
        background: "bg-[#C9A24A]",
        hover: "hover:bg-[#E9C77B]",
        text: "text-[#1a1407]",
        shadow: "shadow-[0_0_0_1px_rgba(0,0,0,0.4)_inset,0_12px_32px_-16px_rgba(201,162,74,0.55)]",
      },
      secondary: {
        background: "bg-[#1D1D24]",
        hover: "hover:bg-[#24242E]",
        text: "text-[#F5F1E8]",
        ring: "ring-1 ring-[#2E2E38]",
      },
    },

    // Card styles
    card: {
      background: "bg-[#16161B]",
      border: "border-[#23232C]",
      shadow: "shadow-lg",
    },

    // Input styles
    input: {
      background: "bg-[#16161B]",
      border: "border-[#2E2E38]",
      focus: "focus:border-[#C9A24A] focus:ring-[#C9A24A]/20",
    },
  },
} as const;

// CSS custom properties for runtime theming
export const cssVariables = {
  "--color-black": DESIGN_SYSTEM.colors.black,
  "--color-charcoal": DESIGN_SYSTEM.colors.charcoal,
  "--color-gold": DESIGN_SYSTEM.colors.gold,
  "--color-deep-gold": DESIGN_SYSTEM.colors.deepGold,
  "--color-purple": DESIGN_SYSTEM.colors.purple,
  "--color-violet": DESIGN_SYSTEM.colors.violet,
  "--color-red": DESIGN_SYSTEM.colors.red,
  "--color-white": DESIGN_SYSTEM.colors.white,
} as const;
