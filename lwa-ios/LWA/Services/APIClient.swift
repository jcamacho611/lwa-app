import Foundation

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
        return URL(string: "http://127.0.0.1:8000")!
        #else
        return URL(string: "https://your-render-service.onrender.com")!
        #endif
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

    static var defaultAPIBaseURL: String {
        APIConfig.defaultBaseURL.absoluteString
    }

    static var defaultCheckoutURL: String {
        (Bundle.main.object(forInfoDictionaryKey: "LWACheckoutURL") as? String) ?? "https://example.com/lwa-checkout"
    }

    static var apiBaseURL: String {
        APIConfig.baseURL.absoluteString
    }

    static var checkoutURL: String {
        let override = UserDefaults.standard.string(forKey: checkoutURLKey)?.trimmingCharacters(in: .whitespacesAndNewlines)
        return override?.isEmpty == false ? override! : defaultCheckoutURL
    }

    static func save(apiBaseURL: String, checkoutURL: String) {
        UserDefaults.standard.set(apiBaseURL.trimmingCharacters(in: .whitespacesAndNewlines), forKey: apiBaseURLKey)
        UserDefaults.standard.set(checkoutURL.trimmingCharacters(in: .whitespacesAndNewlines), forKey: checkoutURLKey)
    }
}

struct APIClient {
    private var processEndpoint: URL? {
        APIConfig.baseURL.appendingPathComponent("process")
    }

    private var trendsEndpoint: URL {
        APIConfig.baseURL.appendingPathComponent("v1/trends")
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

    func fetchTrends() async throws -> [TrendItem] {
        var request = URLRequest(url: trendsEndpoint)
        request.httpMethod = "GET"
        request.timeoutInterval = 20

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
