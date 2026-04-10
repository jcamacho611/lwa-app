import AVKit
import SwiftUI
import UIKit

struct ContentView: View {
    @StateObject private var viewModel = ContentViewModel()
    @State private var showSettings = false
    @State private var showCopiedAlert = false
    @State private var copiedMessage = "The latest clip pack is now on your clipboard."
    @State private var selectedClipIndex = 0

    private var selectedClip: ClipResult? {
        guard !viewModel.clips.isEmpty else { return nil }
        let safeIndex = min(max(selectedClipIndex, 0), viewModel.clips.count - 1)
        return viewModel.clips[safeIndex]
    }

    var body: some View {
        NavigationStack {
            ZStack {
                cosmicBackground

                ScrollView(showsIndicators: false) {
                    VStack(alignment: .leading, spacing: 24) {
                        heroSection

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
        .onChange(of: viewModel.latestResponse?.requestID ?? "") { _ in
            selectedClipIndex = 0
        }
        .onChange(of: viewModel.clips.count) { count in
            if count == 0 {
                selectedClipIndex = 0
            } else if selectedClipIndex >= count {
                selectedClipIndex = count - 1
            }
        }
        .alert("Copied", isPresented: $showCopiedAlert) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(copiedMessage)
        }
    }

    private var cosmicBackground: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.03, green: 0.04, blue: 0.08),
                    Color(red: 0.03, green: 0.02, blue: 0.05),
                    Color(red: 0.01, green: 0.01, blue: 0.02),
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            RadialGradient(
                colors: [
                    Color(red: 0.23, green: 0.74, blue: 0.98).opacity(0.24),
                    .clear,
                ],
                center: .topTrailing,
                startRadius: 40,
                endRadius: 420
            )
            .ignoresSafeArea()

            RadialGradient(
                colors: [
                    Color(red: 0.94, green: 0.58, blue: 0.33).opacity(0.18),
                    .clear,
                ],
                center: .bottomLeading,
                startRadius: 30,
                endRadius: 320
            )
            .ignoresSafeArea()

            GeometryReader { geometry in
                ZStack {
                    Circle()
                        .fill(Color(red: 0.18, green: 0.68, blue: 0.91).opacity(0.24))
                        .frame(width: 240, height: 240)
                        .blur(radius: 36)
                        .offset(x: geometry.size.width * 0.32, y: -geometry.size.height * 0.26)

                    Circle()
                        .fill(Color(red: 0.96, green: 0.78, blue: 0.35).opacity(0.16))
                        .frame(width: 200, height: 200)
                        .blur(radius: 32)
                        .offset(x: -geometry.size.width * 0.30, y: geometry.size.height * 0.14)

                    ForEach(0 ..< 18, id: \.self) { index in
                        Circle()
                            .fill(Color.white.opacity(index.isMultiple(of: 3) ? 0.16 : 0.08))
                            .frame(width: CGFloat((index % 3) + 2), height: CGFloat((index % 3) + 2))
                            .offset(
                                x: CGFloat((index * 43) % 280) - 140,
                                y: CGFloat((index * 61) % 520) - 260
                            )
                    }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
            .ignoresSafeArea()
            .allowsHitTesting(false)
        }
    }

    private var heroSection: some View {
        VStack(alignment: .leading, spacing: 18) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 10) {
                    Text("IWA")
                        .font(.system(size: 40, weight: .bold, design: .rounded))
                        .foregroundStyle(.white)

                    Text("Automated content engine")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(Color(red: 0.34, green: 0.89, blue: 0.82))
                        .textCase(.uppercase)

                    Text("Turn one long-form source into a vertical review deck, caption pack, and ready-to-share assets with a single run.")
                        .font(.subheadline)
                        .foregroundStyle(Color.white.opacity(0.74))
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
                metricPill("Full-stack pipeline")
                metricPill(viewModel.selectedPlatform)
                metricPill(viewModel.creditsRemainingLabel)
            }

            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text(viewModel.generationStageTitle)
                        .font(.headline)
                        .foregroundStyle(.white)

                    Spacer()

                    Text(viewModel.latestResponse?.processingSummary.processingMode.uppercased() ?? "READY")
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(Color.black)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(Color(red: 0.34, green: 0.89, blue: 0.82))
                        .clipShape(Capsule())
                }

                Text(viewModel.generationStageDetail)
                    .font(.subheadline)
                    .foregroundStyle(Color.white.opacity(0.72))

                HStack(spacing: 10) {
                    ForEach(viewModel.generationTrack) { stage in
                        VStack(alignment: .leading, spacing: 6) {
                            Circle()
                                .fill(color(for: stage.status))
                                .frame(width: 10, height: 10)

                            Text(stage.title)
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(color(for: stage.status))
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
            }
            .padding(16)
            .background(Color.white.opacity(0.05))
            .overlay(
                RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .stroke(Color.white.opacity(0.08), lineWidth: 1)
            )
            .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
        }
        .padding(22)
        .background(.ultraThinMaterial.opacity(0.22))
        .overlay(
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .stroke(
                    LinearGradient(
                        colors: [
                            Color.white.opacity(0.16),
                            Color(red: 0.18, green: 0.68, blue: 0.91).opacity(0.28),
                            Color(red: 0.96, green: 0.78, blue: 0.35).opacity(0.20),
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ),
                    lineWidth: 1.2
                )
        )
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }

    private var launchReadinessCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Production Build")
                .font(.headline)
                .foregroundStyle(.white)

            Text("This mobile build is aimed at the live Railway stack over HTTPS. Use Settings only when you need to point the app back at your local backend.")
                .font(.subheadline)
                .foregroundStyle(Color.white.opacity(0.72))

            HStack(spacing: 12) {
                badge(title: "Backend", detail: "Railway", tint: Color(red: 0.34, green: 0.89, blue: 0.82))
                badge(title: "Mode", detail: "App Store", tint: Color(red: 0.96, green: 0.78, blue: 0.35))
                badge(title: "Output", detail: "Vertical clips", tint: Color(red: 0.72, green: 0.70, blue: 0.98))
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
            Text("Revenue Setup")
                .font(.headline)
                .foregroundStyle(.white)

            Text("Use the mobile app as the output console. Keep payment, plan upgrades, and client distribution on the web so the generation flow stays immediate.")
                .font(.subheadline)
                .foregroundStyle(Color.white.opacity(0.72))

            HStack(spacing: 12) {
                badge(title: "Plan", detail: viewModel.planName, tint: Color(red: 0.34, green: 0.89, blue: 0.82))
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
            Text("Source Command")
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
                            .buttonStyle(.plain)
                        }
                    }
                }
            }

            if let selectedTrend = viewModel.selectedTrend {
                statusCard(
                    title: "Trend angle locked",
                    body: "\(selectedTrend.title) • \(selectedTrend.source)",
                    tint: Color(red: 0.96, green: 0.78, blue: 0.35)
                )
            }

            Button {
                Task {
                    await viewModel.generateClips()
                }
            } label: {
                HStack(spacing: 12) {
                    if viewModel.isLoading {
                        ProgressView()
                            .tint(.black)
                    }

                    VStack(alignment: .leading, spacing: 2) {
                        Text(viewModel.isLoading ? "Generating Clip Pack" : "Generate Clips")
                            .fontWeight(.semibold)

                        Text(viewModel.isLoading ? "The review deck will refresh automatically." : "Launch the real backend pipeline.")
                            .font(.caption)
                            .foregroundStyle(Color.black.opacity(0.72))
                    }

                    Spacer()

                    Image(systemName: "sparkles.rectangle.stack.fill")
                        .font(.headline)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .padding(.horizontal, 16)
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
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            }
            .disabled(viewModel.isLoading)
            .opacity(viewModel.isLoading ? 0.84 : 1.0)
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

            Text("Public signals from Google Trends, Reddit, and Hacker News shape the hook angle before the run starts.")
                .font(.subheadline)
                .foregroundStyle(Color.white.opacity(0.68))

            if viewModel.trends.isEmpty {
                statusCard(
                    title: "Loading signals",
                    body: "Fetching public trends you can turn into hooks, angles, and caption framing.",
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
                Text("Review Deck")
                    .font(.headline)
                    .foregroundStyle(.white)

                Spacer()

                if !viewModel.lastSubmittedURL.isEmpty {
                    Text(viewModel.latestResponse?.sourcePlatform ?? "Ready")
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
                generationConsoleCard
            } else if viewModel.clips.isEmpty {
                statusCard(
                    title: "No review deck yet",
                    body: "Launch a run and the first output will appear here as a vertical swipe deck with export links, copy controls, and saved history below.",
                    tint: Color.white.opacity(0.8)
                )
            } else {
                reviewDeck
            }
        }
    }

    private var generationConsoleCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                VStack(alignment: .leading, spacing: 6) {
                    Text(viewModel.generationStageTitle)
                        .font(.headline)
                        .foregroundStyle(.white)

                    Text(viewModel.generationStageDetail)
                        .font(.subheadline)
                        .foregroundStyle(Color.white.opacity(0.72))
                }

                Spacer()

                ProgressView()
                    .tint(Color(red: 0.34, green: 0.89, blue: 0.82))
                    .scaleEffect(1.2)
            }

            HStack(spacing: 12) {
                ForEach(viewModel.generationTrack) { stage in
                    VStack(alignment: .leading, spacing: 8) {
                        Capsule()
                            .fill(color(for: stage.status))
                            .frame(height: 6)

                        Text(stage.title)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(color(for: stage.status))
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
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

    private var reviewDeck: some View {
        VStack(alignment: .leading, spacing: 18) {
            if let summary = viewModel.latestResponse?.processingSummary {
                reviewStageSummary(summary)
            }

            clipViewport

            HStack(spacing: 12) {
                Button {
                    copyToPasteboard(viewModel.shareText, confirmation: "The latest clip bundle is on your clipboard.")
                } label: {
                    secondaryAction(title: "Copy Bundle")
                }

                ShareLink(item: viewModel.shareText) {
                    secondaryAction(title: "Share")
                }
            }

            if let clip = selectedClip {
                clipInspector(clip)
            }

            if let summary = viewModel.latestResponse?.processingSummary {
                summaryMatrix(summary)
            }
        }
    }

    private var clipViewport: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Swipe through outputs")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.white)

                    Text("The first pass is already optimized for \(viewModel.selectedPlatform) review.")
                        .font(.caption)
                        .foregroundStyle(Color.white.opacity(0.62))
                }

                Spacer()

                if !viewModel.clips.isEmpty {
                    Text("\(selectedClipIndex + 1) / \(viewModel.clips.count)")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color.white.opacity(0.72))
                }
            }

            TabView(selection: $selectedClipIndex) {
                ForEach(Array(viewModel.clips.enumerated()), id: \.element.id) { index, clip in
                    ClipPreviewCard(
                        clip: clip,
                        platform: viewModel.selectedPlatform
                    )
                    .tag(index)
                }
            }
            .frame(height: 540)
            .tabViewStyle(.page(indexDisplayMode: .always))

            if let clip = selectedClip {
                VStack(alignment: .leading, spacing: 10) {
                    HStack {
                        Text(clip.title)
                            .font(.title3.weight(.semibold))
                            .foregroundStyle(.white)

                        Spacer()

                        scoreBadge(clip.score)
                    }

                    Text(clip.hook)
                        .font(.headline)
                        .foregroundStyle(Color.white.opacity(0.92))

                    HStack(spacing: 10) {
                        signalPill(label: "\(clip.startTime) - \(clip.endTime)")
                        signalPill(label: clip.format)
                        signalPill(label: clip.aspectRatio ?? "9:16")
                    }
                }
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

    private func clipInspector(_ clip: ClipResult) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("Selected Clip")
                    .font(.headline)
                    .foregroundStyle(.white)

                Spacer()

                if let editProfile = clip.editProfile, !editProfile.isEmpty {
                    Text(editProfile)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color.black)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(Color(red: 0.96, green: 0.78, blue: 0.35))
                        .clipShape(Capsule())
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

            HStack(spacing: 12) {
                Button {
                    copyToPasteboard(clip.hook, confirmation: "The hook is now on your clipboard.")
                } label: {
                    secondaryAction(title: "Copy Hook")
                }

                Button {
                    copyToPasteboard(clip.caption, confirmation: "The caption is now on your clipboard.")
                } label: {
                    secondaryAction(title: "Copy Caption")
                }
            }

            HStack(spacing: 12) {
                if let preferredAssetURL = clip.preferredAssetURL {
                    Link(destination: preferredAssetURL) {
                        primaryLinkAction(title: clip.editedClipURL != nil ? "Open Edited Clip" : "Open Clip Asset")
                    }
                }

                if let rawAssetURL = clip.rawAssetURL,
                   rawAssetURL != clip.preferredAssetURL {
                    Link(destination: rawAssetURL) {
                        secondaryAction(title: "Open Raw Cut")
                    }
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

    private func reviewStageSummary(_ summary: ProcessingSummary) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Run Summary")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.white)

            HStack(spacing: 12) {
                badge(title: "Mode", detail: summary.processingMode.capitalized, tint: Color(red: 0.34, green: 0.89, blue: 0.82))
                badge(title: "Selection", detail: summary.selectionStrategy.capitalized, tint: Color(red: 0.96, green: 0.78, blue: 0.35))
                badge(title: "AI", detail: summary.aiProvider, tint: Color(red: 0.72, green: 0.70, blue: 0.98))
            }

            Text(summary.recommendedNextStep)
                .font(.subheadline)
                .foregroundStyle(Color.white.opacity(0.72))
        }
        .padding(18)
        .background(Color.white.opacity(0.06))
        .overlay(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(Color.white.opacity(0.08), lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
    }

    private func summaryMatrix(_ summary: ProcessingSummary) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Run Intelligence")
                .font(.headline)
                .foregroundStyle(.white)

            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                insightTile(title: "Plan", value: summary.planName)
                insightTile(title: "Credits", value: "\(summary.creditsRemaining)")
                insightTile(title: "Turnaround", value: summary.estimatedTurnaround)
                insightTile(title: "Target", value: summary.targetPlatform)
                insightTile(title: "Assets", value: "\(summary.assetsCreated)")
                insightTile(title: "Edited", value: "\(summary.editedAssetsCreated)")

                if let sourceTitle = summary.sourceTitle, !sourceTitle.isEmpty {
                    insightTile(title: "Source Title", value: sourceTitle)
                }

                if let sourceDurationSeconds = summary.sourceDurationSeconds {
                    insightTile(title: "Source Length", value: "\(sourceDurationSeconds)s")
                }

                if let trendUsed = summary.trendUsed, !trendUsed.isEmpty {
                    insightTile(title: "Trend", value: trendUsed)
                }
            }

            VStack(alignment: .leading, spacing: 6) {
                Text("Sources Considered")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(Color.white.opacity(0.62))

                Text(summary.sourcesConsidered.joined(separator: ", "))
                    .font(.subheadline)
                    .foregroundStyle(Color.white.opacity(0.72))
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
                    body: "Every successful generation is saved on this device so you can reopen, reshare, or compare clip packs later.",
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

                                Text("\(run.response.clips.count) clips • \(run.response.processingSummary.planName) • \(run.response.processingSummary.targetPlatform)")
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

    private func insightTile(title: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title.uppercased())
                .font(.caption2.weight(.bold))
                .foregroundStyle(Color.white.opacity(0.56))

            Text(value)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.white)
        }
        .frame(maxWidth: .infinity, minHeight: 76, alignment: .leading)
        .padding(14)
        .background(Color.white.opacity(0.05))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private func scoreBadge(_ score: Int) -> some View {
        Text("\(score)")
            .font(.headline.weight(.bold))
            .foregroundStyle(.black)
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color(red: 0.34, green: 0.89, blue: 0.82))
            .clipShape(Capsule())
    }

    private func signalPill(label: String) -> some View {
        Text(label)
            .font(.caption.weight(.medium))
            .foregroundStyle(Color.white.opacity(0.78))
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color.white.opacity(0.07))
            .clipShape(Capsule())
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
                .lineLimit(2)
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

    private func primaryLinkAction(title: String) -> some View {
        Text(title)
            .font(.subheadline.weight(.semibold))
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
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
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    private func color(for status: GenerationTrackItem.Status) -> Color {
        switch status {
        case .pending:
            return Color.white.opacity(0.26)
        case .active:
            return Color(red: 0.34, green: 0.89, blue: 0.82)
        case .complete:
            return Color(red: 0.96, green: 0.78, blue: 0.35)
        }
    }

    private func copyToPasteboard(_ value: String, confirmation: String) {
        UIPasteboard.general.string = value
        copiedMessage = confirmation
        showCopiedAlert = true
    }
}

private struct ClipPreviewCard: View {
    let clip: ClipResult
    let platform: String

    var body: some View {
        ZStack(alignment: .bottomLeading) {
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .fill(Color.white.opacity(0.05))

            if let preferredAssetURL = clip.preferredAssetURL {
                LoopingVideoPlayer(url: preferredAssetURL)
                    .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
            } else {
                VStack(spacing: 14) {
                    Image(systemName: "sparkles.tv.fill")
                        .font(.system(size: 44))
                        .foregroundStyle(Color(red: 0.34, green: 0.89, blue: 0.82))

                    Text("Asset ready for export")
                        .font(.headline)
                        .foregroundStyle(.white)

                    Text("Open the generated file below if the inline preview is unavailable.")
                        .font(.subheadline)
                        .multilineTextAlignment(.center)
                        .foregroundStyle(Color.white.opacity(0.62))
                        .padding(.horizontal, 30)
                }
            }

            LinearGradient(
                colors: [
                    .clear,
                    Color.black.opacity(0.18),
                    Color.black.opacity(0.78),
                ],
                startPoint: .top,
                endPoint: .bottom
            )
            .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))

            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Text(platform)
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(Color.black)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(Color(red: 0.34, green: 0.89, blue: 0.82))
                        .clipShape(Capsule())

                    Spacer()

                    Text(clip.format)
                        .font(.caption.weight(.medium))
                        .foregroundStyle(Color.white.opacity(0.74))
                }

                VStack(alignment: .leading, spacing: 6) {
                    Text(clip.title)
                        .font(.title3.weight(.bold))
                        .foregroundStyle(.white)
                        .lineLimit(2)

                    Text(clip.hook)
                        .font(.subheadline)
                        .foregroundStyle(Color.white.opacity(0.82))
                        .lineLimit(3)
                }

                HStack(spacing: 10) {
                    clipMetric("\(clip.score)", label: "Score")
                    clipMetric(clip.startTime, label: "Start")
                    clipMetric(clip.endTime, label: "End")
                }
            }
            .padding(18)
        }
        .frame(maxWidth: .infinity)
        .overlay(
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .stroke(Color.white.opacity(0.08), lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }

    private func clipMetric(_ value: String, label: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label.uppercased())
                .font(.caption2.weight(.bold))
                .foregroundStyle(Color.white.opacity(0.52))

            Text(value)
                .font(.caption.weight(.semibold))
                .foregroundStyle(.white)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(Color.black.opacity(0.24))
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }
}

private struct LoopingVideoPlayer: View {
    let url: URL

    @State private var player = AVQueuePlayer()
    @State private var looper: AVPlayerLooper?

    var body: some View {
        VideoPlayer(player: player)
            .id(url.absoluteString)
            .onAppear {
                configurePlayerIfNeeded()
                player.play()
            }
            .onDisappear {
                player.pause()
                looper?.disableLooping()
                looper = nil
                player.removeAllItems()
            }
            .allowsHitTesting(false)
    }

    private func configurePlayerIfNeeded() {
        guard player.items().isEmpty else { return }

        player.isMuted = true
        player.actionAtItemEnd = .none
        let item = AVPlayerItem(url: url)
        looper = AVPlayerLooper(player: player, templateItem: item)
    }
}

private struct SettingsSheet: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(\.openURL) private var openURL
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

                    Text("Use `http://127.0.0.1:8000` for the simulator when you want to point the app at your local backend.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Section("Optional Auth") {
                    TextField("API key", text: $apiKey)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()

                    Text("If your backend requires a custom header, the app sends this value as `x-api-key`.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Section("Help") {
                    Button("Open Privacy Policy") {
                        if let url = URL(string: AppConfiguration.privacyPolicyURL) {
                            openURL(url)
                        }
                    }

                    Button("Open Support") {
                        if let url = URL(string: AppConfiguration.supportURL) {
                            openURL(url)
                        }
                    }
                }

                if !AppConfiguration.isAppStoreMode {
                    Section("Checkout") {
                        TextField("Checkout URL", text: $checkoutURL)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()

                        Text("Replace the placeholder with a real Stripe Payment Link or hosted checkout page.")
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
                    if AppConfiguration.isAppStoreMode {
                        Text("IWA Usage")
                            .font(.system(size: 30, weight: .bold, design: .rounded))
                            .foregroundStyle(.white)

                        Text("This build stays focused on clip generation. Use Settings when you need privacy or support information.")
                            .font(.subheadline)
                            .foregroundStyle(Color.white.opacity(0.72))

                        pricingCard(
                            title: "Need Help?",
                            price: "Support",
                            bullets: "Open Settings to reach the privacy policy and support pages."
                        )
                    } else {
                        Text("Manage IWA on the web")
                            .font(.system(size: 30, weight: .bold, design: .rounded))
                            .foregroundStyle(.white)

                        Text("Keep payments and plan changes on the web. Let the mobile app stay fast, focused, and operational.")
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
}

#Preview {
    ContentView()
}
