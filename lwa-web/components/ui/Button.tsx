"use client";

import { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
};

export default function Button({ children, className = "", type = "button", ...props }: ButtonProps) {
  return (
    <button
      type={type}
      className={[
        "rounded-xl bg-gradient-to-r from-neonPurple via-neonBlue to-neonPink px-6 py-3 font-semibold text-white shadow-neon transition duration-200 hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-60",
        className,
      ].join(" ")}
      {...props}
    >
      {children}
    </button>
  );
}
