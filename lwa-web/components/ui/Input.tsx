import { InputHTMLAttributes, TextareaHTMLAttributes } from "react";

type InputProps = InputHTMLAttributes<HTMLInputElement>;

export default function Input({ className = "", ...props }: InputProps) {
  return (
    <input
      {...props}
      className={[
        "w-full rounded-xl border border-white/10 bg-black/70 p-4 text-white placeholder:text-white/35 focus:border-neonPurple focus:outline-none focus:ring-4 focus:ring-neonPurple/10",
        className,
      ].join(" ")}
    />
  );
}

export function Textarea({ className = "", ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      {...props}
      className={[
        "w-full rounded-xl border border-white/10 bg-black/70 p-4 text-white placeholder:text-white/35 focus:border-neonPurple focus:outline-none focus:ring-4 focus:ring-neonPurple/10",
        className,
      ].join(" ")}
    />
  );
}
