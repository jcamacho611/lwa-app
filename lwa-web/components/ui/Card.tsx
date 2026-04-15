import { HTMLAttributes, ReactNode } from "react";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode;
  variant?: "glass" | "hero" | "utility";
};

export default function Card({ children, className = "", variant = "glass", ...props }: CardProps) {
  const variantClass =
    variant === "hero" ? "hero-card" : variant === "utility" ? "metric-tile" : "glass-panel";

  return (
    <div
      className={[
        "rounded-[28px] p-5",
        variantClass,
        className,
      ].join(" ")}
      {...props}
    >
      {children}
    </div>
  );
}
