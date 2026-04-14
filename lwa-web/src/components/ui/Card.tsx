import React from 'react';

type CardVariant = 'hero' | 'glass' | 'utility';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
}

export function Card({
  variant = 'glass',
  className = '',
  children,
  ...props
}: CardProps) {
  const variants: Record<CardVariant, string> = {
    hero: 'rounded-2xl border border-neon-purple/30 bg-surface-800/60 backdrop-blur-xl shadow-card-premium neon-glow p-8',
    glass:
      'rounded-xl border border-white/8 bg-surface-800/40 backdrop-blur-md p-6',
    utility: 'rounded-lg border border-white/6 bg-surface-800/30 p-4',
  };

  return (
    <div className={`${variants[variant]} ${className}`} {...props}>
      {children}
    </div>
  );
}
