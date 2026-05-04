/**
 * Version State Definitions
 * 
 * Clear definitions for all operating modes.
 * This eliminates debugging chaos by making system state explicit.
 */

export type VersionState = 
  | "demo"           // Pre-generated clips, no backend
  | "offline"        // Analysis engine, no AI APIs
  | "strategy_only"  // Analysis engine + manual input
  | "rendering"      // Full pipeline with video rendering
  | "recovery";      // Fallback mode after error

export interface VersionStateConfig {
  state: VersionState;
  label: string;
  description: string;
  features: string[];
  limitations: string[];
  userMessage: string;
}

export const VERSION_STATES: Record<VersionState, VersionStateConfig> = {
  demo: {
    state: "demo",
    label: "Demo Mode",
    description: "Pre-generated clips for instant experience. No backend required.",
    features: [
      "Instant results",
      "No signup required",
      "3 sample clips",
      "Copy hooks/captions",
    ],
    limitations: [
      "Cannot process custom content",
      "Static demo data only",
    ],
    userMessage: "Try LWA instantly with sample content. No signup required.",
  },
  
  offline: {
    state: "offline",
    label: "Offline Mode",
    description: "100% offline analysis using deterministic engine. No AI APIs.",
    features: [
      "Guaranteed 3-5 clips",
      "Template-based hooks",
      "Keyword scoring",
      "Never fails",
      "Works without internet",
    ],
    limitations: [
      "No AI nuance",
      "Template-driven output",
      "No video rendering",
    ],
    userMessage: "Using offline mode - your clips are being analyzed locally (fast, reliable, always works).",
  },
  
  strategy_only: {
    state: "strategy_only",
    label: "Strategy Mode",
    description: "Full analysis with hooks, captions, CTAs, but no video rendering.",
    features: [
      "Complete content strategy",
      "Hooks + captions + CTAs",
      "Post scheduling",
      "Quality scoring",
      "Posting schedule",
    ],
    limitations: [
      "No rendered videos",
      "Strategy guidance only",
    ],
    userMessage: "Your content strategy is ready! Post these clips with the provided hooks and captions.",
  },
  
  rendering: {
    state: "rendering",
    label: "Full Mode",
    description: "Complete pipeline with video rendering and AI enhancement.",
    features: [
      "Video rendering",
      "AI-enhanced hooks",
      "Auto-captioned videos",
      "Full automation",
      "Platform optimization",
    ],
    limitations: [
      "Requires API keys",
      "Slower processing",
      "May fail without fallback",
    ],
    userMessage: "Full processing mode active. Your videos are being rendered with AI-enhanced captions.",
  },
  
  recovery: {
    state: "recovery",
    label: "Recovery Mode",
    description: "Fallback mode after error. Uses guaranteed engine.",
    features: [
      "Always returns clips",
      "No errors shown",
      "Automatic fallback",
      "Maintains trust",
    ],
    limitations: [
      "Simplified output",
      "May use generic templates",
    ],
    userMessage: "Switching to guaranteed mode - you'll still get great clips, just using our most reliable engine.",
  },
};

/**
 * Get version state for current conditions
 */
export function detectVersionState(options: {
  hasError: boolean;
  hasVideoUrl: boolean;
  hasApiKey: boolean;
  isDemo: boolean;
  isOffline: boolean;
}): VersionState {
  if (options.isDemo) return "demo";
  if (options.hasError) return "recovery";
  if (options.isOffline) return "offline";
  if (!options.hasVideoUrl) return "strategy_only";
  if (options.hasApiKey) return "rendering";
  return "offline";
}

/**
 * Feature flags based on version state
 */
export function getFeatures(state: VersionState) {
  return {
    canRenderVideo: state === "rendering",
    canUseAI: state === "rendering",
    isGuaranteed: state === "offline" || state === "recovery" || state === "demo",
    isInstant: state === "demo" || state === "offline",
    showsSchedule: state !== "demo",
    showsScore: true,
    allowsCustomInput: state !== "demo",
  };
}
