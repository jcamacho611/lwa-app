import Foundation

@MainActor
final class ContentViewModel: ObservableObject {
    @Published var videoURL = ""
    @Published private(set) var clips: [ClipResult] = []
    @Published private(set) var isLoading = false
    @Published var errorMessage: String?
    @Published private(set) var lastSubmittedURL = ""

    private let apiClient: APIClient

    init(apiClient: APIClient = APIClient()) {
        self.apiClient = apiClient
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

        do {
            let response = try await apiClient.process(videoURL: trimmedURL)
            clips = response.clips
            lastSubmittedURL = response.videoURL
        } catch {
            clips = []
            lastSubmittedURL = ""
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }
}

