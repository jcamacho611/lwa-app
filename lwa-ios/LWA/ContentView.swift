import SwiftUI
import UIKit

struct ContentView: View {
    @StateObject private var viewModel = ContentViewModel()
    @State private var showSettings = false
    @State private var showCopiedAlert = false

    var body: some View {
        NavigationStack {
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
                        if AppConfiguration.isAppStoreMode {
                            launchReadinessCard
                        } else {
                            monetizationCard
                        }
                        trendsSection
                        inputCard
                        resultsSection
                        historySection
                    }
                    .padding(20)
                }
            }
            .navigationBarHidden(true)
        }
        .preferredColorScheme(.dark)
        .sheet(isPresented: $showSettings) {
            SettingsSheet()
        }
        .sheet(isPresented: $viewModel.showPaywall) {
            PaywallSheet()
        }
        .alert("Results copied", isPresented: $showCopiedAlert) {
            Button("OK", role: .cancel) { }
        } message: {
            Text("The latest clip pack is now on your clipboard.")
        }
    }

    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 10) {
                    Text("LWA")
                        .font(.system(size: 34, weight: .bold, design: .rounded))
                        .foregroundStyle(.white)

                    Text("Turn long videos into clips, hooks, and captions you can hand to clients or publish fast.")
                        .font(.subheadline)
                        .foregroundStyle(Color.white.opacity(0.72))
                }

                Spacer()

                HStack(spacing: 10) {
                    if !AppConfiguration.isAppStoreMode {
                        smallActionButton(title: "Pricing") {
                            viewModel.showPaywall = true
                        }
                    }

                    smallActionButton(title: "Settings") {
                        showSettings = true
                    }
                }
            }

            HStack(spacing: 10) {
                metricPill("Fast turnaround")
                metricPill(viewModel.selectedPlatform)
                metricPill(viewModel.creditsRemainingLabel)
            }
        }
    }

    private var launchReadinessCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Production Build")
                .font(.headline)
                .foregroundStyle(.white)

            Text("This App Store build points at the live LWA backend over HTTPS. You can still override the API base URL in Settings for local testing.")
                .font(.subheadline)
                .foregroundStyle(Color.white.opacity(0.72))

            HStack(spacing: 12) {
                badge(title: "Backend", detail: "Railway", tint: Color(red: 0.34, green: 0.89, blue: 0.82))
                badge(title: "Mode", detail: "App Store", tint: Color(red: 0.96, green: 0.78, blue: 0.35))
            }
        }
        .padding(18)
        .background(Color.white.opacity(0.06))
        .overlay(
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(Color.white.opacity(0.08), lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var monetizationCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Sell the output, not just the idea")
                        .font(.headline)
                        .foregroundStyle(.white)

                    Text("This MVP now keeps clip history, supports a configurable checkout link, and makes each result easy to copy or share.")
                        .font(.subheadline)
                        .foregroundStyle(Color.white.opacity(0.72))
                }

                Spacer()
            }

            HStack(spacing: 12) {
                badge(title: "Trial", detail: viewModel.planName, tint: Color(red: 0.34, green: 0.89, blue: 0.82))
                badge(title: "Credits", detail: viewModel.creditsRemainingLabel, tint: Color(red: 0.96, green: 0.78, blue: 0.35))
            }

            Button {
                viewModel.showPaywall = true
            } label: {
                Text("Open Revenue Setup")
                    .font(.subheadline.weight(.semibold))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .background(Color.white.opacity(0.08))
                    .foregroundStyle(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
            }
        }
        .padding(18)
        .background(Color.white.opacity(0.06))
        .overlay(
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(Color.white.opacity(0.08), lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
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

            VStack(alignment: .leading, spacing: 10) {
                Text("Target Platform")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(Color.white.opacity(0.68))

                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 10) {
                        ForEach(viewModel.supportedPlatforms, id: \.self) { platform in
                            Button {
                                viewModel.selectedPlatform = platform
                            } label: {
                                Text(platform)
                                    .font(.caption.weight(.semibold))
                                    .foregroundStyle(viewModel.selectedPlatform == platform ? .black : .white)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 10)
                                    .background(
                                        viewModel.selectedPlatform == platform
                                            ? Color(red: 0.34, green: 0.89, blue: 0.82)
                                            : Color.white.opacity(0.08)
                                    )
                                    .clipShape(Capsule())
                            }
                        }
                    }
                }
            }

            if let selectedTrend = viewModel.selectedTrend {
                statusCard(
                    title: "Trend angle selected",
                    body: "\(selectedTrend.title) • \(selectedTrend.source)",
                    tint: Color(red: 0.96, green: 0.78, blue: 0.35)
                )
            }

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
    private var trendsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("Trend Radar")
                    .font(.headline)
                    .foregroundStyle(.white)

                Spacer()

                Button("Refresh") {
                    Task {
                        await viewModel.refreshTrends()
                    }
                }
                .font(.caption.weight(.medium))
                .foregroundStyle(Color.white.opacity(0.68))
            }

            Text("Public signals from Google Trends, Reddit, and Hacker News feed the angle selection.")
                .font(.subheadline)
                .foregroundStyle(Color.white.opacity(0.68))

            if viewModel.trends.isEmpty {
                statusCard(
                    title: "Loading trends",
                    body: "Fetching public signals you can use for hooks, angles, and caption framing.",
                    tint: Color(red: 0.34, green: 0.89, blue: 0.82)
                )
            } else {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(alignment: .top, spacing: 12) {
                        ForEach(viewModel.trends) { trend in
                            Button {
                                viewModel.toggleTrend(trend)
                            } label: {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text(trend.source)
                                        .font(.caption2.weight(.bold))
                                        .foregroundStyle(
                                            viewModel.selectedTrend == trend
                                                ? Color.black.opacity(0.72)
                                                : Color(red: 0.34, green: 0.89, blue: 0.82)
                                        )

                                    Text(trend.title)
                                        .font(.subheadline.weight(.semibold))
                                        .foregroundStyle(viewModel.selectedTrend == trend ? .black : .white)
                                        .multilineTextAlignment(.leading)

                                    Text(trend.detail)
                                        .font(.caption)
                                        .foregroundStyle(
                                            viewModel.selectedTrend == trend
                                                ? Color.black.opacity(0.62)
                                                : Color.white.opacity(0.58)
                                        )
                                        .multilineTextAlignment(.leading)
                                }
                                .frame(width: 220, alignment: .leading)
                                .padding(16)
                                .background(
                                    viewModel.selectedTrend == trend
                                        ? Color(red: 0.34, green: 0.89, blue: 0.82)
                                        : Color.white.opacity(0.06)
                                )
                                .overlay(
                                    RoundedRectangle(cornerRadius: 20, style: .continuous)
                                        .stroke(Color.white.opacity(0.08), lineWidth: 1)
                                )
                                .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
            }
        }
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
                    Text(viewModel.latestResponse?.sourcePlatform ?? "Mock clips")
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
                    body: viewModel.jobStatusMessage,
                    tint: Color(red: 0.34, green: 0.89, blue: 0.82)
                )
            } else if viewModel.clips.isEmpty {
                statusCard(
                    title: "No clips yet",
                    body: "Start the FastAPI backend, paste a video URL, and tap Generate Clips. Saved runs will appear below.",
                    tint: Color.white.opacity(0.8)
                )
            } else {
                if let summary = viewModel.latestResponse?.processingSummary {
                    summaryCard(summary)
                }

                HStack(spacing: 12) {
                    Button {
                        UIPasteboard.general.string = viewModel.shareText
                        showCopiedAlert = true
                    } label: {
                        secondaryAction(title: "Copy Bundle")
                    }

                    ShareLink(item: viewModel.shareText) {
                        secondaryAction(title: "Share")
                    }
                }

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

    private func summaryCard(_ summary: ProcessingSummary) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Processing Summary")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.white)

            Text("Plan: \(summary.planName)")
                .foregroundStyle(Color.white.opacity(0.78))

            Text("Credits remaining: \(summary.creditsRemaining)")
                .foregroundStyle(Color.white.opacity(0.78))

            Text("Estimated turnaround: \(summary.estimatedTurnaround)")
                .foregroundStyle(Color.white.opacity(0.78))

            Text("AI provider: \(summary.aiProvider)")
                .foregroundStyle(Color.white.opacity(0.78))

            Text("Processing mode: \(summary.processingMode)")
                .foregroundStyle(Color.white.opacity(0.78))

            Text("Selection strategy: \(summary.selectionStrategy)")
                .foregroundStyle(Color.white.opacity(0.78))

            Text("Target platform: \(summary.targetPlatform)")
                .foregroundStyle(Color.white.opacity(0.78))

            if let sourceTitle = summary.sourceTitle, !sourceTitle.isEmpty {
                Text("Source title: \(sourceTitle)")
                    .foregroundStyle(Color.white.opacity(0.78))
            }

            if let sourceDurationSeconds = summary.sourceDurationSeconds {
                Text("Source duration: \(sourceDurationSeconds)s")
                    .foregroundStyle(Color.white.opacity(0.78))
            }

            Text("Assets created: \(summary.assetsCreated)")
                .foregroundStyle(Color.white.opacity(0.78))

            if let trendUsed = summary.trendUsed, !trendUsed.isEmpty {
                Text("Trend used: \(trendUsed)")
                    .foregroundStyle(Color.white.opacity(0.78))
            }

            Text("Sources considered: \(summary.sourcesConsidered.joined(separator: ", "))")
                .foregroundStyle(Color.white.opacity(0.78))

            Text(summary.recommendedNextStep)
                .font(.subheadline)
                .foregroundStyle(Color(red: 0.34, green: 0.89, blue: 0.82))
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

                VStack(alignment: .trailing, spacing: 4) {
                    Text("\(clip.score)")
                        .font(.headline.weight(.bold))
                        .foregroundStyle(Color(red: 0.34, green: 0.89, blue: 0.82))

                    Text(clip.format)
                        .font(.caption)
                        .foregroundStyle(Color.white.opacity(0.56))
                }
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

            if let clipURL = clip.clipURL, let url = URL(string: clipURL) {
                Link(destination: url) {
                    Text("Open Clip Asset")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.black)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 10)
                        .background(Color(red: 0.34, green: 0.89, blue: 0.82))
                        .clipShape(Capsule())
                }
            }

            if let transcriptExcerpt = clip.transcriptExcerpt, !transcriptExcerpt.isEmpty {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Transcript Excerpt")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color.white.opacity(0.62))

                    Text(transcriptExcerpt)
                        .font(.caption)
                        .foregroundStyle(Color.white.opacity(0.72))
                }
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

    @ViewBuilder
    private var historySection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("Saved Runs")
                    .font(.headline)
                    .foregroundStyle(.white)

                Spacer()

                if !viewModel.history.isEmpty {
                    Button("Clear") {
                        viewModel.clearHistory()
                    }
                    .font(.caption.weight(.medium))
                    .foregroundStyle(Color.white.opacity(0.62))
                }
            }

            if viewModel.history.isEmpty {
                statusCard(
                    title: "No history yet",
                    body: "Every successful generation is saved on this device so you can reopen and reshare it later.",
                    tint: Color.white.opacity(0.8)
                )
            } else {
                ForEach(viewModel.history) { run in
                    Button {
                        viewModel.restore(run: run)
                    } label: {
                        HStack(alignment: .top, spacing: 12) {
                            VStack(alignment: .leading, spacing: 6) {
                                Text(run.response.videoURL)
                                    .font(.subheadline.weight(.semibold))
                                    .foregroundStyle(.white)
                                    .multilineTextAlignment(.leading)

                                Text("\(run.response.clips.count) clips • \(run.response.processingSummary.planName)")
                                    .font(.caption)
                                    .foregroundStyle(Color.white.opacity(0.56))
                            }

                            Spacer()

                            Text(run.createdAt.formatted(date: .abbreviated, time: .shortened))
                                .font(.caption)
                                .foregroundStyle(Color.white.opacity(0.56))
                        }
                        .padding(16)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.white.opacity(0.05))
                        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    private func smallActionButton(title: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(.white)
                .padding(.horizontal, 12)
                .padding(.vertical, 9)
                .background(Color.white.opacity(0.08))
                .clipShape(Capsule())
        }
    }

    private func metricPill(_ title: String) -> some View {
        Text(title)
            .font(.caption.weight(.medium))
            .foregroundStyle(Color.white.opacity(0.76))
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color.white.opacity(0.05))
            .clipShape(Capsule())
    }

    private func badge(title: String, detail: String, tint: Color) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title.uppercased())
                .font(.caption2.weight(.bold))
                .foregroundStyle(tint)

            Text(detail)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.white)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .background(Color.white.opacity(0.05))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private func secondaryAction(title: String) -> some View {
        Text(title)
            .font(.subheadline.weight(.semibold))
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(Color.white.opacity(0.08))
            .foregroundStyle(.white)
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }
}

private struct SettingsSheet: View {
    @Environment(\.dismiss) private var dismiss
    @State private var apiBaseURL = AppConfiguration.apiBaseURL
    @State private var checkoutURL = AppConfiguration.checkoutURL
    @State private var apiKey = AppConfiguration.apiKey

    var body: some View {
        NavigationStack {
            Form {
                Section("Backend") {
                    TextField("API base URL", text: $apiBaseURL)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()

                    Text("Use `http://localhost:8000` for the simulator. Switch this to your hosted API when you launch.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Section("Optional Auth") {
                    TextField("API key", text: $apiKey)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()

                    Text("If your backend requires a custom header, the app will send this value as `x-api-key`.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                if !AppConfiguration.isAppStoreMode {
                    Section("Checkout") {
                        TextField("Checkout URL", text: $checkoutURL)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()

                        Text("Replace the placeholder with a real Stripe Payment Link or your checkout page.")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("Settings")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        AppConfiguration.save(
                            apiBaseURL: apiBaseURL,
                            checkoutURL: checkoutURL,
                            apiKey: apiKey
                        )
                        dismiss()
                    }
                }
            }
        }
    }
}

private struct PaywallSheet: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(\.openURL) private var openURL

    var body: some View {
        NavigationStack {
            ZStack {
                LinearGradient(
                    colors: [
                        Color(red: 0.08, green: 0.10, blue: 0.16),
                        Color(red: 0.03, green: 0.04, blue: 0.07),
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()

                VStack(alignment: .leading, spacing: 20) {
                    Text("Manage LWA on the web")
                        .font(.system(size: 30, weight: .bold, design: .rounded))
                        .foregroundStyle(.white)

                    Text("For App Store builds, payments and plan changes should be managed on the web. Keep the mobile app focused on clip generation and account usage.")
                        .font(.subheadline)
                        .foregroundStyle(Color.white.opacity(0.72))

                    pricingCard(
                        title: "Starter",
                        price: "Free",
                        bullets: "3 local generations, saved history, shareable bundles"
                    )

                    pricingCard(
                        title: "Creator",
                        price: "$29/mo",
                        bullets: "Unlimited clip packs, hosted API, export workflow"
                    )

                    pricingCard(
                        title: "Studio",
                        price: "$99/mo",
                        bullets: "Client seats, branded exports, priority processing"
                    )

                    if !AppConfiguration.isAppStoreMode {
                        Button {
                            if let url = URL(string: AppConfiguration.checkoutURL) {
                                openURL(url)
                            }
                        } label: {
                            Text("Open Checkout")
                                .font(.headline.weight(.semibold))
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

                        Text("Current checkout URL: \(AppConfiguration.checkoutURL)")
                            .font(.caption)
                            .foregroundStyle(Color.white.opacity(0.56))
                    } else {
                        Text("Web storefront: \(AppConfiguration.checkoutURL)")
                            .font(.caption)
                            .foregroundStyle(Color.white.opacity(0.56))
                    }

                    Spacer()
                }
                .padding(20)
            }
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Close") {
                        dismiss()
                    }
                }
            }
        }
        .preferredColorScheme(.dark)
    }

    private func pricingCard(title: String, price: String, bullets: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(title)
                    .font(.headline)
                    .foregroundStyle(.white)

                Spacer()

                Text(price)
                    .font(.headline.weight(.bold))
                    .foregroundStyle(Color(red: 0.34, green: 0.89, blue: 0.82))
            }

            Text(bullets)
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
}

#Preview {
    ContentView()
}
