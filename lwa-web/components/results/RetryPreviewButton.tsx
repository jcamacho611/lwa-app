"use client";

type RetryPreviewButtonProps = {
  onRetry: () => void;
  className?: string;
};

export function RetryPreviewButton({ onRetry, className = "" }: RetryPreviewButtonProps) {
  return (
    <button
      onClick={onRetry}
      className={`
        px-4 py-2 bg-red-500 text-white rounded-lg 
        text-sm font-medium hover:bg-red-600 
        transition-colors duration-200
        ${className}
      `}
    >
      Retry Render
    </button>
  );
}
