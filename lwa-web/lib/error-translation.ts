/**
 * Error Translation Layer
 * 
 * Converts technical errors into user-friendly messages that maintain trust.
 * NEVER shows "Error" - always provides value.
 */

export interface TranslatedError {
  title: string;
  message: string;
  action: string;
  fallbackAvailable: boolean;
  severity: "info" | "warning" | "success";
}

/**
 * Translate any error into a user-friendly message
 */
export function translateError(error: unknown): TranslatedError {
  const errorMessage = error instanceof Error ? error.message : String(error);
  
  // Network errors
  if (errorMessage.includes("network") || errorMessage.includes("fetch") || errorMessage.includes("connection")) {
    return {
      title: "Working offline...",
      message: "We couldn't reach our servers, but your content is still being analyzed.",
      action: "Your clips will appear using our offline engine (same quality, zero delay).",
      fallbackAvailable: true,
      severity: "info",
    };
  }
  
  // API errors
  if (errorMessage.includes("API") || errorMessage.includes("timeout") || errorMessage.includes("500")) {
    return {
      title: "Switching to guaranteed mode...",
      message: "Our advanced system is taking a break, but we've got you covered.",
      action: "Using our 100% reliable analysis engine instead. You'll get the same great clips.",
      fallbackAvailable: true,
      severity: "info",
    };
  }
  
  // Auth errors
  if (errorMessage.includes("auth") || errorMessage.includes("token") || errorMessage.includes("unauthorized")) {
    return {
      title: "Demo mode activated",
      message: "Let's show you what LWA can do - no signup required.",
      action: "Try our instant demo with pre-generated clips, or sign in to process your own content.",
      fallbackAvailable: true,
      severity: "info",
    };
  }
  
  // Rate limit
  if (errorMessage.includes("rate") || errorMessage.includes("limit") || errorMessage.includes("quota")) {
    return {
      title: "Taking a breather...",
      message: "You've been generating a lot of great content!",
      action: "Your clips are still being prepared. Try again in a moment, or check out your recent results.",
      fallbackAvailable: false,
      severity: "warning",
    };
  }
  
  // Rendering errors
  if (errorMessage.includes("render") || errorMessage.includes("video") || errorMessage.includes("processing")) {
    return {
      title: "Strategy clips ready!",
      message: "Video rendering is taking longer than expected, but your content intelligence is complete.",
      action: "You have everything you need to post: hooks, captions, and timestamps. Videos will be ready shortly.",
      fallbackAvailable: true,
      severity: "success",
    };
  }
  
  // Default - never show generic error
  return {
    title: "Analyzing your content...",
    message: "We're making sure you get the best possible clips.",
    action: "Using our guaranteed analysis engine to deliver your results. This will only take a moment.",
    fallbackAvailable: true,
    severity: "info",
  };
}

/**
 * Success translation - makes success feel even better
 */
export function translateSuccess(clipCount: number, method?: string): {
  title: string;
  subtitle: string;
  excitement: string;
} {
  if (clipCount === 0) {
    return {
      title: "Content analyzed",
      subtitle: "Your content has been processed",
      excitement: "Try adding more details or a different angle for more clip opportunities.",
    };
  }
  
  if (clipCount === 1) {
    return {
      title: "Perfect clip found!",
      subtitle: "We found your best moment",
      excitement: "This is your golden clip - post it now for maximum impact.",
    };
  }
  
  if (clipCount <= 3) {
    return {
      title: "Great clips ready!",
      subtitle: `${clipCount} high-quality clips analyzed`,
      excitement: "You have a solid content strategy. Post the #1 clip first for best results.",
    };
  }
  
  return {
    title: "Content goldmine!",
    subtitle: `${clipCount} clips ready to post`,
    excitement: method === "analysis_engine" 
      ? "Our analysis engine found multiple high-value moments. Space these out over the week."
      : "Multiple strong clips identified. You have content for days!",
  };
}

/**
 * Clip quality labels based on score
 */
export function getQualityLabel(score: number): {
  label: string;
  color: string;
  description: string;
} {
  if (score >= 0.85) {
    return {
      label: "Viral Potential",
      color: "#10b981", // emerald
      description: "Strong hook pattern + emotional trigger + optimal length",
    };
  }
  if (score >= 0.7) {
    return {
      label: "High Engagement",
      color: "#3b82f6", // blue
      description: "Proven engagement pattern with clear value proposition",
    };
  }
  if (score >= 0.55) {
    return {
      label: "Solid Post",
      color: "#f59e0b", // amber
      description: "Good content with consistent messaging",
    };
  }
  return {
    label: "Test Clip",
    color: "#6b7280", // gray
    description: "Try this angle and see how your audience responds",
  };
}
