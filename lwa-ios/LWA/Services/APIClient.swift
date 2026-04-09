import Foundation

private enum BundleConfiguration {
    static func string(for key: String, fallback: String) -> String {
        (Bundle.main.object(forInfoDictionaryKey: key) as? String) ?? fallback
    }

    static func bool(for key: String, fallback: Bool = false) -> Bool {
        (Bundle.main.object(forInfoDictionaryKey: key) as? Bool) ?? fallback
    }
}

enum APIError: LocalizedError {
    case invalidVideoURL
    case invalidBaseURL
    case invalidResponse
    case server(String)

    var errorDescription: String? {
        switch self {
        case .invalidVideoURL:
            return "Enter a valid http or https video URL."
        case .invalidBaseURL:
            return "Set a valid backend base URL in Settings."
        case .invalidResponse:
            return "The backend returned an invalid response."
        case .server(let message):
            return message
        }
    }
}

enum APIConfig {
    static var defaultBaseURL: URL {
        #if DEBUG
        let configured = BundleConfiguration.string(for: "LWADebugAPIBaseURL", fallback: "http://localhost:8000")
        #else
        let configured = BundleConfiguration.string(
            for: "LWAProductionAPIBaseURL",
            fallback: "https://lwa-backend-production-c9cc.up.railway.app"
        )
        #endif

        return URL(string: configured) ?? URL(string: "https://lwa-backend-production-c9cc.up.railway.app")!
    }

    static var baseURL: URL {
        let override = UserDefaults.standard.string(forKey: AppConfiguration.apiBaseURLKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines)

        if let override, !override.isEmpty, let url = URL(string: override) {
            return url
        }

        return defaultBaseURL
    }
}

enum AppConfiguration {
    static let apiBaseURLKey = "lwa.api_base_url"
    static let checkoutURLKey = "lwa.checkout_url"
    static let apiKeyKey = "lwa.api_key"
    static let appStoreModeKey = "LWAAppStoreMode"

    static var defaultAPIBaseURL: String {
        APIConfig.defaultBaseURL.absoluteString
    }

    static var defaultCheckoutURL: String {
        BundleConfiguration.string(
            for: "LWACheckoutURL",
            fallback: "https://whop.com/lwa-app/lwa-ai-content-repurposer/"
        )
    }

    static var defaultAPIKey: String {
        BundleConfiguration.string(for: "LWAAPIKey", fallback: "")
    }

    static var privacyPolicyURL: String {
        BundleConfiguration.string(
            for: "LWAPrivacyPolicyURL",
            fallback: "https://github.com/jcamacho611/lwa-app/blob/main/docs/privacy-policy.md"
        )
    }

    static var supportURL: String {
        BundleConfiguration.string(
            for: "LWASupportURL",
            fallback: "https://github.com/jcamacho611/lwa-app/blob/main/docs/support.md"
        )
    }

    static var apiKeyHeaderName: String {
        BundleConfiguration.string(for: "LWAAPIKeyHeaderName", fallback: "x-api-key")
    }

    static var isAppStoreMode: Bool {
        BundleConfiguration.bool(for: appStoreModeKey, fallback: true)
    }

    static var apiBaseURL: String {
        APIConfig.baseURL.absoluteString
    }

    static var checkoutURL: String {
        let override = UserDefaults.standard.string(forKey: checkoutURLKey)?.trimmingCharacters(in: .whitespacesAndNewlines)
        return override?.isEmpty == false ? override! : defaultCheckoutURL
    }

    static var apiKey: String {
        let override = UserDefaults.standard.string(forKey: apiKeyKey)?.trimmingCharacters(in: .whitespacesAndNewlines)
        return override?.isEmpty == false ? override! : defaultAPIKey
    }

    static func save(apiBaseURL: String, checkoutURL: String, apiKey: String) {
        UserDefaults.standard.set(apiBaseURL.trimmingCharacters(in: .whitespacesAndNewlines), forKey: apiBaseURLKey)
        UserDefaults.standard.set(checkoutURL.trimmingCharacters(in: .whitespacesAndNewlines), forKey: checkoutURLKey)
        UserDefaults.standard.set(apiKey.trimmingCharacters(in: .whitespacesAndNewlines), forKey: apiKeyKey)
    }
}

struct APIClient {
    private var jobsEndpoint: URL {
        APIConfig.baseURL.appendingPathComponent("v1/jobs")
    }

    private var processEndpoint: URL? {
        APIConfig.baseURL.appendingPathComponent("process")
    }

    private var trendsEndpoint: URL {
        APIConfig.baseURL.appendingPathComponent("v1/trends")
    }

    private func applySharedHeaders(to request: inout URLRequest) {
        let apiKey = AppConfiguration.apiKey.trimmingCharacters(in: .whitespacesAndNewlines)
        if !apiKey.isEmpty {
            request.setValue(apiKey, forHTTPHeaderField: AppConfiguration.apiKeyHeaderName)
        }
    }

    func process(
        videoURL: String,
        selectedTrend: TrendItem?,
        targetPlatform: String
    ) async throws -> ClipResponse {
        guard let candidateURL = URL(string: videoURL),
              let scheme = candidateURL.scheme?.lowercased(),
              scheme == "http" || scheme == "https" else {
            throw APIError.invalidVideoURL
        }

        guard let endpoint = processEndpoint else {
            throw APIError.invalidBaseURL
        }

        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 30
        applySharedHeaders(to: &request)
        request.httpBody = try JSONEncoder().encode(
            ProcessRequest(
                videoURL: videoURL,
                selectedTrend: selectedTrend?.title,
                trendSource: selectedTrend?.source,
                targetPlatform: targetPlatform,
                contentAngle: nil
            )
        )

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200 ... 299).contains(httpResponse.statusCode) else {
            let fallback = "Backend error \(httpResponse.statusCode)"
            let message = String(data: data, encoding: .utf8) ?? fallback
            throw APIError.server(message)
        }

        return try JSONDecoder().decode(ClipResponse.self, from: data)
    }

    func createJob(
        videoURL: String,
        selectedTrend: TrendItem?,
        targetPlatform: String
    ) async throws -> JobCreatedResponse {
        guard let candidateURL = URL(string: videoURL),
              let scheme = candidateURL.scheme?.lowercased(),
              scheme == "http" || scheme == "https" else {
            throw APIError.invalidVideoURL
        }

        var request = URLRequest(url: jobsEndpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 30
        applySharedHeaders(to: &request)
        request.httpBody = try JSONEncoder().encode(
            ProcessRequest(
                videoURL: videoURL,
                selectedTrend: selectedTrend?.title,
                trendSource: selectedTrend?.source,
                targetPlatform: targetPlatform,
                contentAngle: nil
            )
        )

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200 ... 299).contains(httpResponse.statusCode) else {
            let fallback = "Backend error \(httpResponse.statusCode)"
            let message = String(data: data, encoding: .utf8) ?? fallback
            throw APIError.server(message)
        }

        return try JSONDecoder().decode(JobCreatedResponse.self, from: data)
    }

    func fetchJob(jobID: String) async throws -> JobStatusResponse {
        let endpoint = jobsEndpoint.appendingPathComponent(jobID)
        var request = URLRequest(url: endpoint)
        request.httpMethod = "GET"
        request.timeoutInterval = 20
        applySharedHeaders(to: &request)

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200 ... 299).contains(httpResponse.statusCode) else {
            let fallback = "Backend error \(httpResponse.statusCode)"
            let message = String(data: data, encoding: .utf8) ?? fallback
            throw APIError.server(message)
        }

        return try JSONDecoder().decode(JobStatusResponse.self, from: data)
    }

    func fetchTrends() async throws -> [TrendItem] {
        var request = URLRequest(url: trendsEndpoint)
        request.httpMethod = "GET"
        request.timeoutInterval = 20
        applySharedHeaders(to: &request)

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              (200 ... 299).contains(httpResponse.statusCode) else {
            throw APIError.invalidResponse
        }

        return try JSONDecoder().decode(TrendsResponse.self, from: data).trends
    }
}

private struct ProcessRequest: Encodable {
    let videoURL: String
    let selectedTrend: String?
    let trendSource: String?
    let targetPlatform: String
    let contentAngle: String?

    enum CodingKeys: String, CodingKey {
        case videoURL = "video_url"
        case selectedTrend = "selected_trend"
        case trendSource = "trend_source"
        case targetPlatform = "target_platform"
        case contentAngle = "content_angle"
    }
}
