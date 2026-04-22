"use client";

type RetryPreviewButtonProps = {
  onRetry: () => void;
  disabled?: boolean;
  label?: string;
  className?: string;
};

export function RetryPreviewButton({ onRetry, disabled = false, label = "Retry preview", className = "" }: RetryPreviewButtonProps) {
  return (
    <button
      type="button"
      onClick={onRetry}
      disabled={disabled}
      className={`
        secondary-button inline-flex items-center justify-center rounded-full px-4 py-2
        text-sm font-medium disabled:cursor-not-allowed disabled:opacity-60
        ${className}
      `}
    >
      {label}
    </button>
  );
}
