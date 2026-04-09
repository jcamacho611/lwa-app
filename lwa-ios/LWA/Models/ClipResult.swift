import Foundation

struct ClipResponse: Decodable {
    let videoURL: String
    let status: String
    let clips: [ClipResult]

    enum CodingKeys: String, CodingKey {
        case videoURL = "video_url"
        case status
        case clips
    }
}

struct ClipResult: Decodable, Identifiable {
    let id: String
    let title: String
    let hook: String
    let caption: String
    let startTime: String
    let endTime: String

    enum CodingKeys: String, CodingKey {
        case id
        case title
        case hook
        case caption
        case startTime = "start_time"
        case endTime = "end_time"
    }
}

