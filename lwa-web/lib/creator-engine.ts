export type CreatorEngineJobType = 
  | "clip_generation"
  | "hook_extraction"
  | "caption_generation"
  | "scoring"
  | "ranking"
  | "render_job"
  | "export_bundle";

export type CreatorEngineStatus = 
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "cancelled";

export type CreatorEngineJob = {
  id: string;
  type: CreatorEngineJobType;
  status: CreatorEngineStatus;
  userId?: string;
  sourceUrl?: string;
  sourceContent?: string;
  config?: Record<string, any>;
  result?: {
    clips?: ClipResult[];
    hooks?: HookResult[];
    captions?: CaptionResult[];
    scores?: ScoreResult[];
    rankings?: RankingResult[];
    renderJobs?: RenderJobResult[];
    exportBundle?: ExportBundleResult;
  };
  error?: string;
  progress?: number;
  stage?: string;
  createdAt: number;
  updatedAt: number;
  completedAt?: number;
};

export type ClipResult = {
  id: string;
  title: string;
  hook: string;
  caption: string;
  score: number;
  duration: number;
  timestamps: {
    start: number;
    end: number;
  };
  sourceUrl: string;
  previewUrl?: string;
  downloadUrl?: string;
  metadata?: Record<string, any>;
};

export type HookResult = {
  id: string;
  hook: string;
  score: number;
  category: "question" | "statement" | "shock" | "benefit" | "story";
  sourceTimestamp: number;
  confidence: number;
};

export type CaptionResult = {
  id: string;
  text: string;
  start: number;
  end: number;
  style: "caption" | "subtitle" | "overlay";
  confidence: number;
};

export type ScoreResult = {
  id: string;
  type: "viral" | "engagement" | "retention" | "quality";
  score: number;
  factors: Record<string, number>;
  explanation: string;
};

export type RankingResult = {
  id: string;
  clips: ClipResult[];
  ranking: "top" | "trending" | "recommended" | "quality";
  criteria: string[];
};

export type RenderJobResult = {
  id: string;
  inputClipId: string;
  outputUrl?: string;
  status: "queued" | "processing" | "completed" | "failed";
  format: string;
  quality: string;
  effects?: string[];
  progress?: number;
  error?: string;
};

export type ExportBundleResult = {
  id: string;
  clips: ClipResult[];
  metadata: {
    totalDuration: number;
    formats: string[];
    platform: string;
    exportDate: string;
  };
  downloadUrl?: string;
  size?: number;
};

export type CreatorEngineConfig = {
  maxClips: number;
  minClipDuration: number;
  maxClipDuration: number;
  hookCategories: string[];
  captionStyles: string[];
  scoringWeights: Record<string, number>;
  renderFormats: string[];
  exportFormats: string[];
};

// Creator Engine Implementation
export class CreatorEngine {
  private jobs: Map<string, CreatorEngineJob> = new Map();
  private config: CreatorEngineConfig;
  private eventCallbacks: Map<string, (job: CreatorEngineJob) => void> = new Map();

  constructor(config?: Partial<CreatorEngineConfig>) {
    this.config = {
      maxClips: 10,
      minClipDuration: 15,
      maxClipDuration: 60,
      hookCategories: ["question", "statement", "shock", "benefit", "story"],
      captionStyles: ["caption", "subtitle", "overlay"],
      scoringWeights: {
        viral: 0.4,
        engagement: 0.3,
        retention: 0.2,
        quality: 0.1,
      },
      renderFormats: ["mp4", "webm", "gif"],
      exportFormats: ["zip", "json", "csv"],
      ...config,
    };
  }

  // Job Management
  createJob(
    type: CreatorEngineJobType,
    userId?: string,
    sourceUrl?: string,
    config?: Record<string, any>
  ): string {
    const jobId = `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const job: CreatorEngineJob = {
      id: jobId,
      type,
      status: "pending",
      userId,
      sourceUrl,
      config,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    this.jobs.set(jobId, job);
    this.notifyEvent(job);
    return jobId;
  }

  getJob(jobId: string): CreatorEngineJob | undefined {
    return this.jobs.get(jobId);
  }

  getJobsByUser(userId: string): CreatorEngineJob[] {
    return Array.from(this.jobs.values()).filter(job => job.userId === userId);
  }

  getJobsByType(type: CreatorEngineJobType): CreatorEngineJob[] {
    return Array.from(this.jobs.values()).filter(job => job.type === type);
  }

  getAllJobs(): CreatorEngineJob[] {
    return Array.from(this.jobs.values());
  }

  updateJob(jobId: string, updates: Partial<CreatorEngineJob>): boolean {
    const job = this.jobs.get(jobId);
    if (!job) return false;

    const updatedJob = { ...job, ...updates, updatedAt: Date.now() };
    if (updates.status === "completed" && !job.completedAt) {
      updatedJob.completedAt = Date.now();
    }
    
    this.jobs.set(jobId, updatedJob);
    this.notifyEvent(updatedJob);
    return true;
  }

  deleteJob(jobId: string): boolean {
    const deleted = this.jobs.delete(jobId);
    if (deleted) {
      this.eventCallbacks.delete(jobId);
    }
    return deleted;
  }

  // Event Management
  onJobEvent(jobId: string, callback: (job: CreatorEngineJob) => void): () => void {
    this.eventCallbacks.set(jobId, callback);
    return () => {
      this.eventCallbacks.delete(jobId);
    };
  }

  private notifyEvent(job: CreatorEngineJob): void {
    const callback = this.eventCallbacks.get(job.id);
    if (callback) {
      callback(job);
    }
  }

  // Core Processing Methods
  async processClipGeneration(jobId: string): Promise<void> {
    const job = this.getJob(jobId);
    if (!job || !job.sourceUrl) return;

    this.updateJob(jobId, { status: "processing", progress: 0, stage: "analyzing" });

    // Simulate processing stages
    await this.simulateProgress(jobId, 0, 25, "analyzing");
    await this.simulateProgress(jobId, 25, 50, "extracting");
    await this.simulateProgress(jobId, 50, 75, "generating");
    await this.simulateProgress(jobId, 75, 90, "optimizing");

    // Generate mock clip results
    const clips = this.generateMockClips(job.sourceUrl);
    
    this.updateJob(jobId, {
      status: "completed",
      progress: 100,
      stage: "completed",
      result: { clips },
    });
  }

  async processHookExtraction(jobId: string): Promise<void> {
    const job = this.getJob(jobId);
    if (!job || !job.sourceContent) return;

    this.updateJob(jobId, { status: "processing", progress: 0, stage: "analyzing" });

    await this.simulateProgress(jobId, 0, 33, "scanning");
    await this.simulateProgress(jobId, 33, 66, "extracting");
    await this.simulateProgress(jobId, 66, 90, "scoring");

    const hooks = this.generateMockHooks(job.sourceContent);
    
    this.updateJob(jobId, {
      status: "completed",
      progress: 100,
      stage: "completed",
      result: { hooks },
    });
  }

  async processCaptionGeneration(jobId: string): Promise<void> {
    const job = this.getJob(jobId);
    if (!job || !job.sourceUrl) return;

    this.updateJob(jobId, { status: "processing", progress: 0, stage: "transcribing" });

    await this.simulateProgress(jobId, 0, 40, "transcribing");
    await this.simulateProgress(jobId, 40, 70, "generating");
    await this.simulateProgress(jobId, 70, 90, "formatting");

    const captions = this.generateMockCaptions();
    
    this.updateJob(jobId, {
      status: "completed",
      progress: 100,
      stage: "completed",
      result: { captions },
    });
  }

  async processScoring(jobId: string): Promise<void> {
    const job = this.getJob(jobId);
    if (!job || !job.sourceContent) return;

    this.updateJob(jobId, { status: "processing", progress: 0, stage: "analyzing" });

    await this.simulateProgress(jobId, 0, 50, "scoring");
    await this.simulateProgress(jobId, 50, 80, "ranking");
    await this.simulateProgress(jobId, 80, 90, "finalizing");

    const scores = this.generateMockScores();
    
    this.updateJob(jobId, {
      status: "completed",
      progress: 100,
      stage: "completed",
      result: { scores },
    });
  }

  async processRenderJob(jobId: string): Promise<void> {
    const job = this.getJob(jobId);
    if (!job || !job.config?.clipId) return;

    this.updateJob(jobId, { status: "processing", progress: 0, stage: "queued" });

    await this.simulateProgress(jobId, 0, 20, "queued");
    await this.simulateProgress(jobId, 20, 40, "rendering");
    await this.simulateProgress(jobId, 40, 80, "encoding");
    await this.simulateProgress(jobId, 80, 95, "uploading");

    const renderJobs = this.generateMockRenderJobs(job.config.clipId);
    
    this.updateJob(jobId, {
      status: "completed",
      progress: 100,
      stage: "completed",
      result: { renderJobs },
    });
  }

  async processExportBundle(jobId: string): Promise<void> {
    const job = this.getJob(jobId);
    if (!job || !job.config?.clipIds) return;

    this.updateJob(jobId, { status: "processing", progress: 0, stage: "collecting" });

    await this.simulateProgress(jobId, 0, 30, "collecting");
    await this.simulateProgress(jobId, 30, 60, "packaging");
    await this.simulateProgress(jobId, 60, 85, "compressing");
    await this.simulateProgress(jobId, 85, 95, "uploading");

    const exportBundle = this.generateMockExportBundle(job.config.clipIds);
    
    this.updateJob(jobId, {
      status: "completed",
      progress: 100,
      stage: "completed",
      result: { exportBundle },
    });
  }

  // Utility Methods
  private async simulateProgress(jobId: string, startProgress: number, endProgress: number, stage: string): Promise<void> {
    const duration = 500 + Math.random() * 1000; // 0.5-1.5 seconds
    const steps = 5;
    const stepDuration = duration / steps;
    const stepProgress = (endProgress - startProgress) / steps;

    for (let i = 0; i < steps; i++) {
      await new Promise(resolve => setTimeout(resolve, stepDuration));
      const currentProgress = startProgress + (stepProgress * (i + 1));
      this.updateJob(jobId, { progress: currentProgress, stage });
    }
  }

  private generateMockClips(sourceUrl: string): ClipResult[] {
    const clipCount = Math.floor(Math.random() * 5) + 3; // 3-7 clips
    const clips: ClipResult[] = [];

    for (let i = 0; i < clipCount; i++) {
      clips.push({
        id: `clip_${Date.now()}_${i}`,
        title: `Generated Clip ${i + 1}`,
        hook: `This is hook ${i + 1} - engaging and viral!`,
        caption: `Caption for clip ${i + 1} with call to action`,
        score: 70 + Math.floor(Math.random() * 30), // 70-99
        duration: 15 + Math.floor(Math.random() * 45), // 15-60 seconds
        timestamps: {
          start: i * 30,
          end: (i + 1) * 30,
        },
        sourceUrl,
        previewUrl: `${sourceUrl}/preview_${i}.mp4`,
        downloadUrl: `${sourceUrl}/download_${i}.mp4`,
        metadata: {
          platform: "tiktok",
          category: "entertainment",
          tags: ["viral", "trending", "engaging"],
        },
      });
    }

    return clips;
  }

  private generateMockHooks(content: string): HookResult[] {
    const hooks: HookResult[] = [];
    const hookCount = Math.floor(Math.random() * 8) + 5; // 5-12 hooks

    for (let i = 0; i < hookCount; i++) {
      hooks.push({
        id: `hook_${Date.now()}_${i}`,
        hook: `Hook ${i + 1}: ${content.substring(0, 50)}...`,
        score: 60 + Math.floor(Math.random() * 40), // 60-99
        category: ["question", "statement", "shock", "benefit", "story"][Math.floor(Math.random() * 5)] as any,
        sourceTimestamp: i * 10,
        confidence: 0.7 + Math.random() * 0.3, // 0.7-1.0
      });
    }

    return hooks;
  }

  private generateMockCaptions(): CaptionResult[] {
    const captions: CaptionResult[] = [];
    const captionCount = Math.floor(Math.random() * 20) + 10; // 10-30 captions

    for (let i = 0; i < captionCount; i++) {
      captions.push({
        id: `caption_${Date.now()}_${i}`,
        text: `Caption text ${i + 1}`,
        start: i * 5,
        end: (i + 1) * 5,
        style: ["caption", "subtitle", "overlay"][Math.floor(Math.random() * 3)] as any,
        confidence: 0.8 + Math.random() * 0.2, // 0.8-1.0
      });
    }

    return captions;
  }

  private generateMockScores(): ScoreResult[] {
    return [
      {
        id: `score_${Date.now()}_viral`,
        type: "viral",
        score: 75 + Math.floor(Math.random() * 25), // 75-99
        factors: {
          hook: 80,
          content: 75,
          timing: 70,
          engagement: 85,
        },
        explanation: "Strong viral potential with engaging hook and timing",
      },
      {
        id: `score_${Date.now()}_engagement`,
        type: "engagement",
        score: 70 + Math.floor(Math.random() * 30), // 70-99
        factors: {
          visual: 80,
          audio: 75,
          content: 70,
          call_to_action: 85,
        },
        explanation: "High engagement potential with strong visual elements",
      },
      {
        id: `score_${Date.now()}_retention`,
        type: "retention",
        score: 65 + Math.floor(Math.random() * 35), // 65-99
        factors: {
          pacing: 75,
          content: 70,
          length: 80,
          relevance: 85,
        },
        explanation: "Good retention with optimal pacing and length",
      },
      {
        id: `score_${Date.now()}_quality`,
        type: "quality",
        score: 80 + Math.floor(Math.random() * 20), // 80-99
        factors: {
          technical: 85,
          content: 80,
          production: 75,
          overall: 90,
        },
        explanation: "High quality production and content",
      },
    ];
  }

  private generateMockRenderJobs(clipId: string): RenderJobResult[] {
    const formats = this.config.renderFormats;
    return formats.map(format => ({
      id: `render_${Date.now()}_${format}`,
      inputClipId: clipId,
      outputUrl: `https://cdn.example.com/rendered/${clipId}.${format}`,
      status: "completed" as const,
      format,
      quality: "high",
      effects: ["enhance", "optimize"],
      progress: 100,
    }));
  }

  private generateMockExportBundle(clipIds: string[]): ExportBundleResult {
    return {
      id: `bundle_${Date.now()}`,
      clips: clipIds.map(id => ({
        id,
        title: `Clip ${id}`,
        hook: "Generated hook",
        caption: "Generated caption",
        score: 85,
        duration: 30,
        timestamps: { start: 0, end: 30 },
        sourceUrl: "https://example.com/source.mp4",
      })),
      metadata: {
        totalDuration: clipIds.length * 30,
        formats: this.config.exportFormats,
        platform: "multi",
        exportDate: new Date().toISOString(),
      },
      downloadUrl: `https://cdn.example.com/bundles/bundle_${Date.now()}.zip`,
      size: 1024 * 1024 * (10 + Math.floor(Math.random() * 50)), // 10-60 MB
    };
  }

  // Batch Operations
  async processBatchJobs(jobIds: string[]): Promise<void> {
    const promises = jobIds.map(jobId => {
      const job = this.getJob(jobId);
      if (!job) return Promise.resolve();

      switch (job.type) {
        case "clip_generation":
          return this.processClipGeneration(jobId);
        case "hook_extraction":
          return this.processHookExtraction(jobId);
        case "caption_generation":
          return this.processCaptionGeneration(jobId);
        case "scoring":
          return this.processScoring(jobId);
        case "render_job":
          return this.processRenderJob(jobId);
        case "export_bundle":
          return this.processExportBundle(jobId);
        default:
          return Promise.resolve();
      }
    });

    await Promise.all(promises);
  }

  // Statistics
  getStatistics(): {
    totalJobs: number;
    completedJobs: number;
    failedJobs: number;
    averageProcessingTime: number;
    jobsByType: Record<CreatorEngineJobType, number>;
  } {
    const jobs = this.getAllJobs();
    const completedJobs = jobs.filter(job => job.status === "completed");
    const failedJobs = jobs.filter(job => job.status === "failed");
    
    const averageProcessingTime = completedJobs.length > 0
      ? completedJobs.reduce((sum, job) => {
          const processingTime = (job.completedAt || 0) - job.createdAt;
          return sum + processingTime;
        }, 0) / completedJobs.length
      : 0;

    const jobsByType = jobs.reduce((acc, job) => {
      acc[job.type] = (acc[job.type] || 0) + 1;
      return acc;
    }, {} as Record<CreatorEngineJobType, number>);

    return {
      totalJobs: jobs.length,
      completedJobs: completedJobs.length,
      failedJobs: failedJobs.length,
      averageProcessingTime,
      jobsByType,
    };
  }

  // Cleanup
  clearCompletedJobs(olderThan: number = 24 * 60 * 60 * 1000): number {
    const now = Date.now();
    const jobsToDelete: string[] = [];

    this.jobs.forEach((job, jobId) => {
      if (
        job.status === "completed" &&
        job.completedAt &&
        (now - job.completedAt) > olderThan
      ) {
        jobsToDelete.push(jobId);
      }
    });

    jobsToDelete.forEach(jobId => this.deleteJob(jobId));
    return jobsToDelete.length;
  }
}

// Singleton Instance
export const creatorEngine = new CreatorEngine();
