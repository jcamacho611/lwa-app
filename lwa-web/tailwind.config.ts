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
        neonPurple: "#FF1E56",
        neonBlue: "#FF2DA6",
        neonPink: "#FF6B8B",
        neonGlow: "#FF003C",
        neonCyan: "#00E7FF",
        brightCyan: "#8DF7FF",
        accentCrimson: "#A1002F",
        accentWine: "#520A1B",
        bgDark: "#040405",
        bgCard: "#0A0608",
        bgPanel: "#12070A",
        bgGlass: "#0B0507",
        ink: "#F8F3F5",
        subtext: "#CCB8BE",
        muted: "#8D7179",
        accent: "#FF1E56",
        accentSoft: "#FF6B8B",
        accentBlue: "#00E7FF",
        accentPink: "#FF2DA6",
        surfaceLine: 'rgba(255,255,255,0.08)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-hero': 'linear-gradient(135deg, #040405 0%, #12070A 45%, #18060F 100%)',
        'hero-radial': 'radial-gradient(circle at 16% 12%, rgba(255,30,86,0.18), transparent 24%), radial-gradient(circle at 82% 18%, rgba(255,45,166,0.16), transparent 26%), radial-gradient(circle at 68% 78%, rgba(0,231,255,0.1), transparent 22%), linear-gradient(180deg, #040405 0%, #0B0507 48%, #040405 100%)',
        'mesh-grid': 'linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)',
      },
      boxShadow: {
        neon: "0 0 24px rgba(255,30,86,0.28)",
        crimson: "0 0 24px rgba(161,0,47,0.22)",
        glow: '0 0 0 1px rgba(255,30,86,0.16), 0 24px 70px rgba(4,4,5,0.64)',
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
