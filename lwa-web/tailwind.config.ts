import type { Config } from 'tailwindcss';

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
        neonPurple: "#B88632",
        neonBlue: "#D9B56D",
        neonPink: "#F5E0B3",
        neonGlow: "#E2C17A",
        neonCyan: "#F1D7A1",
        brightCyan: "#FFF0CF",
        accentCrimson: "#7A162C",
        accentWine: "#441019",
        bgDark: "#050403",
        bgCard: "#0E0B08",
        bgPanel: "#15110C",
        bgGlass: "#100D09",
        ink: '#F6EEDD',
        subtext: '#B7A58A',
        muted: '#7C6D55',
        accent: '#D9B56D',
        accentSoft: '#F3DAA3',
        accentBlue: '#A97729',
        accentPink: '#CC9652',
        surfaceLine: 'rgba(255,255,255,0.08)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-hero': 'linear-gradient(135deg, #050816 0%, #0A1023 45%, #10182E 100%)',
        'hero-radial': 'radial-gradient(circle at 16% 12%, rgba(124,58,237,0.20), transparent 24%), radial-gradient(circle at 82% 18%, rgba(37,99,255,0.18), transparent 26%), radial-gradient(circle at 68% 78%, rgba(34,211,238,0.12), transparent 22%), linear-gradient(180deg, #050816 0%, #071024 48%, #050816 100%)',
        'mesh-grid': 'linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)',
      },
      boxShadow: {
        neon: "0 0 24px rgba(217,181,109,0.28)",
        crimson: "0 0 24px rgba(122,22,44,0.22)",
        glow: '0 0 0 1px rgba(217,181,109,0.16), 0 24px 70px rgba(5,4,3,0.58)',
        card: '0 28px 80px rgba(0,0,0,0.42)',
        panel: '0 22px 60px rgba(0,0,0,0.34)',
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
