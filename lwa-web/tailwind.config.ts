import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#05070B",
        surface: "#0B1016",
        panel: "rgba(255,255,255,0.05)",
        line: "rgba(255,255,255,0.08)",
        accent: "#55BFFF",
        accent2: "#8CE0FF",
        gold: "#E9C98B",
        text: "#F4F7FB",
        muted: "rgba(244,247,251,0.68)",
      },
      boxShadow: {
        glass: "0 20px 60px rgba(0,0,0,0.32)",
        glow: "0 0 0 1px rgba(255,255,255,0.06), 0 24px 80px rgba(85,191,255,0.18)",
      },
      borderRadius: {
        xl2: "1.25rem",
        xl3: "1.75rem",
      },
      backgroundImage: {
        hero:
          "radial-gradient(circle at top right, rgba(85,191,255,0.20), transparent 34%), radial-gradient(circle at bottom left, rgba(233,201,139,0.16), transparent 26%), linear-gradient(140deg, #05070B, #0A111A 60%, #05070B)",
        button:
          "linear-gradient(135deg, rgba(85,191,255,1), rgba(140,224,255,0.95))",
      },
      animation: {
        float: "float 8s ease-in-out infinite",
        pulseSoft: "pulseSoft 1.6s ease-in-out infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-8px)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.55" },
          "50%": { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
