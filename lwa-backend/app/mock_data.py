from .schemas import ClipResult


def build_mock_clips(video_url: str) -> list[ClipResult]:
    source_label = video_url.split("//")[-1].split("/")[0]

    return [
        ClipResult(
            id="clip_001",
            title="Fast Value Hook",
            hook="Stop scrolling if you want the shortest path to better videos.",
            caption=(
                f"Pulled from {source_label}: lead with the outcome first, then show the proof "
                "before the audience swipes away."
            ),
            start_time="00:03",
            end_time="00:18",
        ),
        ClipResult(
            id="clip_002",
            title="Contrarian Take",
            hook="Most creators are editing too much and saying too little.",
            caption=(
                "This cut turns one opinion into a punchy short: one sharp claim, one example, "
                "one takeaway."
            ),
            start_time="00:24",
            end_time="00:39",
        ),
        ClipResult(
            id="clip_003",
            title="Story-Based CTA",
            hook="Here is the exact moment the content started working.",
            caption=(
                "Use this clip as the payoff moment, then close with a simple call to action to "
                "push comments or follows."
            ),
            start_time="00:47",
            end_time="01:04",
        ),
    ]

