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
        neonPurple: "#8B5CF6",
        neonBlue: "#3B82F6",
        neonPink: "#EC4899",
        neonGlow: "#A855F7",
        bgDark: "#050505",
        bgCard: "#0A0A0A",
        ink: '#edf2ff',
        muted: '#8a93a8',
        accent: '#79b8ff',
        accentSoft: '#7c5cff',
        accentPink: '#f15efc',
        surfaceLine: 'rgba(255,255,255,0.08)',
        brand: {
          50:  '#f0f4ff',
          100: '#e0e9ff',
          200: '#c7d7fe',
          300: '#a5b8fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        surface: {
          900: '#0a0a0f',
          800: '#111118',
          700: '#18181f',
          600: '#1e1e28',
          500: '#26263a',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-hero': 'linear-gradient(135deg, #0a0a0f 0%, #1a1040 50%, #0a0a0f 100%)',
        'hero-radial': 'radial-gradient(circle at top, rgba(121, 184, 255, 0.18), transparent 30%), radial-gradient(circle at 82% 16%, rgba(124, 92, 255, 0.18), transparent 24%), linear-gradient(180deg, #06070b 0%, #090b11 52%, #05060a 100%)',
        'mesh-grid': 'linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)',
      },
      boxShadow: {
        neon: "0 0 20px rgba(139,92,246,0.5)",
        glow: '0 0 0 1px rgba(121,184,255,0.16), 0 18px 60px rgba(14,26,54,0.42)',
        card: '0 22px 60px rgba(0,0,0,0.35)',
      },
      opacity: {
        6: '0.06',
        8: '0.08',
        12: '0.12',
        46: '0.46',
        55: '0.55',
        56: '0.56',
        62: '0.62',
        64: '0.64',
        68: '0.68',
        72: '0.72',
        82: '0.82',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
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
      },
    },
  },
  plugins: [],
};

export default config;
