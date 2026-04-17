import AVKit
import SwiftUI
import UniformTypeIdentifiers
import UIKit

struct ContentView: View {
    @StateObject private var viewModel = ContentViewModel()
    @State private var selectedTab: OmegaTab = .home
    @State private var selectedClip: ClipResult?
    @State private var showSettings = false
    @State private var showFileImporter = false
    @State private var showCopiedAlert = false
    @State private var copiedMessage = ""

    var body: some View {
        NavigationStack {
            ZStack {
                OmegaBackground()

                TabView(selection: $selectedTab) {
                    OmegaHomeScreen(
                        viewModel: viewModel,
                        onOpenSettings: { showSettings = true },
                        onOpenUpload: { showFileImporter = true },
                        onOpenPaywall: { viewModel.showPaywall = true },
                        onOpenClip: { selectedClip = $0 },
                        onRestoreRun: {
                            viewModel.restore(run: $0)
                            selectedTab = .home
                        },
                        onCopyBundle: {
                            copyToPasteboard(viewModel.shareText, confirmation: "The full clip pack is now on your clipboard.")
                        }
                    )
                    .tag(OmegaTab.home)
                    .tabItem {
                        Label("Home", systemImage: "sparkles.tv")
                    }

                    OmegaHistoryScreen(
                        history: viewModel.history,
                        onRestoreRun: {
                            viewModel.restore(run: $0)
                            selectedTab = .home
                        },
                        onClearHistory: viewModel.clearHistory
                    )
                    .tag(OmegaTab.history)
                    .tabItem {
                        Label("History", systemImage: "clock.arrow.circlepath")
                    }
                }
                .tint(OmegaPalette.accent)
                .toolbar(.hidden, for: .navigationBar)
                .fileImporter(
                    isPresented: $showFileImporter,
                    allowedContentTypes: [.movie, .mpeg4Movie, .quickTimeMovie, .audio, .image],
                    allowsMultipleSelection: false,
                    onCompletion: handleFileSelection
                )

                if viewModel.isLoading || viewModel.isUploading {
                    OmegaProcessingOverlay(
                        title: viewModel.generationStageTitle,
                        detail: viewModel.generationStageDetail,
                        progress: viewModel.generationProgress,
                        steps: viewModel.generationTrack
                    )
                    .transition(.opacity.combined(with: .scale(scale: 0.98)))
                    .zIndex(10)
                }
            }
        }
        .preferredColorScheme(.dark)
        .sheet(item: $selectedClip) { clip in
            OmegaClipDetailView(
                clip: clip,
                onCopy: { value, message in
                    copyToPasteboard(value, confirmation: message)
                }
            )
        }
        .sheet(isPresented: $showSettings) {
            SettingsSheet()
        }
        .sheet(isPresented: $viewModel.showPaywall) {
            PaywallSheet()
        }
        .alert("Copied", isPresented: $showCopiedAlert) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(copiedMessage)
        }
    }

    private func handleFileSelection(_ result: Result<[URL], Error>) {
        switch result {
        case .success(let urls):
            guard let url = urls.first else { return }
            let canAccess = url.startAccessingSecurityScopedResource()
            defer {
                if canAccess {
                    url.stopAccessingSecurityScopedResource()
                }
            }

            Task {
                await viewModel.uploadVideo(fileURL: url)
            }
        case .failure(let error):
            copiedMessage = error.localizedDescription
            showCopiedAlert = true
        }
    }

    private func copyToPasteboard(_ value: String, confirmation: String) {
        UIPasteboard.general.string = value
        copiedMessage = confirmation
        showCopiedAlert = true
    }
}

private enum OmegaTab: Hashable {
    case home
    case history
}

private struct OmegaHomeScreen: View {
    @ObservedObject var viewModel: ContentViewModel
    let onOpenSettings: () -> Void
    let onOpenUpload: () -> Void
    let onOpenPaywall: () -> Void
    let onOpenClip: (ClipResult) -> Void
    let onRestoreRun: (SavedRun) -> Void
    let onCopyBundle: () -> Void

    var body: some View {
        ScrollView(showsIndicators: false) {
            VStack(alignment: .leading, spacing: 20) {
                hero
                sourceCommandCard
                recentRuns
                trends
                results
            }
            .padding(.horizontal, 20)
            .padding(.top, 16)
            .padding(.bottom, 32)
        }
    }

    private var hero: some View {
        OmegaGlassCard {
            VStack(alignment: .leading, spacing: 18) {
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("LWA Ω")
                            .font(.system(size: 36, weight: .bold, design: .serif))
                            .foregroundStyle(OmegaPalette.goldSoft)

                        Text("AI clipping engine")
                            .font(.caption.weight(.bold))
                            .foregroundStyle(OmegaPalette.goldSoft)
                            .textCase(.uppercase)

                        Text("Turn one source into ranked clips, hooks, captions, timestamps, and export-ready outputs.")
                            .font(.subheadline)
                            .foregroundStyle(OmegaPalette.secondaryText)
                    }

                    Spacer()

                    HStack(spacing: 10) {
                        OmegaGhostButton(title: "Pricing", action: onOpenPaywall)
                        OmegaGhostButton(title: "Settings", action: onOpenSettings)
                    }
                }

                HStack(spacing: 10) {
                    OmegaMetricPill(label: viewModel.processingStatusLabel)
                    OmegaMetricPill(label: viewModel.creditsRemainingLabel)
                    OmegaMetricPill(label: viewModel.premiumStatusLabel)
                    OmegaMetricPill(label: viewModel.planName)
                }
            }
        }
    }

    private var sourceCommandCard: some View {
        OmegaGlassCard {
            VStack(alignment: .leading, spacing: 16) {
                OmegaSectionHeader(
                    title: "Source command",
                    subtitle: "Run from a URL or uploaded file without leaving the app."
                )

                TextField("Paste a source URL", text: $viewModel.videoURL, axis: .vertical)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .padding(.horizontal, 16)
                    .padding(.vertical, 14)
                    .background(OmegaPalette.input)
                    .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                    .foregroundStyle(.white)

                HStack(spacing: 12) {
                    OmegaGhostButton(
                        title: viewModel.isUploading ? "Uploading..." : "Upload Source",
                        systemImage: "arrow.up.doc.fill",
                        action: onOpenUpload
                    )

                    if viewModel.selectedUpload != nil {
                        OmegaGhostButton(
                            title: "Clear Upload",
                            systemImage: "xmark.circle.fill",
                            action: viewModel.clearSelectedUpload
                        )
                    }
                }

                if let upload = viewModel.selectedUpload {
                    HStack(spacing: 10) {
                        OmegaMetricPill(label: upload.filename)
                        OmegaMetricPill(label: ByteCountFormatter.string(fromByteCount: Int64(upload.sizeBytes), countStyle: .file))
                    }
                }

                VStack(alignment: .leading, spacing: 10) {
                    Text("Target Platform")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(OmegaPalette.mutedText)

                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 10) {
                            ForEach(viewModel.supportedPlatforms, id: \.self) { platform in
                                Button {
                                    viewModel.selectedPlatform = platform
                                } label: {
                                    Text(platform)
                                        .font(.subheadline.weight(.semibold))
                                        .foregroundStyle(viewModel.selectedPlatform == platform ? .black : .white)
                                        .padding(.horizontal, 14)
                                        .padding(.vertical, 10)
                                        .background(
                                            viewModel.selectedPlatform == platform
                                                ? OmegaPalette.accent
                                                : OmegaPalette.card
                                        )
                                        .clipShape(Capsule())
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }
                }

                HStack(spacing: 12) {
                    OmegaMetricPill(label: viewModel.sourceSummaryLabel)
                    OmegaMetricPill(label: viewModel.premiumStatusLabel)
                }

                Button {
                    Task {
                        await viewModel.generateClips()
                    }
                } label: {
                    HStack(spacing: 12) {
                        Image(systemName: "sparkles.rectangle.stack.fill")
                            .font(.headline)
                        Text(viewModel.isLoading ? "Generating clip pack" : "Generate clip pack")
                            .font(.headline.weight(.semibold))
                        Spacer()
                        Text(viewModel.selectedPlatform)
                            .font(.caption.weight(.bold))
                    }
                }
                .buttonStyle(OmegaPrimaryButtonStyle())
                .disabled(viewModel.isLoading || viewModel.isUploading)
            }
        }
    }

    @ViewBuilder
    private var recentRuns: some View {
        VStack(alignment: .leading, spacing: 14) {
            OmegaSectionHeader(
                title: "Recent clip packs",
                subtitle: "Jump back into prior runs or compare new sources against recent output."
            )

            if viewModel.recentRuns.isEmpty {
                OmegaEmptyStateCard(
                    title: "No clip packs yet",
                    message: "Your recent packs will appear here once the first source has been processed."
                )
            } else {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 14) {
                        ForEach(viewModel.recentRuns) { run in
                            Button {
                                onRestoreRun(run)
                            } label: {
                                OmegaRecentRunCard(run: run)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.vertical, 2)
                }
            }
        }
    }

    @ViewBuilder
    private var trends: some View {
        VStack(alignment: .leading, spacing: 14) {
            OmegaSectionHeader(
                title: "Trend radar",
                subtitle: "Layer a live public signal into the packaging angle before you generate."
            )

            if viewModel.trends.isEmpty {
                OmegaEmptyStateCard(
                    title: "Loading signals",
                    message: "Public trends from Google Trends, Reddit, and Hacker News will appear here."
                )
            } else {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) {
                        ForEach(viewModel.trends) { trend in
                            Button {
                                viewModel.toggleTrend(trend)
                            } label: {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text(trend.source.uppercased())
                                        .font(.caption2.weight(.bold))
                                        .foregroundStyle(viewModel.selectedTrend == trend ? .black.opacity(0.7) : OmegaPalette.accent)

                                    Text(trend.title)
                                        .font(.subheadline.weight(.semibold))
                                        .foregroundStyle(viewModel.selectedTrend == trend ? .black : .white)
                                        .multilineTextAlignment(.leading)

                                    Text(trend.detail)
                                        .font(.caption)
                                        .foregroundStyle(viewModel.selectedTrend == trend ? .black.opacity(0.65) : OmegaPalette.secondaryText)
                                        .multilineTextAlignment(.leading)
                                }
                                .padding(16)
                                .frame(width: 220, alignment: .leading)
                                .background(viewModel.selectedTrend == trend ? OmegaPalette.accent : OmegaPalette.card)
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
    private var results: some View {
        VStack(alignment: .leading, spacing: 14) {
            OmegaSectionHeader(
                title: "Results",
                subtitle: "Lead clip first, then the ranked pack."
            )

            if let errorMessage = viewModel.errorMessage, !errorMessage.isEmpty {
                OmegaEmptyStateCard(title: "Request failed", message: errorMessage)
            } else if viewModel.clips.isEmpty {
                OmegaEmptyStateCard(
                    title: "No results yet",
                    message: "Run a source and the lead clip will appear here with ranking, copy, and export actions."
                )
            } else {
                if let bestClip = viewModel.bestClip {
                    OmegaGlassCard {
                        VStack(alignment: .leading, spacing: 14) {
                            HStack {
                                Text("Lead Clip")
                                    .font(.title3.weight(.bold))
                                    .foregroundStyle(.white)
                                Spacer()
                                OmegaMetricPill(label: "Rank #\(bestClip.displayRank ?? 1)")
                                OmegaMetricPill(label: bestClip.compilerConfidenceLabel ?? "Confidence pending")
                            }

                            OmegaClipVisual(clip: bestClip, height: 260)

                            Text(bestClip.hook)
                                .font(.title3.weight(.semibold))
                                .foregroundStyle(.white)

                            if let primaryReason = bestClip.primaryReason {
                                Text(primaryReason)
                                    .font(.subheadline)
                                    .foregroundStyle(OmegaPalette.secondaryText)
                            }

                            HStack(spacing: 10) {
                                OmegaMetricPill(label: bestClip.packagingAngleLabel ?? "Packaging pending")
                                OmegaMetricPill(label: "Score \(bestClip.score)")
                                if let bestPostOrder = bestClip.bestPostOrder {
                                    OmegaMetricPill(label: "Post #\(bestPostOrder)")
                                }
                                if bestClip.preferredAssetURL != nil {
                                    OmegaMetricPill(label: "Preview ready")
                                }
                            }

                            Button {
                                onOpenClip(bestClip)
                            } label: {
                                HStack {
                                    Text("Open Clip Detail")
                                    Spacer()
                                    Image(systemName: "arrow.up.right.circle.fill")
                                }
                            }
                            .buttonStyle(OmegaPrimaryButtonStyle())
                        }
                    }
                    .overlay(
                        RoundedRectangle(cornerRadius: 28, style: .continuous)
                            .stroke(OmegaPalette.accent.opacity(0.45), lineWidth: 1.2)
                    )
                    .shadow(color: OmegaPalette.accent.opacity(0.18), radius: 24, y: 16)
                }

                HStack(spacing: 12) {
                    Button(action: onCopyBundle) {
                        Label("Copy Bundle", systemImage: "doc.on.doc")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(OmegaSecondaryButtonStyle())

                    ShareLink(item: viewModel.shareText) {
                        Label("Share Pack", systemImage: "square.and.arrow.up")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(OmegaSecondaryButtonStyle())
                }

                VStack(spacing: 12) {
                    ForEach(viewModel.clips) { clip in
                        Button {
                            onOpenClip(clip)
                        } label: {
                            OmegaClipCard(clip: clip, isFeatured: clip.id == viewModel.bestClip?.id)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
        }
    }
}

private struct OmegaHistoryScreen: View {
    let history: [SavedRun]
    let onRestoreRun: (SavedRun) -> Void
    let onClearHistory: () -> Void

    var body: some View {
        ScrollView(showsIndicators: false) {
            VStack(alignment: .leading, spacing: 18) {
                OmegaGlassCard {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Text("History")
                                .font(.system(size: 28, weight: .bold, design: .rounded))
                                .foregroundStyle(.white)
                            Spacer()
                            if !history.isEmpty {
                                OmegaGhostButton(title: "Clear", action: onClearHistory)
                            }
                        }

                        Text("Reopen past videos, compare clip packs, and rerun sources without losing the original output context.")
                            .font(.subheadline)
                            .foregroundStyle(OmegaPalette.secondaryText)
                    }
                }

                if history.isEmpty {
                    OmegaEmptyStateCard(
                        title: "No saved runs",
                        message: "Once you generate a clip pack, it will appear here with quick reopen access."
                    )
                } else {
                    VStack(spacing: 12) {
                        ForEach(history) { run in
                            OmegaGlassCard {
                                VStack(alignment: .leading, spacing: 10) {
                                    Text(run.response.videoURL)
                                        .font(.headline)
                                        .foregroundStyle(.white)
                                        .lineLimit(2)

                                    HStack(spacing: 10) {
                                        OmegaMetricPill(label: "\(run.response.clips.count) clips")
                                        OmegaMetricPill(label: run.response.processingSummary.targetPlatform)
                                        OmegaMetricPill(label: run.createdAt.formatted(date: .abbreviated, time: .shortened))
                                    }

                                    Button {
                                        onRestoreRun(run)
                                    } label: {
                                        HStack {
                                            Text("Re-open Run")
                                            Spacer()
                                            Image(systemName: "arrow.clockwise.circle.fill")
                                        }
                                    }
                                    .buttonStyle(OmegaSecondaryButtonStyle())
                                }
                            }
                        }
                    }
                }
            }
            .padding(.horizontal, 20)
            .padding(.top, 16)
            .padding(.bottom, 32)
        }
    }
}

private struct OmegaClipCard: View {
    let clip: ClipResult
    let isFeatured: Bool

    var body: some View {
        OmegaGlassCard {
            HStack(spacing: 14) {
                OmegaClipVisual(clip: clip, height: 112, width: 94)

                VStack(alignment: .leading, spacing: 10) {
                    HStack {
                        Text(clip.title)
                            .font(.headline)
                            .foregroundStyle(.white)
                            .lineLimit(2)

                        Spacer()

                        Text("\(clip.score)")
                            .font(.caption.weight(.bold))
                            .foregroundStyle(.black)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(isFeatured ? OmegaPalette.gold : OmegaPalette.accent)
                            .clipShape(Capsule())
                    }

                    Text(clip.hook)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.white.opacity(0.92))
                        .lineLimit(2)

                    HStack(spacing: 8) {
                        if let displayRank = clip.displayRank {
                            OmegaMetricPill(label: "Rank #\(displayRank)")
                        }
                        if let packagingAngleLabel = clip.packagingAngleLabel {
                            OmegaMetricPill(label: packagingAngleLabel)
                        }
                        if let bestPostOrder = clip.bestPostOrder {
                            OmegaMetricPill(label: "Post #\(bestPostOrder)")
                        }
                        OmegaMetricPill(label: "\(clip.startTime)-\(clip.endTime)")
                    }

                    if let primaryReason = clip.primaryReason {
                        Text(primaryReason)
                            .font(.caption)
                            .foregroundStyle(OmegaPalette.secondaryText)
                            .lineLimit(2)
                    }
                }
            }
        }
    }
}

private struct OmegaClipDetailView: View {
    let clip: ClipResult
    let onCopy: (String, String) -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var trimStart: Double
    @State private var trimEnd: Double
    @State private var captionStyle = 0

    init(clip: ClipResult, onCopy: @escaping (String, String) -> Void) {
        self.clip = clip
        self.onCopy = onCopy
        let start = max(0, parseSeconds(clip.startTime))
        let end = max(start + 1, parseSeconds(clip.endTime))
        _trimStart = State(initialValue: start)
        _trimEnd = State(initialValue: end)
    }

    var body: some View {
        NavigationStack {
            ZStack {
                OmegaBackground()

                ScrollView(showsIndicators: false) {
                    VStack(alignment: .leading, spacing: 18) {
                        playerCard
                        whyItWorks
                        hookSuggestions
                        captionSection
                        editingControls
                        exportActions
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 16)
                    .padding(.bottom, 32)
                }
            }
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Close") {
                        dismiss()
                    }
                    .foregroundStyle(.white)
                }
            }
        }
        .preferredColorScheme(.dark)
    }

    private var playerCard: some View {
        OmegaGlassCard {
            VStack(alignment: .leading, spacing: 14) {
                if let assetURL = clip.preferredAssetURL {
                    OmegaVideoPlayer(url: assetURL)
                        .frame(height: 320)
                        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
                } else {
                    OmegaClipVisual(clip: clip, height: 320)
                }

                HStack {
                    Text(clip.title)
                        .font(.title2.weight(.bold))
                        .foregroundStyle(.white)
                    Spacer()
                    OmegaMetricPill(label: clip.compilerConfidenceLabel ?? "Confidence pending")
                }

                HStack(spacing: 10) {
                    if let displayRank = clip.displayRank {
                        OmegaMetricPill(label: "Rank #\(displayRank)")
                    }
                    if let packagingAngleLabel = clip.packagingAngleLabel {
                        OmegaMetricPill(label: packagingAngleLabel)
                    }
                    if let bestPostOrder = clip.bestPostOrder {
                        OmegaMetricPill(label: "Post #\(bestPostOrder)")
                    }
                }
            }
        }
    }

    private var whyItWorks: some View {
        OmegaGlassCard {
            VStack(alignment: .leading, spacing: 14) {
                OmegaSectionHeader(title: "Why this lands", subtitle: "AI signal for why this cut should win attention.")

                Text(clip.primaryReason ?? "Strong pacing, clear payoff, and creator-ready packaging.")
                    .font(.body.weight(.medium))
                    .foregroundStyle(.white.opacity(0.92))

                Divider()
                    .background(Color.white.opacity(0.08))

                HStack(alignment: .top, spacing: 12) {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("PLATFORM FIT")
                            .font(.caption2.weight(.bold))
                            .foregroundStyle(OmegaPalette.mutedText)
                        Text(clip.resolvedPlatformFit)
                            .font(.subheadline)
                            .foregroundStyle(OmegaPalette.secondaryText)
                    }
                    Spacer()
                }

                HStack(alignment: .top, spacing: 12) {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("CTA")
                            .font(.caption2.weight(.bold))
                            .foregroundStyle(OmegaPalette.mutedText)
                        Text(clip.resolvedCTA)
                            .font(.subheadline)
                            .foregroundStyle(OmegaPalette.secondaryText)
                    }
                    Spacer()
                }

                HStack(spacing: 10) {
                    OmegaMetricPill(label: clip.resolvedPackagingAngle.capitalized)
                    if let thumbnailText = clip.thumbnailText {
                        OmegaMetricPill(label: "🖼 \(thumbnailText)")
                    }
                }
            }
        }
    }

    private var hookSuggestions: some View {
        OmegaGlassCard {
            VStack(alignment: .leading, spacing: 12) {
                OmegaSectionHeader(title: "Hook angles", subtitle: "Tap any angle to copy it into your posting workflow.")

                ForEach(Array(clip.hookVariants.enumerated()), id: \.offset) { index, variant in
                    Button {
                        onCopy(variant, "Hook \(index + 1) copied.")
                    } label: {
                        HStack(alignment: .top, spacing: 12) {
                            Text("\(index + 1)")
                                .font(.caption.weight(.bold))
                                .foregroundStyle(.black)
                                .frame(width: 26, height: 26)
                                .background(OmegaPalette.accent)
                                .clipShape(Circle())

                            Text(variant)
                                .font(.subheadline.weight(.medium))
                                .foregroundStyle(.white)
                                .frame(maxWidth: .infinity, alignment: .leading)

                            Image(systemName: "doc.on.doc")
                                .foregroundStyle(OmegaPalette.secondaryText)
                        }
                        .padding(14)
                        .background(OmegaPalette.card)
                        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    private var captionSection: some View {
        OmegaGlassCard {
            VStack(alignment: .leading, spacing: 14) {
                OmegaSectionHeader(title: "Copy pack", subtitle: "Packaging copy and caption variants ready for export.")

                Text(clip.caption)
                    .font(.body)
                    .foregroundStyle(.white.opacity(0.88))

                Text("Thumbnail: \(clip.resolvedThumbnailText)")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(OmegaPalette.gold)

                Text("CTA: \(clip.resolvedCTA)")
                    .font(.subheadline)
                    .foregroundStyle(OmegaPalette.secondaryText)

                if let captionStyle = clip.captionStyle {
                    Text("Caption style: \(captionStyle)")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(OmegaPalette.goldSoft)
                }

                // Caption variants
                if !clip.resolvedCaptionVariants.isEmpty {
                    Divider()
                        .background(Color.white.opacity(0.08))

                    Text("CAPTION VARIANTS")
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(OmegaPalette.mutedText)

                    ForEach(clip.resolvedCaptionVariants.sorted(by: { $0.key < $1.key }), id: \.key) { key, value in
                        Button {
                            onCopy(value, "\(key.capitalized) caption copied.")
                        } label: {
                            VStack(alignment: .leading, spacing: 6) {
                                Text(key.uppercased())
                                    .font(.caption2.weight(.bold))
                                    .foregroundStyle(OmegaPalette.accent)
                                Text(value)
                                    .font(.subheadline)
                                    .foregroundStyle(.white.opacity(0.82))
                                    .frame(maxWidth: .infinity, alignment: .leading)
                            }
                            .padding(12)
                            .background(OmegaPalette.card)
                            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                        }
                        .buttonStyle(.plain)
                    }
                }

                HStack(spacing: 12) {
                    Button {
                        onCopy(clip.caption, "Caption copied.")
                    } label: {
                        Label("Copy Caption", systemImage: "text.quote")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(OmegaSecondaryButtonStyle())

                    Button {
                        onCopy(clip.packagingBundle, "Full package copied.")
                    } label: {
                        Label("Copy Package", systemImage: "doc.on.doc.fill")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(OmegaSecondaryButtonStyle())
                }
            }
        }
    }

    private var editingControls: some View {
        OmegaGlassCard {
            VStack(alignment: .leading, spacing: 14) {
                OmegaSectionHeader(title: "Editing Tools", subtitle: "Minimal control room for trim and caption presentation.")

                VStack(alignment: .leading, spacing: 8) {
                    Text("Trim Start")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(OmegaPalette.mutedText)
                    Slider(value: $trimStart, in: 0...max(trimEnd - 1, 1), step: 1)
                        .tint(OmegaPalette.accent)
                    Text(formatSeconds(trimStart))
                        .font(.caption)
                        .foregroundStyle(OmegaPalette.secondaryText)
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text("Trim End")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(OmegaPalette.mutedText)
                    Slider(value: $trimEnd, in: min(trimStart + 1, trimUpperBound)...trimUpperBound, step: 1)
                        .tint(OmegaPalette.gold)
                    Text(formatSeconds(trimEnd))
                        .font(.caption)
                        .foregroundStyle(OmegaPalette.secondaryText)
                }

                Picker("Caption Style", selection: $captionStyle) {
                    Text("Auto").tag(0)
                    Text("Minimal").tag(1)
                    Text("Bold").tag(2)
                }
                .pickerStyle(.segmented)

                Text("Preview trim: \(formatSeconds(trimStart)) – \(formatSeconds(trimEnd))")
                    .font(.footnote)
                    .foregroundStyle(OmegaPalette.secondaryText)
            }
        }
    }

    private var exportActions: some View {
        OmegaGlassCard {
            VStack(alignment: .leading, spacing: 12) {
                OmegaSectionHeader(title: "Export", subtitle: "Open the rendered asset or share the package immediately.")

                if let preferredAssetURL = clip.preferredAssetURL {
                    Link(destination: preferredAssetURL) {
                        Label("Open Export", systemImage: "arrow.up.right.square")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(OmegaPrimaryButtonStyle())
                }

                if let rawAssetURL = clip.rawAssetURL, rawAssetURL != clip.preferredAssetURL {
                    Link(destination: rawAssetURL) {
                        Label("Open Raw Clip", systemImage: "film.stack")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(OmegaSecondaryButtonStyle())
                }
            }
        }
    }

    private var trimUpperBound: Double {
        let suggestedEnd = max(parseSeconds(clip.endTime), trimStart + 1)
        return max(suggestedEnd, trimEnd, 15)
    }
}

private struct OmegaProcessingOverlay: View {
    let title: String
    let detail: String
    let progress: Double
    let steps: [GenerationTrackItem]

    var body: some View {
        ZStack {
            Color.black.opacity(0.45)
                .ignoresSafeArea()

            OmegaGlassCard {
                VStack(alignment: .leading, spacing: 18) {
                    HStack {
                        VStack(alignment: .leading, spacing: 6) {
                            Text(title)
                                .font(.title3.weight(.bold))
                                .foregroundStyle(.white)
                            Text(detail)
                                .font(.subheadline)
                                .foregroundStyle(OmegaPalette.secondaryText)
                        }

                        Spacer()

                        ProgressView()
                            .tint(OmegaPalette.accent)
                            .scaleEffect(1.2)
                    }

                    ProgressView(value: progress)
                        .tint(OmegaPalette.accent)
                        .progressViewStyle(.linear)

                    VStack(spacing: 10) {
                        ForEach(steps) { step in
                            HStack(spacing: 12) {
                                Circle()
                                    .fill(color(for: step.status))
                                    .frame(width: 10, height: 10)

                                Text(step.title)
                                    .font(.subheadline.weight(.medium))
                                    .foregroundStyle(color(for: step.status))

                                Spacer()
                            }
                        }
                    }
                }
            }
            .frame(maxWidth: 420)
            .padding(24)
        }
    }

    private func color(for status: GenerationTrackItem.Status) -> Color {
        switch status {
        case .pending:
            return OmegaPalette.mutedText
        case .active:
            return OmegaPalette.accent
        case .complete:
            return OmegaPalette.gold
        }
    }
}

private struct OmegaRecentRunCard: View {
    let run: SavedRun

    var body: some View {
        OmegaGlassCard {
            VStack(alignment: .leading, spacing: 12) {
                Text(run.response.processingSummary.sourceTitle ?? run.response.videoURL)
                    .font(.headline)
                    .foregroundStyle(.white)
                    .lineLimit(2)

                Text(run.response.processingSummary.targetPlatform)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(OmegaPalette.accent)

                HStack(spacing: 10) {
                    OmegaMetricPill(label: "\(run.response.clips.count) clips")
                    OmegaMetricPill(label: run.createdAt.formatted(date: .abbreviated, time: .shortened))
                }
            }
            .frame(width: 240, alignment: .leading)
        }
    }
}

private struct OmegaClipVisual: View {
    let clip: ClipResult
    var height: CGFloat
    var width: CGFloat? = nil

    var body: some View {
        ZStack(alignment: .bottomLeading) {
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [OmegaPalette.card, OmegaPalette.card.opacity(0.65), OmegaPalette.surface],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )

            if let previewURL = clip.previewImageAssetURL {
                AsyncImage(url: previewURL) { phase in
                    switch phase {
                    case .success(let image):
                        image
                            .resizable()
                            .scaledToFill()
                    default:
                        placeholder
                    }
                }
                .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
            } else {
                placeholder
            }

            LinearGradient(
                colors: [.clear, Color.black.opacity(0.76)],
                startPoint: .center,
                endPoint: .bottom
            )
            .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))

            VStack(alignment: .leading, spacing: 8) {
                if let thumbnailText = clip.thumbnailText {
                    Text(thumbnailText)
                        .font(.headline.weight(.bold))
                        .foregroundStyle(.white)
                        .lineLimit(2)
                }

                Text(clip.startTime + " – " + clip.endTime)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.white.opacity(0.78))
            }
            .padding(16)
        }
        .frame(width: width, height: height)
        .overlay(alignment: .center) {
            Image(systemName: "play.circle.fill")
                .font(.system(size: 34))
                .foregroundStyle(.white.opacity(0.88))
                .shadow(color: .black.opacity(0.34), radius: 12, y: 8)
        }
        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
    }

    private var placeholder: some View {
        LinearGradient(
            colors: [OmegaPalette.accent.opacity(0.24), OmegaPalette.gold.opacity(0.14), OmegaPalette.surface],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
}

private struct OmegaVideoPlayer: View {
    let url: URL
    @State private var player: AVPlayer?

    var body: some View {
        VideoPlayer(player: player)
            .onAppear {
                player = AVPlayer(url: url)
            }
            .onDisappear {
                player?.pause()
            }
    }
}

private struct OmegaGlassCard<Content: View>: View {
    @ViewBuilder var content: Content

    var body: some View {
        content
            .padding(18)
            .background(.ultraThinMaterial.opacity(0.18))
            .background(OmegaPalette.card.opacity(0.78))
            .overlay(
                RoundedRectangle(cornerRadius: 28, style: .continuous)
                    .stroke(
                        LinearGradient(
                            colors: [
                                Color.white.opacity(0.12),
                                OmegaPalette.accent.opacity(0.18),
                                OmegaPalette.gold.opacity(0.12),
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ),
                        lineWidth: 1
                    )
            )
            .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }
}

private struct OmegaSectionHeader: View {
    let title: String
    let subtitle: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.title3.weight(.bold))
                .foregroundStyle(.white)
            Text(subtitle)
                .font(.subheadline)
                .foregroundStyle(OmegaPalette.secondaryText)
        }
    }
}

private struct OmegaMetricPill: View {
    let label: String

    var body: some View {
        Text(label)
            .font(.caption.weight(.semibold))
            .foregroundStyle(.white.opacity(0.86))
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(OmegaPalette.card)
            .clipShape(Capsule())
    }
}

private struct OmegaEmptyStateCard: View {
    let title: String
    let message: String

    var body: some View {
        OmegaGlassCard {
            VStack(alignment: .leading, spacing: 10) {
                Text(title)
                    .font(.headline)
                    .foregroundStyle(.white)
                Text(message)
                    .font(.subheadline)
                    .foregroundStyle(OmegaPalette.secondaryText)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

private struct OmegaGhostButton: View {
    let title: String
    var systemImage: String? = nil
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                if let systemImage {
                    Image(systemName: systemImage)
                }
                Text(title)
            }
            .font(.subheadline.weight(.semibold))
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
            .background(OmegaPalette.card)
            .foregroundStyle(.white)
            .clipShape(Capsule())
        }
        .buttonStyle(.plain)
    }
}

private struct OmegaPrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding(.horizontal, 18)
            .padding(.vertical, 15)
            .background(
                LinearGradient(
                    colors: [OmegaPalette.accent, OmegaPalette.accentSecondary],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .foregroundStyle(.black)
            .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            .scaleEffect(configuration.isPressed ? 0.985 : 1)
            .animation(.spring(response: 0.28, dampingFraction: 0.88), value: configuration.isPressed)
    }
}

private struct OmegaSecondaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding(.horizontal, 16)
            .padding(.vertical, 14)
            .background(OmegaPalette.card)
            .foregroundStyle(.white)
            .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .stroke(Color.white.opacity(0.08), lineWidth: 1)
            )
            .scaleEffect(configuration.isPressed ? 0.985 : 1)
            .animation(.spring(response: 0.28, dampingFraction: 0.88), value: configuration.isPressed)
    }
}

private struct OmegaBackground: View {
    var body: some View {
        ZStack {
            LinearGradient(
                colors: [OmegaPalette.backgroundTop, OmegaPalette.backgroundMid, OmegaPalette.backgroundBottom],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            RadialGradient(
                colors: [OmegaPalette.accent.opacity(0.22), .clear],
                center: .topTrailing,
                startRadius: 20,
                endRadius: 380
            )
            .ignoresSafeArea()

            RadialGradient(
                colors: [OmegaPalette.gold.opacity(0.16), .clear],
                center: .bottomLeading,
                startRadius: 20,
                endRadius: 300
            )
            .ignoresSafeArea()
        }
    }
}

private enum OmegaPalette {
    static let backgroundTop = Color(red: 0.04, green: 0.03, blue: 0.02)
    static let backgroundMid = Color(red: 0.02, green: 0.02, blue: 0.02)
    static let backgroundBottom = Color(red: 0.01, green: 0.01, blue: 0.01)
    static let surface = Color(red: 0.12, green: 0.09, blue: 0.06)
    static let card = Color.white.opacity(0.055)
    static let input = Color.white.opacity(0.08)
    static let accent = Color(red: 0.85, green: 0.71, blue: 0.43)
    static let accentSecondary = Color(red: 0.67, green: 0.47, blue: 0.16)
    static let gold = Color(red: 0.96, green: 0.80, blue: 0.42)
    static let goldSoft = Color(red: 0.98, green: 0.91, blue: 0.75)
    static let secondaryText = Color.white.opacity(0.72)
    static let mutedText = Color.white.opacity(0.58)
}

private struct SettingsSheet: View {
    @Environment(\.dismiss) private var dismiss
    @State private var apiBaseURL = AppConfiguration.apiBaseURL
    @State private var checkoutURL = AppConfiguration.checkoutURL
    @State private var apiKey = AppConfiguration.apiKey

    var body: some View {
        NavigationStack {
            ZStack {
                OmegaBackground()

                ScrollView {
                    VStack(alignment: .leading, spacing: 18) {
                        OmegaGlassCard {
                            VStack(alignment: .leading, spacing: 14) {
                                OmegaSectionHeader(
                                    title: "Settings",
                                    subtitle: "Point the app at a different backend or update checkout preferences."
                                )

                                settingsField(title: "API Base URL", value: $apiBaseURL)
                                settingsField(title: "Checkout URL", value: $checkoutURL)
                                settingsField(title: "API Key", value: $apiKey)

                                Button("Save") {
                                    AppConfiguration.save(
                                        apiBaseURL: apiBaseURL,
                                        checkoutURL: checkoutURL,
                                        apiKey: apiKey
                                    )
                                    dismiss()
                                }
                                .buttonStyle(OmegaPrimaryButtonStyle())
                            }
                        }

                        OmegaGlassCard {
                            VStack(alignment: .leading, spacing: 10) {
                                Text("Support")
                                    .font(.headline)
                                    .foregroundStyle(.white)

                                Link("Privacy Policy", destination: URL(string: AppConfiguration.privacyPolicyURL)!)
                                    .foregroundStyle(OmegaPalette.accent)
                                Link("Support", destination: URL(string: AppConfiguration.supportURL)!)
                                    .foregroundStyle(OmegaPalette.accent)
                            }
                        }
                    }
                    .padding(20)
                }
            }
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Close") {
                        dismiss()
                    }
                    .foregroundStyle(.white)
                }
            }
        }
        .preferredColorScheme(.dark)
    }

    private func settingsField(title: String, value: Binding<String>) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(OmegaPalette.mutedText)
            TextField(title, text: value, axis: .vertical)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .padding(.horizontal, 14)
                .padding(.vertical, 12)
                .background(OmegaPalette.input)
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                .foregroundStyle(.white)
        }
    }
}

private struct PaywallSheet: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(\.openURL) private var openURL

    var body: some View {
        NavigationStack {
            ZStack {
                OmegaBackground()

                ScrollView {
                    VStack(alignment: .leading, spacing: 18) {
                        OmegaGlassCard {
                            VStack(alignment: .leading, spacing: 12) {
                                Text("LWA Omega Plans")
                                    .font(.system(size: 30, weight: .bold, design: .rounded))
                                    .foregroundStyle(.white)

                                Text("Unlock more clip volume, stronger packaging tools, and faster operator workflows without slowing the mobile experience down.")
                                    .font(.subheadline)
                                    .foregroundStyle(OmegaPalette.secondaryText)
                            }
                        }

                        pricingCard(title: "Free", price: "Starter", bullets: "3 clips per run, local history, packaged exports")
                        pricingCard(title: "Pro", price: "$29/mo", bullets: "20 clips, alternate hooks, premium exports, faster iteration")
                        pricingCard(title: "Scale", price: "$99/mo", bullets: "40 clips, campaign mode, workflow leverage, queue-first execution")

                        Button {
                            if let url = URL(string: AppConfiguration.checkoutURL) {
                                openURL(url)
                            }
                        } label: {
                            Label("Open Checkout", systemImage: "arrow.up.right.square")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(OmegaPrimaryButtonStyle())
                    }
                    .padding(20)
                }
            }
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Close") {
                        dismiss()
                    }
                    .foregroundStyle(.white)
                }
            }
        }
        .preferredColorScheme(.dark)
    }

    private func pricingCard(title: String, price: String, bullets: String) -> some View {
        OmegaGlassCard {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text(title)
                        .font(.headline)
                        .foregroundStyle(.white)
                    Spacer()
                    Text(price)
                        .font(.headline.weight(.bold))
                        .foregroundStyle(OmegaPalette.accent)
                }

                Text(bullets)
                    .font(.subheadline)
                    .foregroundStyle(OmegaPalette.secondaryText)
            }
        }
    }
}

private extension ClipResult {
    var preferredAssetURL: URL? {
        if let editedClipURL, let url = URL(string: editedClipURL) {
            return url
        }
        if let clipURL, let url = URL(string: clipURL) {
            return url
        }
        if let rawClipURL, let url = URL(string: rawClipURL) {
            return url
        }
        return nil
    }

    var rawAssetURL: URL? {
        guard let rawClipURL else { return nil }
        return URL(string: rawClipURL)
    }

    var previewImageAssetURL: URL? {
        guard let previewImageURL else { return nil }
        return URL(string: previewImageURL)
    }

    var packagingBundle: String {
        let alternateHooks = resolvedHookVariants.joined(separator: "\n")
        let captionVariantLines = resolvedCaptionVariants
            .sorted(by: { $0.key < $1.key })
            .map { "  \($0.key): \($0.value)" }
            .joined(separator: "\n")
        return """
        Title: \(title)
        Rank: \(displayRank.map(String.init) ?? "not available")
        Confidence: \(compilerConfidenceLabel ?? "not available")
        Packaging angle: \(resolvedPackagingAngle)
        Hook: \(hook)
        Caption: \(caption)
        Why this works: \(primaryReason ?? "Strong pacing, clear payoff, and creator-ready packaging.")
        Platform fit: \(resolvedPlatformFit)
        Thumbnail text: \(resolvedThumbnailText)
        CTA: \(resolvedCTA)
        Alternate hooks:
        \(alternateHooks)
        Caption variants:
        \(captionVariantLines)
        """
    }

    var displayRank: Int? {
        rank ?? postRank
    }

    var compilerConfidenceValue: String? {
        if let confidence {
            return "\(Int((confidence * 100).rounded()))%"
        }
        if let confidenceScore {
            return "\(confidenceScore)%"
        }
        return nil
    }

    var compilerConfidenceLabel: String? {
        guard let compilerConfidenceValue else { return nil }
        return "Confidence \(compilerConfidenceValue)"
    }

    var packagingAngleLabel: String? {
        guard let packagingAngle, !packagingAngle.isEmpty else { return nil }
        return packagingAngle.replacingOccurrences(of: "_", with: " ").capitalized
    }

    var primaryReason: String? {
        if let reason, !reason.isEmpty {
            return reason
        }
        if let whyThisMatters, !whyThisMatters.isEmpty {
            return whyThisMatters
        }
        return nil
    }
}

private func parseSeconds(_ timestamp: String) -> Double {
    let parts = timestamp.split(separator: ":").compactMap { Double($0) }
    switch parts.count {
    case 2:
        return (parts[0] * 60) + parts[1]
    case 3:
        return (parts[0] * 3600) + (parts[1] * 60) + parts[2]
    default:
        return 0
    }
}

private func formatSeconds(_ seconds: Double) -> String {
    let value = Int(seconds.rounded())
    let minutes = value / 60
    let remainder = value % 60
    return String(format: "%02d:%02d", minutes, remainder)
}

#Preview {
    ContentView()
}
