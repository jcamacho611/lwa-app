import Foundation

struct GenerationTrackItem: Identifiable {
    enum Status {
        case pending
        case active
        case complete
    }

    let id: String
    let title: String
    let status: Status
}

@MainActor
final class ContentViewModel: ObservableObject {
    private let historyKey = "lwa.saved_runs"
    private let generationStages = [
        "Analyzing source",
        "Finding moments",
        "Ranking clips",
        "Packaging copy",
        "Delivering assets",
    ]

    let supportedPlatforms = ["TikTok", "Instagram", "YouTube", "Facebook"]

    @Published var videoURL = ""
    @Published private(set) var selectedUpload: UploadedSource?
    @Published private(set) var clips: [ClipResult] = []
    @Published private(set) var isLoading = false
    @Published private(set) var isUploading = false
    @Published var errorMessage: String?
    @Published private(set) var lastSubmittedURL = ""
    @Published private(set) var latestResponse: ClipResponse?
    @Published private(set) var history: [SavedRun] = []
    @Published var showPaywall = false
    @Published private(set) var trends: [TrendItem] = []
    @Published var selectedTrend: TrendItem?
    @Published var selectedPlatform = "TikTok"
    @Published private(set) var jobStatusMessage = "Preparing request."

    private let apiClient: APIClient

    init(apiClient: APIClient = APIClient()) {
        self.apiClient = apiClient
        history = loadHistory()

        Task {
            await refreshTrends()
        }

        if let mostRecentRun = history.first {
            latestResponse = mostRecentRun.response
            clips = mostRecentRun.response.clips
            lastSubmittedURL = mostRecentRun.response.videoURL
            videoURL = mostRecentRun.response.videoURL
            selectedTrend = mostRecentRun.response.trendContext.first
            selectedPlatform = mostRecentRun.response.processingSummary.targetPlatform
        }
    }

    func generateClips() async {
        let trimmedURL = videoURL.trimmingCharacters(in: .whitespacesAndNewlines)

        guard !trimmedURL.isEmpty || selectedUpload != nil else {
            clips = []
            errorMessage = "Paste a source URL or upload a source first."
            lastSubmittedURL = ""
            return
        }

        isLoading = true
        errorMessage = nil
        jobStatusMessage = "Queueing processing job."

        do {
            let job = try await apiClient.createJob(
                videoURL: trimmedURL,
                uploadFileID: selectedUpload?.id,
                selectedTrend: selectedTrend,
                targetPlatform: selectedPlatform
            )
            jobStatusMessage = job.message
            let response = try await waitForJob(jobID: job.jobID)
            clips = response.clips
            lastSubmittedURL = response.videoURL
            latestResponse = response
            saveRun(response)
            showPaywall = !AppConfiguration.isAppStoreMode && response.processingSummary.creditsRemaining <= 1
        } catch {
            clips = []
            lastSubmittedURL = ""
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func uploadVideo(fileURL: URL) async {
        guard !AppConfiguration.authToken.isEmpty else {
            errorMessage = "Uploads require an authenticated account on the current backend."
            return
        }

        isUploading = true
        errorMessage = nil
        defer { isUploading = false }

        do {
            let upload = try await apiClient.uploadVideo(fileURL: fileURL)
            selectedUpload = upload
            if videoURL.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                videoURL = upload.publicURL ?? ""
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func clearSelectedUpload() {
        selectedUpload = nil
    }

    func refreshTrends() async {
        do {
            trends = try await apiClient.fetchTrends()
            if selectedTrend == nil {
                selectedTrend = trends.first
            }
        } catch {
            if trends.isEmpty {
                errorMessage = "Could not load live trends. You can still generate clip ideas from the video URL."
            }
        }
    }

    func toggleTrend(_ trend: TrendItem) {
        if selectedTrend == trend {
            selectedTrend = nil
        } else {
            selectedTrend = trend
        }
    }

    func restore(run: SavedRun) {
        latestResponse = run.response
        clips = run.response.clips
        lastSubmittedURL = run.response.videoURL
        videoURL = run.response.videoURL
        selectedUpload = nil
        selectedTrend = run.response.trendContext.first
        selectedPlatform = run.response.processingSummary.targetPlatform
        errorMessage = nil
    }

    func deleteHistory(at offsets: IndexSet) {
        history.remove(atOffsets: offsets)
        persistHistory()
    }

    func clearHistory() {
        history = []
        persistHistory()
    }

    var planName: String {
        latestResponse?.processingSummary.planName ?? "Starter Trial"
    }

    var creditsRemainingLabel: String {
        guard let credits = latestResponse?.processingSummary.creditsRemaining else {
            return "3 free generations"
        }

        return "\(credits) credits remaining"
    }

    var premiumStatusLabel: String {
        guard let response = latestResponse else {
            return "Free preview"
        }
        return response.processingSummary.featureFlags.premiumExports ? "Premium exports live" : "Free exports locked"
    }

    var bestClip: ClipResult? {
        clips.sorted { lhs, rhs in
            let lhsRank = lhs.rank ?? lhs.postRank ?? Int.max
            let rhsRank = rhs.rank ?? rhs.postRank ?? Int.max
            if lhsRank != rhsRank {
                return lhsRank < rhsRank
            }
            return lhs.score > rhs.score
        }.first
    }

    var recentRuns: [SavedRun] {
        Array(history.prefix(8))
    }

    var processingStatusLabel: String {
        if isUploading {
            return "Uploading source"
        }
        if isLoading {
            return "\(max(clips.count, 1)) clips processing"
        }
        return "\(clips.count) clips ready"
    }

    var generatedTodayCount: Int {
        let calendar = Calendar.current
        return history
            .filter { calendar.isDateInToday($0.createdAt) }
            .reduce(0) { partial, run in
                partial + run.response.clips.count
            }
    }

    var sourceSummaryLabel: String {
        if let selectedUpload {
            return selectedUpload.filename
        }
        let trimmedURL = videoURL.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmedURL.isEmpty ? "No source selected" : trimmedURL
    }

    var generationStageTitle: String {
        if let errorMessage, !errorMessage.isEmpty, latestResponse == nil {
            return "Run blocked"
        }

        if isUploading {
            return "Uploading source"
        }

        if isLoading {
            switch activeGenerationStage {
            case 0:
                return "Analyzing source"
            case 1:
                return "Finding viral moments"
            case 2:
                return "Ranking the stack"
            case 3:
                return "Packaging copy"
            default:
                return "Generating clips"
            }
        }

        if latestResponse != nil {
            return "Clip pack ready"
        }

        return "Awaiting source"
    }

    var generationStageDetail: String {
        if let errorMessage, !errorMessage.isEmpty, latestResponse == nil {
            return errorMessage
        }

        if isUploading {
            return "Your source video is being validated and staged for processing."
        }

        if isLoading {
            return jobStatusMessage
        }

        if let response = latestResponse {
            return "\(response.clips.count) clips ready for \(response.processingSummary.targetPlatform). Edited exports: \(response.processingSummary.editedAssetsCreated)."
        }

        return "Paste a long-form source, choose the target platform, and launch the run."
    }

    var generationTrack: [GenerationTrackItem] {
        let activeStage = activeGenerationStage

        return generationStages.enumerated().map { index, title in
            let status: GenerationTrackItem.Status

            if latestResponse != nil && !isLoading {
                status = .complete
            } else if isLoading {
                if index < activeStage {
                    status = .complete
                } else if index == activeStage {
                    status = .active
                } else {
                    status = .pending
                }
            } else {
                status = .pending
            }

            return GenerationTrackItem(id: title, title: title, status: status)
        }
    }

    var generationProgress: Double {
        if latestResponse != nil && !isLoading {
            return 1.0
        }

        if isUploading {
            return 0.12
        }

        guard isLoading else { return 0.0 }
        return min(max(Double(activeGenerationStage + 1) / Double(generationStages.count), 0.08), 0.94)
    }

    var shareText: String {
        guard let response = latestResponse else { return "" }

        let clipLines = response.clips.enumerated().map { index, clip in
            """
            \(clip.postRank ?? (index + 1)). \(clip.title) [\(clip.startTime)-\(clip.endTime)] score \(clip.score)
            Hook: \(clip.hook)
            Caption: \(clip.caption)
            Why it matters: \(clip.whyThisMatters ?? "not available")
            Thumbnail text: \(clip.thumbnailText ?? "not available")
            CTA: \(clip.ctaSuggestion ?? "not available")
            Alternate hooks: \(clip.hookVariants.isEmpty ? "not available" : clip.hookVariants.joined(separator: " | "))
            Edited asset: \(clip.editedClipURL ?? clip.clipURL ?? "not available")
            Raw cut: \(clip.rawClipURL ?? "not available")
            """
        }

        return """
        LWA clip pack
        Source: \(response.videoURL)
        Platform: \(response.sourcePlatform ?? "not available")
        Target: \(response.processingSummary.targetPlatform)
        AI: \(response.processingSummary.aiProvider)
        Mode: \(response.processingSummary.processingMode)
        Selection: \(response.processingSummary.selectionStrategy)
        Plan: \(response.processingSummary.planName)
        Edited exports: \(response.processingSummary.editedAssetsCreated)

        \(clipLines.joined(separator: "\n\n"))
        """
    }

    private func waitForJob(jobID: String) async throws -> ClipResponse {
        let deadline = Date().addingTimeInterval(180)

        while Date() < deadline {
            let status = try await apiClient.fetchJob(jobID: jobID)
            jobStatusMessage = status.message

            switch status.status {
            case "completed":
                if let result = status.result {
                    return result
                }
                throw APIError.server("The backend marked the job complete without returning a result.")
            case "failed":
                throw APIError.server(status.error ?? "Processing failed.")
            default:
                try await Task.sleep(nanoseconds: 1_500_000_000)
            }
        }

        throw APIError.server("Processing timed out. Try a shorter video or a different source.")
    }

    private func saveRun(_ response: ClipResponse) {
        history.removeAll { $0.id == response.requestID }
        history.insert(SavedRun(response: response), at: 0)
        history = Array(history.prefix(response.processingSummary.featureFlags.historyLimit))
        persistHistory()
    }

    private func loadHistory() -> [SavedRun] {
        guard let data = UserDefaults.standard.data(forKey: historyKey) else {
            return []
        }

        do {
            return try JSONDecoder().decode([SavedRun].self, from: data)
        } catch {
            return []
        }
    }

    private func persistHistory() {
        guard let data = try? JSONEncoder().encode(history) else {
            return
        }

        UserDefaults.standard.set(data, forKey: historyKey)
    }

    private var activeGenerationStage: Int {
        if latestResponse != nil && !isLoading {
            return generationStages.count - 1
        }

        let message = jobStatusMessage.lowercased()

        if message.contains("queue") || message.contains("pending") {
            return 0
        }

        if message.contains("source")
            || message.contains("download")
            || message.contains("ingest")
            || message.contains("probe") {
            return 1
        }

        if message.contains("segment")
            || message.contains("select")
            || message.contains("score")
            || message.contains("seed")
            || message.contains("detect") {
            return 2
        }

        if message.contains("render")
            || message.contains("export")
            || message.contains("encode")
            || message.contains("ffmpeg")
            || message.contains("package") {
            return 3
        }

        if message.contains("final")
            || message.contains("deliver")
            || message.contains("ready") {
            return 4
        }

        return isLoading ? 1 : 0
    }
}
