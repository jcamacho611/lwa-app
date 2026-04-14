import { HTMLAttributes, ReactNode } from "react";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode;
};

export default function Card({ children, className = "", ...props }: CardProps) {
  return (
    <div
      className={[
        "rounded-2xl border border-white/10 bg-bgCard p-5 shadow-card",
        className,
      ].join(" ")}
      {...props}
    >
      {children}
    </div>
  );
}
