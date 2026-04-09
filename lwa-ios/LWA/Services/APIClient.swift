import Foundation

enum APIError: LocalizedError {
    case invalidVideoURL
    case invalidResponse
    case server(String)

    var errorDescription: String? {
        switch self {
        case .invalidVideoURL:
            return "Enter a valid http or https video URL."
        case .invalidResponse:
            return "The backend returned an invalid response."
        case .server(let message):
            return message
        }
    }
}

struct APIClient {
    private let endpoint = URL(string: "http://127.0.0.1:8000/process")!

    func process(videoURL: String) async throws -> ClipResponse {
        guard let candidateURL = URL(string: videoURL),
              let scheme = candidateURL.scheme?.lowercased(),
              scheme == "http" || scheme == "https" else {
            throw APIError.invalidVideoURL
        }

        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(ProcessRequest(videoURL: videoURL))

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
}

private struct ProcessRequest: Encodable {
    let videoURL: String

    enum CodingKeys: String, CodingKey {
        case videoURL = "video_url"
    }
}

