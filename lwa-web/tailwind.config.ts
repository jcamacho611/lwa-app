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
        midnight: "#06070A",
        panel: "#0F1218",
        accent: "#5EA8FF",
        accentSoft: "#7B61FF",
        ink: "#E8EEF7",
        muted: "#8A95A8",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(94,168,255,0.24), 0 18px 50px rgba(14, 21, 35, 0.55)",
        card: "0 24px 60px rgba(0, 0, 0, 0.35)",
      },
      backgroundImage: {
        "hero-radial":
          "radial-gradient(circle at top, rgba(94, 168, 255, 0.18), transparent 28%), radial-gradient(circle at 85% 10%, rgba(123, 97, 255, 0.18), transparent 24%)",
      },
    },
  },
  plugins: [],
};

export default config;
