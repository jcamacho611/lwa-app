export const tokens = {
  colors: {
    bg: "#FFF7FC",
    bgElev: "#F6EEFF",
    bgCard: "#FFFDFE",
    gold: "#8E76FF",
    goldBright: "#F5BDD8",
    goldDim: "rgba(142,118,255,0.10)",
    goldBorder: "rgba(142,118,255,0.24)",
    ink: "#2D1E3D",
    inkMid: "rgba(45,30,61,0.68)",
    inkFaint: "rgba(45,30,61,0.18)",
    success: "#3DD68C",
    danger: "#FF5A5A",
    divider: "rgba(115,95,168,0.14)",
    glass: "rgba(255,255,255,0.48)",
  },
  fonts: {
    display: "Poppins",
    body: "Poppins",
  },
  radius: {
    sm: "8px",
    md: "14px",
    lg: "18px",
    xl: "24px",
    pill: "999px",
  },
  shadow: {
    card: "0 18px 48px rgba(107,80,152,0.14)",
    glow: "0 0 36px rgba(142,118,255,0.18)",
  },
} as const;

export type DesignTokens = typeof tokens;
