export function LogoWordmark() {
  return (
    <svg
      viewBox="0 0 120 32"
      className="h-8 w-auto"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="LWA"
    >
      <defs>
        <linearGradient id="lwaWordGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#7C3AED', stopOpacity: 1 }} />
          <stop
            offset="100%"
            style={{ stopColor: '#2563FF', stopOpacity: 1 }}
          />
        </linearGradient>
      </defs>
      <text
        x="0"
        y="24"
        fontFamily="system-ui, -apple-system, sans-serif"
        fontSize="28"
        fontWeight="700"
        letterSpacing="-0.5"
        fill="url(#lwaWordGrad)"
      >
        LWA
      </text>
    </svg>
  );
}

export function LogoMark() {
  return (
    <svg
      viewBox="0 0 32 32"
      className="h-8 w-8"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="LWA"
    >
      <defs>
        <linearGradient id="lwaMarkGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#7C3AED', stopOpacity: 1 }} />
          <stop
            offset="100%"
            style={{ stopColor: '#2563FF', stopOpacity: 1 }}
          />
        </linearGradient>
        <filter id="lwaGlow">
          <feGaussianBlur stdDeviation="1.5" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <rect
        x="4"
        y="4"
        width="24"
        height="24"
        rx="6"
        fill="none"
        stroke="url(#lwaMarkGrad)"
        strokeWidth="1.5"
        filter="url(#lwaGlow)"
      />
      <path
        d="M 10 10 L 10 22 M 10 10 L 18 10"
        stroke="url(#lwaMarkGrad)"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
        filter="url(#lwaGlow)"
      />
      <circle
        cx="22"
        cy="10"
        r="1.5"
        fill="url(#lwaMarkGrad)"
        filter="url(#lwaGlow)"
      />
    </svg>
  );
}
