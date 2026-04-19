import { ReactNode } from "react";

type WorldLayerProps = {
  className: string;
  children?: ReactNode;
};

export function WorldLayer({ className, children }: WorldLayerProps) {
  return (
    <div className={className} aria-hidden="true">
      {children}
    </div>
  );
}
