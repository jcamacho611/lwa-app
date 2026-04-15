import { InputHTMLAttributes, TextareaHTMLAttributes } from "react";

type InputProps = InputHTMLAttributes<HTMLInputElement>;

export default function Input({ className = "", ...props }: InputProps) {
  return (
    <input
      {...props}
      className={[
        "input-surface w-full rounded-[22px] px-4 py-3.5 text-sm text-ink placeholder:text-muted",
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
        "input-surface min-h-[120px] w-full rounded-[22px] px-4 py-3.5 text-sm text-ink placeholder:text-muted",
        className,
      ].join(" ")}
    />
  );
}
