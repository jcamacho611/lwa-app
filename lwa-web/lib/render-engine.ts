export type RenderJobType = 
  | "video_render"
  | "image_generation"
  | "blender_export"
  | "glb_conversion"
  | "effect_processing"
  | "format_conversion";

export type RenderStatus = 
  | "queued"
  | "processing"
  | "rendering"
  | "encoding"
  | "uploading"
  | "completed"
  | "failed"
  | "cancelled";

export type RenderJob = {
  id: string;
  type: RenderJobType;
  status: RenderStatus;
  userId?: string;
  input: {
    sourceUrl?: string;
    sourceFile?: string;
    parameters?: Record<string, any>;
    settings?: RenderSettings;
  };
  output?: {
    url?: string;
    file?: string;
    metadata?: Record<string, any>;
    thumbnail?: string;
  };
  progress?: number;
  stage?: string;
  error?: string;
  estimatedTime?: number;
  actualTime?: number;
  cost?: number;
  createdAt: number;
  startedAt?: number;
  completedAt?: number;
};

export type RenderSettings = {
  quality: "low" | "medium" | "high" | "ultra";
  format: string;
  resolution: string;
  frameRate?: number;
  bitrate?: number;
  compression?: number;
  effects?: string[];
  optimizations?: string[];
};

export type RenderQueue = {
  id: string;
  jobs: RenderJob[];
  maxConcurrent: number;
  priority: "low" | "medium" | "high" | "urgent";
  estimatedTotalTime: number;
};

export type RenderProvider = 
  | "local_gpu"
  | "cloud_render"
  | "blender_farm"
  | "stable_diffusion"
  | "runway_ml"
  | "midjourney_api";

export type AssetLifecycle = {
  id: string;
  type: "temporary" | "cache" | "permanent" | "archive";
  retention: number; // milliseconds
  autoDelete: boolean;
  costPerHour: number;
};

// Render Engine Implementation
export class RenderEngine {
  private jobs: Map<string, RenderJob> = new Map();
  private queues: Map<string, RenderQueue> = new Map();
  private providers: Map<RenderProvider, boolean> = new Map();
  private assetLifecycles: Map<string, AssetLifecycle> = new Map();
  private eventCallbacks: Map<string, (job: RenderJob) => void> = new Map();
  private processingJobs: Set<string> = new Set();

  constructor() {
    // Initialize providers
    this.providers.set("local_gpu", true);
    this.providers.set("cloud_render", true);
    this.providers.set("blender_farm", false);
    this.providers.set("stable_diffusion", true);
    this.providers.set("runway_ml", false);
    this.providers.set("midjourney_api", false);

    // Initialize default queue
    this.queues.set("default", {
      id: "default",
      jobs: [],
      maxConcurrent: 3,
      priority: "medium",
      estimatedTotalTime: 0,
    });

    // Initialize asset lifecycles
    this.setupAssetLifecycles();
  }

  private setupAssetLifecycles(): void {
    this.assetLifecycles.set("temporary", {
      id: "temporary",
      type: "temporary",
      retention: 60 * 60 * 1000, // 1 hour
      autoDelete: true,
      costPerHour: 0.01,
    });

    this.assetLifecycles.set("cache", {
      id: "cache",
      type: "cache",
      retention: 24 * 60 * 60 * 1000, // 24 hours
      autoDelete: true,
      costPerHour: 0.005,
    });

    this.assetLifecycles.set("permanent", {
      id: "permanent",
      type: "permanent",
      retention: 365 * 24 * 60 * 60 * 1000, // 1 year
      autoDelete: false,
      costPerHour: 0.02,
    });

    this.assetLifecycles.set("archive", {
      id: "archive",
      type: "archive",
      retention: 3 * 365 * 24 * 60 * 60 * 1000, // 3 years
      autoDelete: false,
      costPerHour: 0.001,
    });
  }

  // Job Management
  createJob(
    type: RenderJobType,
    input: RenderJob["input"],
    userId?: string,
    queueId: string = "default"
  ): string {
    const jobId = `render_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const job: RenderJob = {
      id: jobId,
      type,
      status: "queued",
      userId,
      input,
      createdAt: Date.now(),
      estimatedTime: this.estimateRenderTime(type, input),
    };

    this.jobs.set(jobId, job);
    
    // Add to queue
    const queue = this.queues.get(queueId);
    if (queue) {
      queue.jobs.push(job);
      queue.estimatedTotalTime += job.estimatedTime || 0;
    }

    this.notifyEvent(job);
    this.processQueue(queueId);
    return jobId;
  }

  getJob(jobId: string): RenderJob | undefined {
    return this.jobs.get(jobId);
  }

  getJobsByUser(userId: string): RenderJob[] {
    return Array.from(this.jobs.values()).filter(job => job.userId === userId);
  }

  getJobsByType(type: RenderJobType): RenderJob[] {
    return Array.from(this.jobs.values()).filter(job => job.type === type);
  }

  getJobsByStatus(status: RenderStatus): RenderJob[] {
    return Array.from(this.jobs.values()).filter(job => job.status === status);
  }

  getAllJobs(): RenderJob[] {
    return Array.from(this.jobs.values());
  }

  updateJob(jobId: string, updates: Partial<RenderJob>): boolean {
    const job = this.jobs.get(jobId);
    if (!job) return false;

    const updatedJob = { ...job, ...updates };
    if (updates.status === "completed" && !job.completedAt) {
      updatedJob.completedAt = Date.now();
      updatedJob.actualTime = updatedJob.completedAt - (job.startedAt || job.createdAt);
    }
    if (updates.status === "processing" && !job.startedAt) {
      updatedJob.startedAt = Date.now();
    }

    this.jobs.set(jobId, updatedJob);
    this.notifyEvent(updatedJob);
    return true;
  }

  deleteJob(jobId: string): boolean {
    const deleted = this.jobs.delete(jobId);
    if (deleted) {
      this.eventCallbacks.delete(jobId);
      this.processingJobs.delete(jobId);
    }
    return deleted;
  }

  // Queue Management
  private async processQueue(queueId: string): Promise<void> {
    const queue = this.queues.get(queueId);
    if (!queue) return;

    const processingCount = Array.from(this.processingJobs).filter(jobId => {
      const job = this.jobs.get(jobId);
      return job && job.status !== "completed" && job.status !== "failed";
    }).length;

    if (processingCount >= queue.maxConcurrent) return;

    const queuedJobs = queue.jobs.filter(job => job.status === "queued");
    const availableSlots = queue.maxConcurrent - processingCount;
    const jobsToProcess = queuedJobs.slice(0, availableSlots);

    for (const job of jobsToProcess) {
      this.processingJobs.add(job.id);
      this.processJob(job.id);
    }
  }

  private async processJob(jobId: string): Promise<void> {
    const job = this.getJob(jobId);
    if (!job) return;

    try {
      this.updateJob(jobId, { status: "processing", stage: "initializing" });

      switch (job.type) {
        case "video_render":
          await this.processVideoRender(jobId);
          break;
        case "image_generation":
          await this.processImageGeneration(jobId);
          break;
        case "blender_export":
          await this.processBlenderExport(jobId);
          break;
        case "glb_conversion":
          await this.processGLBConversion(jobId);
          break;
        case "effect_processing":
          await this.processEffectProcessing(jobId);
          break;
        case "format_conversion":
          await this.processFormatConversion(jobId);
          break;
      }
    } catch (error) {
      this.updateJob(jobId, {
        status: "failed",
        error: error instanceof Error ? error.message : "Unknown error",
      });
    } finally {
      this.processingJobs.delete(jobId);
      // Process next job in queue
      const queueId = this.findQueueForJob(jobId);
      if (queueId) {
        this.processQueue(queueId);
      }
    }
  }

  private async processVideoRender(jobId: string): Promise<void> {
    const job = this.getJob(jobId);
    if (!job) return;

    const stages = ["loading", "analyzing", "rendering", "encoding", "uploading"];
    const stageProgress = [0, 20, 60, 85, 95];

    for (let i = 0; i < stages.length; i++) {
      this.updateJob(jobId, {
        stage: stages[i],
        progress: stageProgress[i],
      });
      await this.simulateProcessing(1000 + Math.random() * 2000);
    }

    this.updateJob(jobId, {
      status: "completed",
      progress: 100,
      stage: "completed",
      output: {
        url: `https://cdn.example.com/renders/${job.id}.mp4`,
        thumbnail: `https://cdn.example.com/renders/${job.id}_thumb.jpg`,
        metadata: {
          duration: 30,
          resolution: "1920x1080",
          format: "mp4",
          size: "15.2MB",
        },
      },
      cost: this.calculateRenderCost(job.type, job.input),
    });
  }

  private async processImageGeneration(jobId: string): Promise<void> {
    const job = this.getJob(jobId);
    if (!job) return;

    this.updateJob(jobId, { stage: "generating", progress: 0 });
    await this.simulateProcessing(2000 + Math.random() * 3000);

    this.updateJob(jobId, {
      status: "completed",
      progress: 100,
      stage: "completed",
      output: {
        url: `https://cdn.example.com/renders/${job.id}.png`,
        metadata: {
          resolution: "1024x1024",
          format: "png",
          size: "2.4MB",
          model: "stable-diffusion-v2.1",
        },
      },
      cost: this.calculateRenderCost(job.type, job.input),
    });
  }

  private async processBlenderExport(jobId: string): Promise<void> {
    const job = this.getJob(jobId);
    if (!job) return;

    this.updateJob(jobId, { stage: "exporting", progress: 0 });
    await this.simulateProcessing(3000 + Math.random() * 5000);

    this.updateJob(jobId, {
      status: "completed",
      progress: 100,
      stage: "completed",
      output: {
        url: `https://cdn.example.com/renders/${job.id}.blend`,
        file: `/renders/${job.id}.blend`,
        metadata: {
          format: "blend",
          version: "5.1.1",
          size: "45.7MB",
          objects: 156,
        },
      },
      cost: this.calculateRenderCost(job.type, job.input),
    });
  }

  private async processGLBConversion(jobId: string): Promise<void> {
    const job = this.getJob(jobId);
    if (!job) return;

    this.updateJob(jobId, { stage: "converting", progress: 0 });
    await this.simulateProcessing(1500 + Math.random() * 2500);

    this.updateJob(jobId, {
      status: "completed",
      progress: 100,
      stage: "completed",
      output: {
        url: `https://cdn.example.com/renders/${job.id}.glb`,
        metadata: {
          format: "glb",
          size: "8.2MB",
          vertices: 45678,
          materials: 12,
        },
      },
      cost: this.calculateRenderCost(job.type, job.input),
    });
  }

  private async processEffectProcessing(jobId: string): Promise<void> {
    const job = this.getJob(jobId);
    if (!job) return;

    const effects = job.input.settings?.effects || [];
    for (let i = 0; i < effects.length; i++) {
      this.updateJob(jobId, {
        stage: `processing ${effects[i]}`,
        progress: (i / effects.length) * 100,
      });
      await this.simulateProcessing(500 + Math.random() * 1500);
    }

    this.updateJob(jobId, {
      status: "completed",
      progress: 100,
      stage: "completed",
      output: {
        url: `https://cdn.example.com/renders/${job.id}_processed.mp4`,
        metadata: {
          effects: effects,
          format: "mp4",
          size: "18.3MB",
        },
      },
      cost: this.calculateRenderCost(job.type, job.input),
    });
  }

  private async processFormatConversion(jobId: string): Promise<void> {
    const job = this.getJob(jobId);
    if (!job) return;

    const targetFormat = job.input.settings?.format || "mp4";
    this.updateJob(jobId, { stage: `converting to ${targetFormat}`, progress: 0 });
    await this.simulateProcessing(800 + Math.random() * 1200);

    this.updateJob(jobId, {
      status: "completed",
      progress: 100,
      stage: "completed",
      output: {
        url: `https://cdn.example.com/renders/${job.id}.${targetFormat}`,
        metadata: {
          format: targetFormat,
          size: "12.7MB",
          bitrate: "5000k",
        },
      },
      cost: this.calculateRenderCost(job.type, job.input),
    });
  }

  // Event Management
  onJobEvent(jobId: string, callback: (job: RenderJob) => void): () => void {
    this.eventCallbacks.set(jobId, callback);
    return () => {
      this.eventCallbacks.delete(jobId);
    };
  }

  private notifyEvent(job: RenderJob): void {
    const callback = this.eventCallbacks.get(job.id);
    if (callback) {
      callback(job);
    }
  }

  // Utility Methods
  private estimateRenderTime(type: RenderJobType, input: RenderJob["input"]): number {
    const baseTimes = {
      video_render: 30000, // 30 seconds
      image_generation: 5000, // 5 seconds
      blender_export: 20000, // 20 seconds
      glb_conversion: 8000, // 8 seconds
      effect_processing: 10000, // 10 seconds
      format_conversion: 3000, // 3 seconds
    };

    let time = baseTimes[type] || 10000;

    // Adjust based on quality
    if (input.settings?.quality) {
      const qualityMultipliers = {
        low: 0.5,
        medium: 1,
        high: 2,
        ultra: 4,
      };
      time *= qualityMultipliers[input.settings.quality] || 1;
    }

    // Adjust based on resolution
    if (input.settings?.resolution) {
      const resolutionMultipliers: Record<string, number> = {
        "720p": 0.5,
        "1080p": 1,
        "4K": 4,
        "8K": 8,
      };
      time *= resolutionMultipliers[input.settings.resolution] || 1;
    }

    return time;
  }

  private calculateRenderCost(type: RenderJobType, input: RenderJob["input"]): number {
    const baseCosts = {
      video_render: 0.10,
      image_generation: 0.02,
      blender_export: 0.05,
      glb_conversion: 0.03,
      effect_processing: 0.04,
      format_conversion: 0.01,
    };

    let cost = baseCosts[type] || 0.05;

    // Adjust based on quality
    if (input.settings?.quality) {
      const qualityMultipliers = {
        low: 0.5,
        medium: 1,
        high: 2,
        ultra: 4,
      };
      cost *= qualityMultipliers[input.settings.quality] || 1;
    }

    return cost;
  }

  private async simulateProcessing(duration: number): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, duration));
  }

  private findQueueForJob(jobId: string): string | undefined {
    for (const [queueId, queue] of this.queues) {
      if (queue.jobs.some(job => job.id === jobId)) {
        return queueId;
      }
    }
    return undefined;
  }

  // Asset Lifecycle Management
  setAssetLifecycle(assetId: string, lifecycle: AssetLifecycle): void {
    this.assetLifecycles.set(assetId, lifecycle);
  }

  getAssetLifecycle(assetId: string): AssetLifecycle | undefined {
    return this.assetLifecycles.get(assetId);
  }

  cleanupExpiredAssets(): number {
    const now = Date.now();
    let cleaned = 0;

    this.assetLifecycles.forEach((lifecycle, assetId) => {
      if (lifecycle.autoDelete) {
        const asset = this.jobs.get(assetId);
        if (asset && asset.completedAt) {
          const age = now - asset.completedAt;
          if (age > lifecycle.retention) {
            this.deleteJob(assetId);
            cleaned++;
          }
        }
      }
    });

    return cleaned;
  }

  // Statistics
  getStatistics(): {
    totalJobs: number;
    completedJobs: number;
    failedJobs: number;
    processingJobs: number;
    queuedJobs: number;
    averageRenderTime: number;
    totalCost: number;
    jobsByType: Record<RenderJobType, number>;
    jobsByStatus: Record<RenderStatus, number>;
    providerStatus: Record<RenderProvider, boolean>;
  } {
    const jobs = this.getAllJobs();
    const completedJobs = jobs.filter(job => job.status === "completed");
    const failedJobs = jobs.filter(job => job.status === "failed");
    const processingJobs = jobs.filter(job => job.status === "processing");
    const queuedJobs = jobs.filter(job => job.status === "queued");

    const averageRenderTime = completedJobs.length > 0
      ? completedJobs.reduce((sum, job) => sum + (job.actualTime || 0), 0) / completedJobs.length
      : 0;

    const totalCost = jobs.reduce((sum, job) => sum + (job.cost || 0), 0);

    const jobsByType = jobs.reduce((acc, job) => {
      acc[job.type] = (acc[job.type] || 0) + 1;
      return acc;
    }, {} as Record<RenderJobType, number>);

    const jobsByStatus = jobs.reduce((acc, job) => {
      acc[job.status] = (acc[job.status] || 0) + 1;
      return acc;
    }, {} as Record<RenderStatus, number>);

    const providerStatus: Record<RenderProvider, boolean> = {
      local_gpu: this.providers.get("local_gpu") || false,
      cloud_render: this.providers.get("cloud_render") || false,
      blender_farm: this.providers.get("blender_farm") || false,
      stable_diffusion: this.providers.get("stable_diffusion") || false,
      runway_ml: this.providers.get("runway_ml") || false,
      midjourney_api: this.providers.get("midjourney_api") || false,
    };

    return {
      totalJobs: jobs.length,
      completedJobs: completedJobs.length,
      failedJobs: failedJobs.length,
      processingJobs: processingJobs.length,
      queuedJobs: queuedJobs.length,
      averageRenderTime,
      totalCost,
      jobsByType,
      jobsByStatus,
      providerStatus,
    };
  }

  // Queue Management
  createQueue(id: string, maxConcurrent: number = 3, priority: "low" | "medium" | "high" | "urgent" = "medium"): void {
    this.queues.set(id, {
      id,
      jobs: [],
      maxConcurrent,
      priority,
      estimatedTotalTime: 0,
    });
  }

  deleteQueue(id: string): boolean {
    return this.queues.delete(id);
  }

  getQueue(id: string): RenderQueue | undefined {
    return this.queues.get(id);
  }

  getAllQueues(): RenderQueue[] {
    return Array.from(this.queues.values());
  }
}

// Singleton Instance
export const renderEngine = new RenderEngine();
