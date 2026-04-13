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
    struct FeatureFlags: Codable {
        let clipLimit: Int
        let altHooks: Bool
        let campaignMode: Bool
        let packagingProfiles: Bool
        let historyLimit: Int
        let premiumExports: Bool
        let priorityProcessing: Bool

        enum CodingKeys: String, CodingKey {
            case clipLimit = "clip_limit"
            case altHooks = "alt_hooks"
            case campaignMode = "campaign_mode"
            case packagingProfiles = "packaging_profiles"
            case historyLimit = "history_limit"
            case premiumExports = "premium_exports"
            case priorityProcessing = "priority_processing"
        }

        init(from decoder: Decoder) throws {
            let container = try decoder.container(keyedBy: CodingKeys.self)
            clipLimit = try container.decodeIfPresent(Int.self, forKey: .clipLimit) ?? 3
            altHooks = try container.decodeIfPresent(Bool.self, forKey: .altHooks) ?? false
            campaignMode = try container.decodeIfPresent(Bool.self, forKey: .campaignMode) ?? false
            packagingProfiles = try container.decodeIfPresent(Bool.self, forKey: .packagingProfiles) ?? false
            historyLimit = try container.decodeIfPresent(Int.self, forKey: .historyLimit) ?? 10
            premiumExports = try container.decodeIfPresent(Bool.self, forKey: .premiumExports) ?? false
            priorityProcessing = try container.decodeIfPresent(Bool.self, forKey: .priorityProcessing) ?? false
        }
    }

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
    let featureFlags: FeatureFlags

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
        case featureFlags = "feature_flags"
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
        featureFlags = try container.decodeIfPresent(FeatureFlags.self, forKey: .featureFlags) ?? FeatureFlags(
            clipLimit: 3,
            altHooks: false,
            campaignMode: false,
            packagingProfiles: false,
            historyLimit: 10,
            premiumExports: false,
            priorityProcessing: false
        )
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
    let previewImageURL: String?
    let transcriptExcerpt: String?
    let editProfile: String?
    let aspectRatio: String?
    let whyThisMatters: String?
    let confidenceScore: Int?
    let thumbnailText: String?
    let ctaSuggestion: String?
    let postRank: Int?
    let hookVariants: [String]
    let captionStyle: String?

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
        case previewImageURL = "preview_image_url"
        case transcriptExcerpt = "transcript_excerpt"
        case editProfile = "edit_profile"
        case aspectRatio = "aspect_ratio"
        case whyThisMatters = "why_this_matters"
        case confidenceScore = "confidence_score"
        case thumbnailText = "thumbnail_text"
        case ctaSuggestion = "cta_suggestion"
        case postRank = "post_rank"
        case hookVariants = "hook_variants"
        case captionStyle = "caption_style"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        hook = try container.decode(String.self, forKey: .hook)
        caption = try container.decode(String.self, forKey: .caption)
        startTime = try container.decode(String.self, forKey: .startTime)
        endTime = try container.decode(String.self, forKey: .endTime)
        score = try container.decode(Int.self, forKey: .score)
        format = try container.decode(String.self, forKey: .format)
        clipURL = try container.decodeIfPresent(String.self, forKey: .clipURL)
        rawClipURL = try container.decodeIfPresent(String.self, forKey: .rawClipURL)
        editedClipURL = try container.decodeIfPresent(String.self, forKey: .editedClipURL)
        previewImageURL = try container.decodeIfPresent(String.self, forKey: .previewImageURL)
        transcriptExcerpt = try container.decodeIfPresent(String.self, forKey: .transcriptExcerpt)
        editProfile = try container.decodeIfPresent(String.self, forKey: .editProfile)
        aspectRatio = try container.decodeIfPresent(String.self, forKey: .aspectRatio)
        whyThisMatters = try container.decodeIfPresent(String.self, forKey: .whyThisMatters)
        confidenceScore = try container.decodeIfPresent(Int.self, forKey: .confidenceScore)
        thumbnailText = try container.decodeIfPresent(String.self, forKey: .thumbnailText)
        ctaSuggestion = try container.decodeIfPresent(String.self, forKey: .ctaSuggestion)
        postRank = try container.decodeIfPresent(Int.self, forKey: .postRank)
        hookVariants = try container.decodeIfPresent([String].self, forKey: .hookVariants) ?? []
        captionStyle = try container.decodeIfPresent(String.self, forKey: .captionStyle)
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

private extension ProcessingSummary.FeatureFlags {
    init(
        clipLimit: Int,
        altHooks: Bool,
        campaignMode: Bool,
        packagingProfiles: Bool,
        historyLimit: Int,
        premiumExports: Bool,
        priorityProcessing: Bool
    ) {
        self.clipLimit = clipLimit
        self.altHooks = altHooks
        self.campaignMode = campaignMode
        self.packagingProfiles = packagingProfiles
        self.historyLimit = historyLimit
        self.premiumExports = premiumExports
        self.priorityProcessing = priorityProcessing
    }
}
