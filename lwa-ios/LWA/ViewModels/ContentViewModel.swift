import Foundation

@MainActor
final class ContentViewModel: ObservableObject {
    private let historyKey = "lwa.saved_runs"
    let supportedPlatforms = ["TikTok", "Instagram", "YouTube", "Facebook"]

    @Published var videoURL = ""
    @Published private(set) var clips: [ClipResult] = []
    @Published private(set) var isLoading = false
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
        self.history = loadHistory()
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

        guard !trimmedURL.isEmpty else {
            clips = []
            errorMessage = "Enter a video URL first."
            lastSubmittedURL = ""
            return
        }

        isLoading = true
        errorMessage = nil
        jobStatusMessage = "Queueing processing job."

        do {
            let job = try await apiClient.createJob(
                videoURL: trimmedURL,
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

    var shareText: String {
        guard let response = latestResponse else { return "" }

        let clipLines = response.clips.enumerated().map { index, clip in
            """
            \(index + 1). \(clip.title) [\(clip.startTime)-\(clip.endTime)] score \(clip.score)
            Hook: \(clip.hook)
            Caption: \(clip.caption)
            Edited asset: \(clip.editedClipURL ?? clip.clipURL ?? "not available")
            Raw cut: \(clip.rawClipURL ?? "not available")
            """
        }

        return """
        IWA clip pack
        Source: \(response.videoURL)
        Platform: \(response.sourcePlatform)
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
        history = Array(history.prefix(10))
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
}
