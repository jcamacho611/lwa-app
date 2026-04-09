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
    let editedAssetsCreated: Int

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
        case editedAssetsCreated = "edited_assets_created"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        planName = try container.decode(String.self, forKey: .planName)
        creditsRemaining = try container.decode(Int.self, forKey: .creditsRemaining)
        estimatedTurnaround = try container.decode(String.self, forKey: .estimatedTurnaround)
        recommendedNextStep = try container.decode(String.self, forKey: .recommendedNextStep)
        aiProvider = try container.decode(String.self, forKey: .aiProvider)
        targetPlatform = try container.decode(String.self, forKey: .targetPlatform)
        trendUsed = try container.decodeIfPresent(String.self, forKey: .trendUsed)
        sourcesConsidered = try container.decode([String].self, forKey: .sourcesConsidered)
        processingMode = try container.decode(String.self, forKey: .processingMode)
        selectionStrategy = try container.decode(String.self, forKey: .selectionStrategy)
        sourceTitle = try container.decodeIfPresent(String.self, forKey: .sourceTitle)
        sourceDurationSeconds = try container.decodeIfPresent(Int.self, forKey: .sourceDurationSeconds)
        assetsCreated = try container.decodeIfPresent(Int.self, forKey: .assetsCreated) ?? 0
        editedAssetsCreated = try container.decodeIfPresent(Int.self, forKey: .editedAssetsCreated) ?? 0
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
    let rawClipURL: String?
    let editedClipURL: String?
    let transcriptExcerpt: String?
    let editProfile: String?
    let aspectRatio: String?

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
        case rawClipURL = "raw_clip_url"
        case editedClipURL = "edited_clip_url"
        case transcriptExcerpt = "transcript_excerpt"
        case editProfile = "edit_profile"
        case aspectRatio = "aspect_ratio"
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
