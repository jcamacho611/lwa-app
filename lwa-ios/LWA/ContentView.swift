import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = ContentViewModel()

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.05, green: 0.07, blue: 0.11),
                    Color(red: 0.02, green: 0.02, blue: 0.04),
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    headerSection
                    inputCard
                    resultsSection
                }
                .padding(20)
            }
        }
        .preferredColorScheme(.dark)
    }

    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("LWA")
                .font(.system(size: 34, weight: .bold, design: .rounded))
                .foregroundStyle(.white)

            Text("Paste a video URL, send it to the backend, and preview generated hook and caption ideas.")
                .font(.subheadline)
                .foregroundStyle(Color.white.opacity(0.72))
        }
    }

    private var inputCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Source Video")
                .font(.headline)
                .foregroundStyle(.white)

            TextField("https://www.youtube.com/watch?v=example", text: $viewModel.videoURL, axis: .vertical)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .padding(14)
                .background(Color.white.opacity(0.08))
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                .foregroundStyle(.white)

            Button {
                Task {
                    await viewModel.generateClips()
                }
            } label: {
                HStack {
                    if viewModel.isLoading {
                        ProgressView()
                            .tint(.black)
                    }

                    Text(viewModel.isLoading ? "Generating..." : "Generate Clips")
                        .fontWeight(.semibold)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .background(
                    LinearGradient(
                        colors: [
                            Color(red: 0.34, green: 0.89, blue: 0.82),
                            Color(red: 0.18, green: 0.68, blue: 0.91),
                        ],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .foregroundStyle(.black)
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            }
            .disabled(viewModel.isLoading)
            .opacity(viewModel.isLoading ? 0.8 : 1.0)
        }
        .padding(18)
        .background(Color.white.opacity(0.06))
        .overlay(
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(Color.white.opacity(0.08), lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    @ViewBuilder
    private var resultsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("Results")
                    .font(.headline)
                    .foregroundStyle(.white)

                Spacer()

                if !viewModel.lastSubmittedURL.isEmpty {
                    Text("Mock clips")
                        .font(.caption.weight(.medium))
                        .foregroundStyle(Color.white.opacity(0.56))
                }
            }

            if let errorMessage = viewModel.errorMessage {
                statusCard(
                    title: "Request failed",
                    body: errorMessage,
                    tint: Color(red: 1.0, green: 0.39, blue: 0.39)
                )
            } else if viewModel.isLoading {
                statusCard(
                    title: "Talking to backend",
                    body: "The app is waiting for http://127.0.0.1:8000/process to return clip suggestions.",
                    tint: Color(red: 0.34, green: 0.89, blue: 0.82)
                )
            } else if viewModel.clips.isEmpty {
                statusCard(
                    title: "No clips yet",
                    body: "Start the FastAPI backend, paste a video URL, and tap Generate Clips.",
                    tint: Color.white.opacity(0.8)
                )
            } else {
                ForEach(viewModel.clips) { clip in
                    clipCard(for: clip)
                }
            }
        }
    }

    private func statusCard(title: String, body: String, tint: Color) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(tint)

            Text(body)
                .font(.subheadline)
                .foregroundStyle(Color.white.opacity(0.72))
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.06))
        .overlay(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .stroke(Color.white.opacity(0.08), lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    private func clipCard(for clip: ClipResult) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 6) {
                    Text(clip.title)
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(.white)

                    Text("\(clip.startTime) - \(clip.endTime)")
                        .font(.caption.weight(.medium))
                        .foregroundStyle(Color.white.opacity(0.54))
                }

                Spacer()
            }

            VStack(alignment: .leading, spacing: 6) {
                Text("Hook")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(Color(red: 0.34, green: 0.89, blue: 0.82))

                Text(clip.hook)
                    .font(.body)
                    .foregroundStyle(Color.white.opacity(0.9))
            }

            VStack(alignment: .leading, spacing: 6) {
                Text("Caption")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(Color(red: 0.96, green: 0.78, blue: 0.35))

                Text(clip.caption)
                    .font(.body)
                    .foregroundStyle(Color.white.opacity(0.78))
            }
        }
        .padding(18)
        .background(Color.white.opacity(0.06))
        .overlay(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(Color.white.opacity(0.08), lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
    }
}

#Preview {
    ContentView()
}

