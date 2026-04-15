"use client";

import { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
};

export default function Button({
  children,
  className = "",
  type = "button",
  variant = "primary",
  size = "md",
  ...props
}: ButtonProps) {
  const variantClass =
    variant === "primary"
      ? "primary-button text-white"
      : variant === "secondary"
        ? "secondary-button text-ink/90"
        : "ghost-button text-ink/72";
  const sizeClass =
    size === "lg" ? "px-6 py-3.5 text-sm" : size === "sm" ? "px-4 py-2 text-sm" : "px-5 py-3 text-sm";

  return (
    <button
      type={type}
      className={[
        "inline-flex items-center justify-center rounded-full font-semibold transition duration-200 hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60",
        variantClass,
        sizeClass,
        className,
      ].join(" ")}
      {...props}
    >
      {children}
    </button>
  );
}
