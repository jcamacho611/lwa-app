export type MarketplaceJobType = 
  | "content_creation"
  | "video_editing"
  | "graphic_design"
  | "copywriting"
  | "social_media_management"
  | "voice_over"
  | "translation"
  | "consulting";

export type CampaignType = 
  | "brand_awareness"
  | "product_launch"
  | "lead_generation"
  | "content_amplification"
  | "community_building"
  | "sales_promotion";

export type JobStatus = 
  | "draft"
  | "posted"
  | "bidding"
  | "assigned"
  | "in_progress"
  | "review"
  | "completed"
  | "cancelled"
  | "disputed";

export type CampaignStatus = 
  | "draft"
  | "active"
  | "paused"
  | "completed"
  | "cancelled";

export type MarketplaceJob = {
  id: string;
  type: MarketplaceJobType;
  status: JobStatus;
  title: string;
  description: string;
  clientId: string;
  creatorId?: string;
  budget: {
    minimum: number;
    maximum: number;
    currency: string;
  };
  requirements: {
    skills: string[];
    deliverables: string[];
    timeline: string;
    experience: string;
  };
  bids: Bid[];
  selectedBid?: Bid;
  createdAt: number;
  updatedAt: number;
  deadline?: number;
  tags: string[];
  category: string;
  location?: string;
  remote: boolean;
};

export type Bid = {
  id: string;
  jobId: string;
  creatorId: string;
  amount: number;
  currency: string;
  timeline: string;
  proposal: string;
  portfolio: string[];
  availability: string;
  status: "pending" | "accepted" | "rejected";
  createdAt: number;
};

export type Campaign = {
  id: string;
  type: CampaignType;
  status: CampaignStatus;
  name: string;
  description: string;
  clientId: string;
  budget: {
    total: number;
    spent: number;
    currency: string;
  };
  timeline: {
    start: number;
    end: number;
    duration: string;
  };
  objectives: string[];
  targetAudience: {
    demographics: string[];
    interests: string[];
    platforms: string[];
  };
  content: {
    strategy: string;
    requirements: string[];
    deliverables: string[];
  };
  jobs: string[]; // Job IDs
  performance: {
    reach: number;
    engagement: number;
    conversions: number;
    roi: number;
  };
  createdAt: number;
  updatedAt: number;
};

export type CreatorProfile = {
  id: string;
  name: string;
  bio: string;
  skills: string[];
  portfolio: string[];
  experience: string;
  rating: number;
  reviews: number;
  completedJobs: number;
  earnings: number;
  availability: string;
  rates: {
    hourly: number;
    project: number;
    currency: string;
  };
  specialties: MarketplaceJobType[];
  languages: string[];
  location?: string;
  remote: boolean;
  verified: boolean;
  responseTime: number; // hours
};

export type MarketplaceConfig = {
  commissionRate: number;
  minimumBid: number;
  maximumBid: number;
  disputeResolutionTime: number;
  paymentTerms: string;
  qualityThreshold: number;
};

// Marketplace Engine Implementation
export class MarketplaceEngine {
  private jobs: Map<string, MarketplaceJob> = new Map();
  private campaigns: Map<string, Campaign> = new Map();
  private creators: Map<string, CreatorProfile> = new Map();
  private config: MarketplaceConfig;
  private eventCallbacks: Map<string, (event: MarketplaceEvent) => void> = new Map();

  constructor(config?: Partial<MarketplaceConfig>) {
    this.config = {
      commissionRate: 0.15, // 15%
      minimumBid: 10,
      maximumBid: 10000,
      disputeResolutionTime: 7 * 24 * 60 * 60 * 1000, // 7 days
      paymentTerms: "50% upfront, 50% on completion",
      qualityThreshold: 4.0,
      ...config,
    };

    this.initializeMockData();
  }

  private initializeMockData(): void {
    // Initialize mock creators
    const mockCreators: CreatorProfile[] = [
      {
        id: "creator_1",
        name: "Sarah Chen",
        bio: "Professional video editor with 5+ years of experience",
        skills: ["Video Editing", "Color Grading", "Motion Graphics"],
        portfolio: ["https://portfolio.example.com/sarah1", "https://portfolio.example.com/sarah2"],
        experience: "5+ years",
        rating: 4.8,
        reviews: 127,
        completedJobs: 89,
        earnings: 45000,
        availability: "Full-time",
        rates: { hourly: 45, project: 500, currency: "USD" },
        specialties: ["video_editing", "content_creation"],
        languages: ["English", "Mandarin"],
        remote: true,
        verified: true,
        responseTime: 2,
      },
      {
        id: "creator_2",
        name: "Mike Johnson",
        bio: "Creative graphic designer specializing in branding",
        skills: ["Graphic Design", "Branding", "Illustration"],
        portfolio: ["https://portfolio.example.com/mike1", "https://portfolio.example.com/mike2"],
        experience: "3+ years",
        rating: 4.6,
        reviews: 89,
        completedJobs: 67,
        earnings: 32000,
        availability: "Part-time",
        rates: { hourly: 35, project: 400, currency: "USD" },
        specialties: ["graphic_design", "content_creation"],
        languages: ["English"],
        remote: true,
        verified: true,
        responseTime: 4,
      },
    ];

    mockCreators.forEach(creator => {
      this.creators.set(creator.id, creator);
    });
  }

  // Job Management
  createJob(
    type: MarketplaceJobType,
    title: string,
    description: string,
    clientId: string,
    budget: MarketplaceJob["budget"],
    requirements: MarketplaceJob["requirements"],
    options?: {
      tags?: string[];
      category?: string;
      location?: string;
      remote?: boolean;
      deadline?: number;
    }
  ): string {
    const jobId = `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const job: MarketplaceJob = {
      id: jobId,
      type,
      status: "draft",
      title,
      description,
      clientId,
      budget,
      requirements,
      bids: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
      tags: options?.tags || [],
      category: options?.category || "general",
      location: options?.location,
      remote: options?.remote ?? true,
      deadline: options?.deadline,
    };

    this.jobs.set(jobId, job);
    this.notifyEvent({ type: "job_created", data: job });
    return jobId;
  }

  getJob(jobId: string): MarketplaceJob | undefined {
    return this.jobs.get(jobId);
  }

  getJobsByClient(clientId: string): MarketplaceJob[] {
    return Array.from(this.jobs.values()).filter(job => job.clientId === clientId);
  }

  getJobsByCreator(creatorId: string): MarketplaceJob[] {
    return Array.from(this.jobs.values()).filter(job => job.creatorId === creatorId);
  }

  getJobsByStatus(status: JobStatus): MarketplaceJob[] {
    return Array.from(this.jobs.values()).filter(job => job.status === status);
  }

  getJobsByType(type: MarketplaceJobType): MarketplaceJob[] {
    return Array.from(this.jobs.values()).filter(job => job.type === type);
  }

  getAllJobs(): MarketplaceJob[] {
    return Array.from(this.jobs.values());
  }

  updateJob(jobId: string, updates: Partial<MarketplaceJob>): boolean {
    const job = this.jobs.get(jobId);
    if (!job) return false;

    const updatedJob = { ...job, ...updates, updatedAt: Date.now() };
    this.jobs.set(jobId, updatedJob);
    this.notifyEvent({ type: "job_updated", data: updatedJob });
    return true;
  }

  deleteJob(jobId: string): boolean {
    const deleted = this.jobs.delete(jobId);
    if (deleted) {
      this.notifyEvent({ type: "job_deleted", data: { id: jobId } });
    }
    return deleted;
  }

  // Bid Management
  createBid(jobId: string, creatorId: string, amount: number, timeline: string, proposal: string): string {
    const job = this.getJob(jobId);
    if (!job) throw new Error("Job not found");

    const bidId = `bid_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const bid: Bid = {
      id: bidId,
      jobId,
      creatorId,
      amount,
      currency: job.budget.currency,
      timeline,
      proposal,
      portfolio: [],
      availability: "Available",
      status: "pending",
      createdAt: Date.now(),
    };

    job.bids.push(bid);
    this.updateJob(jobId, { bids: job.bids });
    this.notifyEvent({ type: "bid_created", data: bid });
    return bidId;
  }

  acceptBid(jobId: string, bidId: string): boolean {
    const job = this.getJob(jobId);
    if (!job) return false;

    const bid = job.bids.find(b => b.id === bidId);
    if (!bid) return false;

    // Reject all other bids
    job.bids.forEach(b => {
      if (b.id !== bidId) {
        b.status = "rejected";
      }
    });

    bid.status = "accepted";
    job.selectedBid = bid;
    job.creatorId = bid.creatorId;
    job.status = "assigned";

    this.updateJob(jobId, { 
      bids: job.bids, 
      selectedBid: bid, 
      creatorId: bid.creatorId, 
      status: "assigned" 
    });

    this.notifyEvent({ type: "bid_accepted", data: { job, bid } });
    return true;
  }

  rejectBid(jobId: string, bidId: string): boolean {
    const job = this.getJob(jobId);
    if (!job) return false;

    const bid = job.bids.find(b => b.id === bidId);
    if (!bid) return false;

    bid.status = "rejected";
    this.updateJob(jobId, { bids: job.bids });
    this.notifyEvent({ type: "bid_rejected", data: { job, bid } });
    return true;
  }

  // Campaign Management
  createCampaign(
    type: CampaignType,
    name: string,
    description: string,
    clientId: string,
    budget: Campaign["budget"],
    timeline: Campaign["timeline"],
    objectives: string[],
    targetAudience: Campaign["targetAudience"],
    content: Campaign["content"]
  ): string {
    const campaignId = `campaign_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const campaign: Campaign = {
      id: campaignId,
      type,
      status: "draft",
      name,
      description,
      clientId,
      budget,
      timeline,
      objectives,
      targetAudience,
      content,
      jobs: [],
      performance: {
        reach: 0,
        engagement: 0,
        conversions: 0,
        roi: 0,
      },
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    this.campaigns.set(campaignId, campaign);
    this.notifyEvent({ type: "campaign_created", data: campaign });
    return campaignId;
  }

  getCampaign(campaignId: string): Campaign | undefined {
    return this.campaigns.get(campaignId);
  }

  getCampaignsByClient(clientId: string): Campaign[] {
    return Array.from(this.campaigns.values()).filter(campaign => campaign.clientId === clientId);
  }

  getAllCampaigns(): Campaign[] {
    return Array.from(this.campaigns.values());
  }

  updateCampaign(campaignId: string, updates: Partial<Campaign>): boolean {
    const campaign = this.campaigns.get(campaignId);
    if (!campaign) return false;

    const updatedCampaign = { ...campaign, ...updates, updatedAt: Date.now() };
    this.campaigns.set(campaignId, updatedCampaign);
    this.notifyEvent({ type: "campaign_updated", data: updatedCampaign });
    return true;
  }

  // Creator Profile Management
  getCreator(creatorId: string): CreatorProfile | undefined {
    return this.creators.get(creatorId);
  }

  getAllCreators(): CreatorProfile[] {
    return Array.from(this.creators.values());
  }

  getCreatorsBySpecialty(specialty: MarketplaceJobType): CreatorProfile[] {
    return Array.from(this.creators.values()).filter(creator => 
      creator.specialties.includes(specialty)
    );
  }

  getCreatorsByRating(minRating: number): CreatorProfile[] {
    return Array.from(this.creators.values()).filter(creator => creator.rating >= minRating);
  }

  updateCreator(creatorId: string, updates: Partial<CreatorProfile>): boolean {
    const creator = this.creators.get(creatorId);
    if (!creator) return false;

    const updatedCreator = { ...creator, ...updates };
    this.creators.set(creatorId, updatedCreator);
    this.notifyEvent({ type: "creator_updated", data: updatedCreator });
    return true;
  }

  // Search and Discovery
  searchJobs(criteria: {
    type?: MarketplaceJobType;
    status?: JobStatus;
    category?: string;
    minBudget?: number;
    maxBudget?: number;
    tags?: string[];
    remote?: boolean;
  }): MarketplaceJob[] {
    return Array.from(this.jobs.values()).filter(job => {
      if (criteria.type && job.type !== criteria.type) return false;
      if (criteria.status && job.status !== criteria.status) return false;
      if (criteria.category && job.category !== criteria.category) return false;
      if (criteria.minBudget && job.budget.minimum < criteria.minBudget) return false;
      if (criteria.maxBudget && job.budget.maximum > criteria.maxBudget) return false;
      if (criteria.tags && !criteria.tags.every(tag => job.tags.includes(tag))) return false;
      if (criteria.remote !== undefined && job.remote !== criteria.remote) return false;
      return true;
    });
  }

  searchCreators(criteria: {
    specialties?: MarketplaceJobType[];
    minRating?: number;
    maxRate?: number;
    remote?: boolean;
    verified?: boolean;
    location?: string;
  }): CreatorProfile[] {
    return Array.from(this.creators.values()).filter(creator => {
      if (criteria.specialties && !criteria.specialties.some(specialty => creator.specialties.includes(specialty))) return false;
      if (criteria.minRating && creator.rating < criteria.minRating) return false;
      if (criteria.maxRate && creator.rates.hourly > criteria.maxRate) return false;
      if (criteria.remote !== undefined && creator.remote !== criteria.remote) return false;
      if (criteria.verified && !creator.verified) return false;
      if (criteria.location && creator.location !== criteria.location) return false;
      return true;
    });
  }

  // Analytics and Statistics
  getMarketplaceStatistics(): {
    totalJobs: number;
    activeJobs: number;
    completedJobs: number;
    totalCampaigns: number;
    activeCampaigns: number;
    totalCreators: number;
    verifiedCreators: number;
    averageJobBudget: number;
    totalVolume: number;
    jobsByType: Record<MarketplaceJobType, number>;
    jobsByStatus: Record<JobStatus, number>;
    campaignsByType: Record<CampaignType, number>;
    topCreators: CreatorProfile[];
  } {
    const jobs = this.getAllJobs();
    const campaigns = this.getAllCampaigns();
    const creators = this.getAllCreators();

    const activeJobs = jobs.filter(job => ["posted", "bidding", "assigned", "in_progress"].includes(job.status));
    const completedJobs = jobs.filter(job => job.status === "completed");
    const activeCampaigns = campaigns.filter(campaign => campaign.status === "active");
    const verifiedCreators = creators.filter(creator => creator.verified);

    const averageJobBudget = jobs.length > 0
      ? jobs.reduce((sum, job) => sum + (job.budget.minimum + job.budget.maximum) / 2, 0) / jobs.length
      : 0;

    const totalVolume = jobs.reduce((sum, job) => {
      if (job.selectedBid) {
        return sum + job.selectedBid.amount;
      }
      return sum;
    }, 0);

    const jobsByType = jobs.reduce((acc, job) => {
      acc[job.type] = (acc[job.type] || 0) + 1;
      return acc;
    }, {} as Record<MarketplaceJobType, number>);

    const jobsByStatus = jobs.reduce((acc, job) => {
      acc[job.status] = (acc[job.status] || 0) + 1;
      return acc;
    }, {} as Record<JobStatus, number>);

    const campaignsByType = campaigns.reduce((acc, campaign) => {
      acc[campaign.type] = (acc[campaign.type] || 0) + 1;
      return acc;
    }, {} as Record<CampaignType, number>);

    const topCreators = creators
      .sort((a, b) => b.rating - a.rating)
      .slice(0, 10);

    return {
      totalJobs: jobs.length,
      activeJobs: activeJobs.length,
      completedJobs: completedJobs.length,
      totalCampaigns: campaigns.length,
      activeCampaigns: activeCampaigns.length,
      totalCreators: creators.length,
      verifiedCreators: verifiedCreators.length,
      averageJobBudget,
      totalVolume,
      jobsByType,
      jobsByStatus,
      campaignsByType,
      topCreators,
    };
  }

  // Event Management
  onEvent(eventType: string, callback: (event: MarketplaceEvent) => void): () => void {
    const callbackId = `${eventType}_${Date.now()}`;
    this.eventCallbacks.set(callbackId, callback);
    return () => {
      this.eventCallbacks.delete(callbackId);
    };
  }

  private notifyEvent(event: MarketplaceEvent): void {
    this.eventCallbacks.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error("Error in marketplace event callback:", error);
      }
    });
  }

  // Quality Control
  validateJob(jobId: string): { valid: boolean; issues: string[] } {
    const job = this.getJob(jobId);
    if (!job) return { valid: false, issues: ["Job not found"] };

    const issues: string[] = [];

    if (!job.title || job.title.length < 10) {
      issues.push("Title must be at least 10 characters");
    }

    if (!job.description || job.description.length < 50) {
      issues.push("Description must be at least 50 characters");
    }

    if (job.budget.minimum < this.config.minimumBid) {
      issues.push(`Minimum budget must be at least ${this.config.minimumBid}`);
    }

    if (job.budget.maximum > this.config.maximumBid) {
      issues.push(`Maximum budget cannot exceed ${this.config.maximumBid}`);
    }

    if (job.budget.minimum > job.budget.maximum) {
      issues.push("Minimum budget cannot exceed maximum budget");
    }

    if (!job.requirements.skills || job.requirements.skills.length === 0) {
      issues.push("At least one skill requirement must be specified");
    }

    if (!job.requirements.deliverables || job.requirements.deliverables.length === 0) {
      issues.push("At least one deliverable must be specified");
    }

    return { valid: issues.length === 0, issues };
  }

  validateCreator(creatorId: string): { valid: boolean; issues: string[] } {
    const creator = this.getCreator(creatorId);
    if (!creator) return { valid: false, issues: ["Creator not found"] };

    const issues: string[] = [];

    if (!creator.name || creator.name.length < 2) {
      issues.push("Name must be at least 2 characters");
    }

    if (!creator.bio || creator.bio.length < 20) {
      issues.push("Bio must be at least 20 characters");
    }

    if (!creator.skills || creator.skills.length === 0) {
      issues.push("At least one skill must be specified");
    }

    if (!creator.portfolio || creator.portfolio.length === 0) {
      issues.push("At least one portfolio item must be provided");
    }

    if (creator.rating < this.config.qualityThreshold) {
      issues.push(`Rating must be at least ${this.config.qualityThreshold}`);
    }

    return { valid: issues.length === 0, issues };
  }
}

// Types
export type MarketplaceEvent = {
  type: string;
  data: any;
  timestamp?: number;
};

// Singleton Instance
export const marketplaceEngine = new MarketplaceEngine();
