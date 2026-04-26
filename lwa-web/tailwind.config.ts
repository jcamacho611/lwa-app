import type { Config } from 'tailwindcss';
import { tokens } from './lib/design-tokens';

const config: Config = {
  darkMode: "class",
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        neonPurple: tokens.colors.goldDim,
        neonBlue: tokens.colors.goldDim,
        neonPink: tokens.colors.goldBorder,
        neonGlow: tokens.colors.goldBright,
        neonCyan: tokens.colors.gold,
        brightCyan: tokens.colors.goldBright,
        accentCrimson: tokens.colors.danger,
        accentWine: tokens.colors.bgElev,
        bgDark: tokens.colors.bg,
        bgCard: tokens.colors.bgCard,
        bgPanel: tokens.colors.bgElev,
        bgGlass: tokens.colors.glass,
        ink: tokens.colors.ink,
        subtext: tokens.colors.inkMid,
        muted: tokens.colors.inkFaint,
        accent: tokens.colors.gold,
        accentSoft: tokens.colors.goldBright,
        accentBlue: tokens.colors.gold,
        accentPink: tokens.colors.goldBright,
        surfaceLine: tokens.colors.divider,
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-hero': 'linear-gradient(135deg, var(--bg) 0%, var(--bg-elev) 45%, var(--bg-card) 100%)',
        'hero-radial': 'radial-gradient(circle at 16% 12%, var(--gold-dim), transparent 24%), radial-gradient(circle at 82% 18%, var(--gold-border), transparent 26%), radial-gradient(circle at 68% 78%, var(--gold-dim), transparent 22%), linear-gradient(180deg, var(--bg) 0%, var(--bg-elev) 48%, var(--bg) 100%)',
        'mesh-grid': 'linear-gradient(var(--surface-inset-strong) 1px, transparent 1px), linear-gradient(90deg, var(--surface-inset-strong) 1px, transparent 1px)',
      },
      boxShadow: {
        neon: tokens.shadow.glow,
        crimson: `0 0 24px ${tokens.colors.danger}`,
        glow: tokens.shadow.glow,
        card: tokens.shadow.card,
        panel: tokens.shadow.card,
      },
      opacity: {
        6: '0.06',
        8: '0.08',
        12: '0.12',
        14: '0.14',
        15: '0.15',
        16: '0.16',
        46: '0.46',
        55: '0.55',
        56: '0.56',
        62: '0.62',
        64: '0.64',
        68: '0.68',
        72: '0.72',
        76: '0.76',
        82: '0.82',
        84: '0.84',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'float-soft': 'floatSoft 6s ease-in-out infinite',
        'spin-arc': 'spinArc 1s linear infinite',
        'shimmer': 'shimmer 2.2s linear infinite',
        'fade-up': 'fadeUp 0.4s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        floatSoft: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        spinArc: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% center' },
          '100%': { backgroundPosition: '200% center' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
