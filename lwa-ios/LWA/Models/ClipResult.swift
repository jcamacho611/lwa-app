import Foundation

struct ClipResponse: Codable {
    let requestID: String
    let videoURL: String
    let status: String
    let sourcePlatform: String
    let processingSummary: ProcessingSummary
    let trendContext: [TrendItem]
    let clips: [ClipResult]

    enum CodingKeys: String, CodingKey {
        case requestID = "request_id"
        case videoURL = "video_url"
        case status
        case sourcePlatform = "source_platform"
        case processingSummary = "processing_summary"
        case trendContext = "trend_context"
        case clips
    }
}

struct ProcessingSummary: Codable {
    let planName: String
    let creditsRemaining: Int
    let estimatedTurnaround: String
    let recommendedNextStep: String
    let aiProvider: String
    let targetPlatform: String
    let trendUsed: String?
    let sourcesConsidered: [String]
    let processingMode: String
    let selectionStrategy: String
    let sourceTitle: String?
    let sourceDurationSeconds: Int?
    let assetsCreated: Int

    enum CodingKeys: String, CodingKey {
        case planName = "plan_name"
        case creditsRemaining = "credits_remaining"
        case estimatedTurnaround = "estimated_turnaround"
        case recommendedNextStep = "recommended_next_step"
        case aiProvider = "ai_provider"
        case targetPlatform = "target_platform"
        case trendUsed = "trend_used"
        case sourcesConsidered = "sources_considered"
        case processingMode = "processing_mode"
        case selectionStrategy = "selection_strategy"
        case sourceTitle = "source_title"
        case sourceDurationSeconds = "source_duration_seconds"
        case assetsCreated = "assets_created"
    }
}

struct JobCreatedResponse: Codable {
    let jobID: String
    let status: String
    let pollURL: String
    let message: String

    enum CodingKeys: String, CodingKey {
        case jobID = "job_id"
        case status
        case pollURL = "poll_url"
        case message
    }
}

struct JobStatusResponse: Codable {
    let jobID: String
    let status: String
    let message: String
    let createdAt: String
    let updatedAt: String
    let result: ClipResponse?
    let error: String?

    enum CodingKeys: String, CodingKey {
        case jobID = "job_id"
        case status
        case message
        case createdAt = "created_at"
        case updatedAt = "updated_at"
        case result
        case error
    }
}

struct TrendItem: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let source: String
    let detail: String
    let url: String?
}

struct TrendsResponse: Codable {
    let status: String
    let updatedAt: String
    let trends: [TrendItem]

    enum CodingKeys: String, CodingKey {
        case status
        case updatedAt = "updated_at"
        case trends
    }
}

struct ClipResult: Codable, Identifiable {
    let id: String
    let title: String
    let hook: String
    let caption: String
    let startTime: String
    let endTime: String
    let score: Int
    let format: String
    let clipURL: String?
    let transcriptExcerpt: String?

    enum CodingKeys: String, CodingKey {
        case id
        case title
        case hook
        case caption
        case startTime = "start_time"
        case endTime = "end_time"
        case score
        case format
        case clipURL = "clip_url"
        case transcriptExcerpt = "transcript_excerpt"
    }
}

struct SavedRun: Codable, Identifiable {
    let id: String
    let createdAt: Date
    let response: ClipResponse

    init(createdAt: Date = .now, response: ClipResponse) {
        self.id = response.requestID
        self.createdAt = createdAt
        self.response = response
    }
}
