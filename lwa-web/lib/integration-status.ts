/**
 * LWA Integration Status Configuration
 * 
 * This file defines the current status of all API integrations.
 * Status values are used throughout the application to conditionally
 * render features and manage user expectations.
 */

export type IntegrationStatus = 
  | 'live'           // Fully implemented and verified in production
  | 'planned'        // Approved for development in current roadmap phase
  | 'future_only'    // Conceptual phase, not ready for development
  | 'blocked'        // Requires prerequisites or compliance review
  | 'requires_review'; // Needs security/legal/compliance approval

export type IntegrationTier = 
  | 'core_product'   // Tier 1: Core paid product APIs
  | 'premium_engine' // Tier 2: Premium clipping engine APIs
  | 'marketplace'    // Tier 3: Marketplace/creator economy APIs
  | 'world_game'     // Tier 4: World/game/Blender/XR APIs
  | 'blockchain';    // Tier 5: Blockchain/NFT future-only APIs

export interface IntegrationConfig {
  name: string;
  status: IntegrationStatus;
  tier: IntegrationTier;
  description: string;
  requiresAuth: boolean;
  publicFeature: boolean;
  lastUpdated: string;
  notes?: string;
}

/**
 * Core Product Integrations (Tier 1)
 * These are the foundational APIs that power LWA's core product.
 */
export const CORE_PRODUCT_INTEGRATIONS: Record<string, IntegrationConfig> = {
  // LWA Backend API
  lwa_backend: {
    name: 'LWA Backend API',
    status: 'live',
    tier: 'core_product',
    description: 'Core clip generation, user management, and billing',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },

  // Storage APIs
  aws_s3: {
    name: 'AWS S3 Storage',
    status: 'live',
    tier: 'core_product',
    description: 'Asset storage and CDN delivery',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },

  cloudflare_r2: {
    name: 'Cloudflare R2',
    status: 'live',
    tier: 'core_product',
    description: 'Cost-effective storage and CDN',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },

  // Job Queue
  redis_rq: {
    name: 'Redis/RQ Workers',
    status: 'live',
    tier: 'core_product',
    description: 'Background job processing and caching',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },

  // Media Processing
  ffmpeg: {
    name: 'FFmpeg Media Pipeline',
    status: 'live',
    tier: 'core_product',
    description: 'Video processing, transcoding, and clip extraction',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },

  // AI/ML APIs
  openai_whisper: {
    name: 'OpenAI Whisper Transcription',
    status: 'live',
    tier: 'core_product',
    description: 'Audio/video transcription for clip analysis',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },

  openai_gpt: {
    name: 'OpenAI GPT-4',
    status: 'live',
    tier: 'core_product',
    description: 'Content analysis, hook generation, Auto Editor Brain',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },

  anthropic_claude: {
    name: 'Anthropic Claude',
    status: 'live',
    tier: 'core_product',
    description: 'Alternative LLM for content analysis',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },

  // Analytics
  posthog: {
    name: 'PostHog Analytics',
    status: 'live',
    tier: 'core_product',
    description: 'User analytics, feature tracking, conversion metrics',
    requiresAuth: false,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },
};

/**
 * Premium Engine Integrations (Tier 2)
 * These APIs enhance the clipping engine with advanced features.
 */
export const PREMIUM_ENGINE_INTEGRATIONS: Record<string, IntegrationConfig> = {
  // Social Media APIs
  youtube_api: {
    name: 'YouTube Data API',
    status: 'planned',
    tier: 'premium_engine',
    description: 'Video metadata, comments, analytics for clip optimization',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires YouTube API approval and quota management',
  },

  tiktok_api: {
    name: 'TikTok API',
    status: 'planned',
    tier: 'premium_engine',
    description: 'Direct posting to TikTok platform',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires platform approval and compliance review',
  },

  instagram_api: {
    name: 'Instagram API',
    status: 'planned',
    tier: 'premium_engine',
    description: 'Direct posting to Instagram platform',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires platform approval and compliance review',
  },

  // Music Licensing
  epidemic_sound: {
    name: 'Epidemic Sound',
    status: 'future_only',
    tier: 'premium_engine',
    description: 'Licensed background music for clips',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires legal review and licensing agreements',
  },

  soundstripe: {
    name: 'Soundstripe',
    status: 'future_only',
    tier: 'premium_engine',
    description: 'Licensed background music for clips',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires legal review and licensing agreements',
  },

  // Image Generation
  openai_dalle: {
    name: 'OpenAI DALL-E',
    status: 'planned',
    tier: 'premium_engine',
    description: 'AI-generated thumbnails and promotional images',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },

  replicate: {
    name: 'Replicate',
    status: 'planned',
    tier: 'premium_engine',
    description: 'AI model hosting for image generation',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },

  stability_ai: {
    name: 'Stability AI',
    status: 'planned',
    tier: 'premium_engine',
    description: 'AI image generation models',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },

  // Email Services
  resend: {
    name: 'Resend',
    status: 'planned',
    tier: 'premium_engine',
    description: 'Transactional emails and notifications',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },

  postmark: {
    name: 'Postmark',
    status: 'planned',
    tier: 'premium_engine',
    description: 'Transactional emails and notifications',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },

  sendgrid: {
    name: 'SendGrid',
    status: 'planned',
    tier: 'premium_engine',
    description: 'Transactional emails and notifications',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
  },
};

/**
 * Marketplace Integrations (Tier 3)
 * These APIs power the creator economy and marketplace features.
 */
export const MARKETPLACE_INTEGRATIONS: Record<string, IntegrationConfig> = {
  // Payment Processing
  stripe_connect: {
    name: 'Stripe Connect',
    status: 'future_only',
    tier: 'marketplace',
    description: 'Creator payouts and marketplace transactions',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires compliance and banking partnership',
  },

  whop_marketplace: {
    name: 'Whop Marketplace',
    status: 'planned',
    tier: 'marketplace',
    description: 'Marketplace integration and user authentication',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires legal review and compliance',
  },

  // Identity Verification
  stripe_identity: {
    name: 'Stripe Identity',
    status: 'future_only',
    tier: 'marketplace',
    description: 'Identity verification for creators and payouts',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires legal compliance verification',
  },

  persona: {
    name: 'Persona',
    status: 'future_only',
    tier: 'marketplace',
    description: 'Identity verification for creators and payouts',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires legal compliance verification',
  },

  // Contract Management
  docusign: {
    name: 'DocuSign',
    status: 'future_only',
    tier: 'marketplace',
    description: 'Digital contracts for marketplace agreements',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires legal template development',
  },

  pandadoc: {
    name: 'PandaDoc',
    status: 'future_only',
    tier: 'marketplace',
    description: 'Digital contracts for marketplace agreements',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires legal template development',
  },

  // Moderation
  content_safety: {
    name: 'Content Safety API',
    status: 'planned',
    tier: 'marketplace',
    description: 'Content moderation and community safety',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires policy development',
  },
};

/**
 * World/Game/XR Integrations (Tier 4)
 * These APIs power the world layer, game features, and XR experiences.
 */
export const WORLD_GAME_INTEGRATIONS: Record<string, IntegrationConfig> = {
  // 3D Asset Pipeline
  blender_api: {
    name: 'Blender Python API',
    status: 'future_only',
    tier: 'world_game',
    description: 'Automated asset generation and 3D content creation',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires Blender script development',
  },

  // Design Tools
  figma_api: {
    name: 'Figma API',
    status: 'planned',
    tier: 'world_game',
    description: 'Design system integration and asset management',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires design token system integration',
  },

  canva_api: {
    name: 'Canva API',
    status: 'future_only',
    tier: 'world_game',
    description: 'Template integration and design tools',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires Canva app development',
  },

  // Game Backend
  nakama: {
    name: 'Nakama',
    status: 'future_only',
    tier: 'world_game',
    description: 'Multiplayer game infrastructure and real-time sync',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires game architecture design',
  },

  colyseus: {
    name: 'Colyseus',
    status: 'future_only',
    tier: 'world_game',
    description: 'Multiplayer game infrastructure and real-time sync',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires game architecture design',
  },

  playfab: {
    name: 'PlayFab',
    status: 'future_only',
    tier: 'world_game',
    description: 'Multiplayer game infrastructure and real-time sync',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires game architecture design',
  },

  // XR Platforms
  meta_quest: {
    name: 'Meta Quest SDK',
    status: 'future_only',
    tier: 'world_game',
    description: 'VR/AR experiences and immersive content',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires VR hardware partnerships',
  },

  openxr: {
    name: 'OpenXR',
    status: 'future_only',
    tier: 'world_game',
    description: 'Cross-platform VR/AR framework',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires XR prototype development',
  },

  // Real-time Networking
  webrtc: {
    name: 'WebRTC',
    status: 'future_only',
    tier: 'world_game',
    description: 'Real-time communication and multiplayer networking',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires networking architecture design',
  },
};

/**
 * Blockchain/NFT Integrations (Tier 5)
 * These APIs power blockchain and NFT features - all marked as future_only.
 */
export const BLOCKCHAIN_INTEGRATIONS: Record<string, IntegrationConfig> = {
  // Wallet Infrastructure
  walletconnect: {
    name: 'WalletConnect',
    status: 'future_only',
    tier: 'blockchain',
    description: 'Mobile wallet integration for blockchain features',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires legal framework and compliance review',
  },

  privy: {
    name: 'Privy',
    status: 'future_only',
    tier: 'blockchain',
    description: 'Wallet abstraction and user onboarding',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires legal framework and compliance review',
  },

  magic: {
    name: 'Magic.link',
    status: 'future_only',
    tier: 'blockchain',
    description: 'Wallet abstraction and user onboarding',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires legal framework and compliance review',
  },

  // Blockchain Infrastructure
  alchemy: {
    name: 'Alchemy',
    status: 'future_only',
    tier: 'blockchain',
    description: 'Blockchain infrastructure and node access',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires blockchain architecture design',
  },

  infura: {
    name: 'Infura',
    status: 'future_only',
    tier: 'blockchain',
    description: 'Blockchain infrastructure and node access',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires blockchain architecture design',
  },

  quicknode: {
    name: 'QuickNode',
    status: 'future_only',
    tier: 'blockchain',
    description: 'Blockchain infrastructure and node access',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires blockchain architecture design',
  },

  // NFT Marketplaces
  opensea: {
    name: 'OpenSea',
    status: 'future_only',
    tier: 'blockchain',
    description: 'NFT marketplace integration and trading',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires legal compliance and audit',
  },

  reservoir: {
    name: 'Reservoir',
    status: 'future_only',
    tier: 'blockchain',
    description: 'NFT marketplace integration and trading',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires legal compliance and audit',
  },

  // Smart Contract Development
  foundry: {
    name: 'Foundry',
    status: 'future_only',
    tier: 'blockchain',
    description: 'Smart contract development and testing',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires smart contract audit planning',
  },

  hardhat: {
    name: 'Hardhat',
    status: 'future_only',
    tier: 'blockchain',
    description: 'Smart contract development and testing',
    requiresAuth: true,
    publicFeature: false,
    lastUpdated: '2024-01-01',
    notes: 'Requires smart contract audit planning',
  },
};

/**
 * Combined integration registry
 */
export const ALL_INTEGRATIONS = {
  ...CORE_PRODUCT_INTEGRATIONS,
  ...PREMIUM_ENGINE_INTEGRATIONS,
  ...MARKETPLACE_INTEGRATIONS,
  ...WORLD_GAME_INTEGRATIONS,
  ...BLOCKCHAIN_INTEGRATIONS,
};

/**
 * Helper functions for integration status management
 */
export const getLiveIntegrations = (): Record<string, IntegrationConfig> => {
  return Object.fromEntries(
    Object.entries(ALL_INTEGRATIONS).filter(([_, config]) => config.status === 'live')
  );
};

export const getPlannedIntegrations = (): Record<string, IntegrationConfig> => {
  return Object.fromEntries(
    Object.entries(ALL_INTEGRATIONS).filter(([_, config]) => config.status === 'planned')
  );
};

export const getFutureOnlyIntegrations = (): Record<string, IntegrationConfig> => {
  return Object.fromEntries(
    Object.entries(ALL_INTEGRATIONS).filter(([_, config]) => config.status === 'future_only')
  );
};

export const getBlockedIntegrations = (): Record<string, IntegrationConfig> => {
  return Object.fromEntries(
    Object.entries(ALL_INTEGRATIONS).filter(([_, config]) => config.status === 'blocked')
  );
};

export const getIntegrationsByTier = (tier: IntegrationTier): Record<string, IntegrationConfig> => {
  return Object.fromEntries(
    Object.entries(ALL_INTEGRATIONS).filter(([_, config]) => config.tier === tier)
  );
};

export const getPublicFeatures = (): Record<string, IntegrationConfig> => {
  return Object.fromEntries(
    Object.entries(ALL_INTEGRATIONS).filter(([_, config]) => config.publicFeature)
  );
};

export const getIntegrationStatus = (integrationId: string): IntegrationStatus => {
  const integration = ALL_INTEGRATIONS[integrationId];
  return integration?.status || 'future_only';
};

export const isIntegrationLive = (integrationId: string): boolean => {
  return getIntegrationStatus(integrationId) === 'live';
};

export const isIntegrationPlanned = (integrationId: string): boolean => {
  return getIntegrationStatus(integrationId) === 'planned';
};

export const isIntegrationBlocked = (integrationId: string): boolean => {
  return getIntegrationStatus(integrationId) === 'blocked';
};

/**
 * Status checking utilities for conditional rendering
 */
export const shouldShowFeature = (integrationId: string): boolean => {
  const integration = ALL_INTEGRATIONS[integrationId];
  return integration?.status === 'live' && integration.publicFeature;
};

export const shouldShowBetaFeature = (integrationId: string): boolean => {
  const integration = ALL_INTEGRATIONS[integrationId];
  return (integration?.status === 'live' || integration?.status === 'planned') && integration.publicFeature;
};

/**
 * Integration health check
 */
export const checkIntegrationHealth = (): {
  live: number;
  planned: number;
  future_only: number;
  blocked: number;
  total: number;
} => {
  const stats = {
    live: 0,
    planned: 0,
    future_only: 0,
    blocked: 0,
    total: 0,
  };

  Object.values(ALL_INTEGRATIONS).forEach((config) => {
    stats.total++;
    if (config.status === 'live') stats.live++;
    else if (config.status === 'planned') stats.planned++;
    else if (config.status === 'future_only') stats.future_only++;
    else if (config.status === 'blocked') stats.blocked++;
    else if (config.status === 'requires_review') stats.blocked++; // Treat requires_review as blocked for now
  });

  return stats;
};

/**
 * Environment variable validation
 */
export const validateRequiredEnvironmentVariables = (integrationId: string): boolean => {
  const integration = ALL_INTEGRATIONS[integrationId];
  if (!integration || !integration.requiresAuth) {
    return true; // No auth required or integration doesn't exist
  }

  // This would be implemented with actual environment variable checking
  // For now, return true as a placeholder
  return true;
};

/**
 * Default export for easy importing
 */
const integrationStatus = {
  CORE_PRODUCT_INTEGRATIONS,
  PREMIUM_ENGINE_INTEGRATIONS,
  MARKETPLACE_INTEGRATIONS,
  WORLD_GAME_INTEGRATIONS,
  BLOCKCHAIN_INTEGRATIONS,
  ALL_INTEGRATIONS,
  getLiveIntegrations,
  getPlannedIntegrations,
  getFutureOnlyIntegrations,
  getBlockedIntegrations,
  getIntegrationsByTier,
  getPublicFeatures,
  getIntegrationStatus,
  isIntegrationLive,
  isIntegrationPlanned,
  isIntegrationBlocked,
  shouldShowFeature,
  shouldShowBetaFeature,
  checkIntegrationHealth,
  validateRequiredEnvironmentVariables,
};

export default integrationStatus;
