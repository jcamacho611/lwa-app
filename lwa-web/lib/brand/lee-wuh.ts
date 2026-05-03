/**
 * Lee-Wuh Brand System v0
 * 
 * Mascot constants, messaging, and brand identity for Lee-Wuh: The Last Creator.
 * Lee-Wuh is the mascot/brand guide - LWA remains the product/company name.
 */

export type LeeWuhState = 
  | "idle"
  | "watching" 
  | "thinking"
  | "ingesting"
  | "composing"
  | "rendering"
  | "success"
  | "warning"
  | "error"
  | "overlord";

export type LeeWuhSize = "sm" | "md" | "lg" | "hero";

export type LeeWuhTone = "default" | "success" | "warning" | "danger" | "premium";

export const LEE_WUH_BRAND = {
  // Core identity
  mascotName: "Lee-Wuh",
  pronunciation: "lee-wuh",
  productName: "LWA",
  role: "The Last Creator",
  tagline: "Create. Inspire. Take over.",
  coreLine: "The final boss of lazy content.",
  
  // Asset paths
  assetPath: "/brand/lee-wuh-mascot.png",
  heroAssetPath: "/brand/lee-wuh-hero-16x9.png",
  avatarPath: "/brand/lee-wuh/avatar.png",
  loadingPath: "/brand/lee-wuh/loading.png",
  
  // Brand colors (inherited from design system)
  colors: {
    black: "#050505",
    charcoal: "#111016",
    gold: "#F4C45D",
    deepGold: "#B88422",
    purple: "#8B3DFF",
    violet: "#B56CFF",
    red: "#C92A2A",
  },
  
  // Messaging system
  messages: {
    // Homepage hero
    hero: {
      eyebrow: "Meet Lee-Wuh",
      headline: "The final boss of lazy content.",
      subtext: "Drop one video. Get the best clips, hooks, captions, and posting angles.",
      description: "Lee-Wuh is the guardian of the creator engine: Afro-futurist, anime-final-boss energy wrapped around a real clipping product.",
    },
    
    // Loading states
    loading: {
      primary: "Lee-Wuh is finding your strongest moments...",
      secondary: "Scanning hooks, silence, energy, and viral structure.",
      processing: "Lee-Wuh is analyzing the source material...",
      rendering: "Lee-Wuh is composing the perfect clip...",
    },
    
    // Empty states
    empty: {
      primary: "Feed Lee-Wuh a source.",
      secondary: "Paste a video URL and let the clipping engine find the best short-form moments.",
      noSources: "No sources yet. Add a video and Lee-Wuh will get to work.",
      noResults: "Lee-Wuh couldn't find any clips in this source. Try another video.",
    },
    
    // Success states
    success: {
      primary: "Boss-level clip detected.",
      secondary: "Post this first for maximum impact.",
      completed: "Lee-Wuh has finished analyzing your content.",
      exported: "Your clip pack is ready for download.",
    },
    
    // Tips and guidance
    tips: [
      "Drop one source. I'll find the strongest first move.",
      "Rendered proof first. Strategy second.",
      "Boss-level clip detected. Post this first.",
      "Feed me more sources and I'll find patterns.",
      "The silence before the drop matters most.",
      "Your first 3 seconds determine everything.",
      "I'm watching for viral structure.",
      "Energy spikes are your gold mines.",
    ],
    
    // Error states
    error: {
      primary: "Lee-Wuh couldn't process this source.",
      secondary: "Check the URL or try uploading the file directly.",
      network: "Lee-Wuh lost connection to the source.",
      invalid: "This doesn't look like a video source Lee-Wuh can analyze.",
    },
  },
  
  // Character traits
  personality: {
    core: "Afro-futurist anime final boss",
    demeanor: "Cute but powerful",
    energy: "Creator engine guardian",
    style: "Premium luxury with streetwear edge",
    fusion: "Japanese x African x American",
  },
  
  // Usage rules
  rules: {
    placement: "Keep at edges/side, never center",
    interaction: "Guide, don't block workflows",
    mobile: "Collapsible on small screens",
    animation: "Reduced motion safe",
    priority: "Brand layer, not product replacement",
  },
  
  // Asset usage guide
  assetUsage: {
    hero: "Homepage hero image (16:9)",
    mascot: "General mascot usage (square)",
    avatar: "Small avatars and loading states",
    loading: "Processing and loading screens",
    whop: "Marketplace and product listings",
    transparent: "Overlays and stickers",
  },
} as const;

// Helper functions for Lee-Wuh messaging
export function getLeeWuhMessage(type: keyof typeof LEE_WUH_BRAND.messages, variant?: string): string {
  const messages = LEE_WUH_BRAND.messages[type];
  
  if (typeof messages === 'string') {
    return messages;
  }
  
  if (typeof messages === 'object' && messages !== null) {
    const messageObj = messages as Record<string, string>;
    return variant ? messageObj[variant] || messageObj.primary || Object.values(messageObj)[0] : Object.values(messageObj)[0];
  }
  
  return "";
}

export function getLeeWuhTip(index?: number): string {
  const tips = LEE_WUH_BRAND.messages.tips;
  return index !== undefined ? tips[index % tips.length] : tips[Math.floor(Math.random() * tips.length)];
}

export function getLeeWuhAsset(variant: 'hero' | 'mascot' | 'avatar' | 'loading' = 'mascot'): string {
  switch (variant) {
    case 'hero':
      return LEE_WUH_BRAND.heroAssetPath;
    case 'avatar':
      return LEE_WUH_BRAND.avatarPath;
    case 'loading':
      return LEE_WUH_BRAND.loadingPath;
    default:
      return LEE_WUH_BRAND.assetPath;
  }
}
