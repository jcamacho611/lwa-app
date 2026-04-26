export const tokens = {
  colors: {
    bg: "#0A0A0F",
    bgElev: "#12121A",
    bgCard: "#161620",
    gold: "#F5C842",
    goldBright: "#FFD54F",
    goldDim: "rgba(245,200,66,0.08)",
    goldBorder: "rgba(245,200,66,0.28)",
    ink: "#FFFFFF",
    inkMid: "rgba(255,255,255,0.62)",
    inkFaint: "rgba(255,255,255,0.18)",
    success: "#3DD68C",
    danger: "#FF5A5A",
    divider: "rgba(255,255,255,0.08)",
    glass: "rgba(255,255,255,0.025)",
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
    card: "0 8px 24px rgba(0,0,0,0.32)",
    glow: "0 0 32px rgba(245,200,66,0.18)",
  },
} as const;

export type DesignTokens = typeof tokens;
