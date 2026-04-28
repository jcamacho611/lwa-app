from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from app.processor import (
    build_transcript_timing_from_segments,
    build_transcript_words_from_response,
    load_transcript_timing,
    parse_vtt_transcript,
)


class SegmentWord:
    def __init__(self, start: float, end: float, word: str, confidence: float | None = None) -> None:
        self.start = start
        self.end = end
        self.word = word
        self.confidence = confidence


class TranscriptSegment:
    def __init__(self, start: float, end: float, text: str, words: list[SegmentWord] | None = None) -> None:
        self.start = start
        self.end = end
        self.text = text
        self.words = words or []


class ProcessorTranscriptTimingTests(unittest.TestCase):
    def test_build_transcript_words_from_response_preserves_timing(self) -> None:
        words = build_transcript_words_from_response(
            [
                SegmentWord(0.0, 0.3, "Stop", 0.91),
                {"start": 0.31, "end": 0.6, "word": "scrolling", "confidence": 0.88},
            ]
        )

        self.assertEqual(len(words), 2)
        self.assertEqual(words[0].text, "Stop")
        self.assertAlmostEqual(words[1].start_seconds, 0.31, places=2)
        self.assertAlmostEqual(words[1].end_seconds, 0.6, places=2)

    def test_build_transcript_timing_from_segments_returns_windows_and_cues(self) -> None:
        segments = [
            TranscriptSegment(
                0.0,
                3.0,
                "Stop posting random clips if you want better retention.",
                words=[
                    SegmentWord(0.0, 0.2, "Stop"),
                    SegmentWord(0.21, 0.45, "posting"),
                    SegmentWord(0.46, 0.7, "random"),
                ],
            ),
            TranscriptSegment(
                3.2,
                7.8,
                "Lead with the payoff line before the setup drags.",
                words=[
                    SegmentWord(3.2, 3.5, "Lead"),
                    SegmentWord(3.51, 3.8, "with"),
                    SegmentWord(3.81, 4.1, "the"),
                ],
            ),
        ]

        windows, cues = build_transcript_timing_from_segments(segments)

        self.assertEqual(len(cues), 2)
        self.assertEqual(cues[0].text, "Stop posting random clips if you want better retention.")
        self.assertEqual(len(cues[0].words), 3)
        self.assertTrue(windows)
        self.assertIn("payoff", windows[0].excerpt.lower())

    def test_parse_vtt_transcript_returns_cues_without_fake_word_timing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            vtt_path = Path(temp_dir) / "captions.vtt"
            vtt_path.write_text(
                textwrap.dedent(
                    """\
                    WEBVTT

                    00:00:00.000 --> 00:00:02.500
                    Stop posting random clips.

                    00:00:02.600 --> 00:00:05.400
                    Lead with the payoff first.
                    """
                ),
                encoding="utf-8",
            )

            windows, cues, words = parse_vtt_transcript(vtt_path)

            self.assertEqual(len(cues), 2)
            self.assertEqual(cues[0].text, "Stop posting random clips.")
            self.assertEqual(words, [])
            self.assertTrue(windows)

    def test_load_transcript_timing_reads_vtt_from_work_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            work_dir = Path(temp_dir)
            (work_dir / "nested").mkdir()
            vtt_path = work_dir / "nested" / "captions.vtt"
            vtt_path.write_text(
                textwrap.dedent(
                    """\
                    WEBVTT

                    00:00:00.000 --> 00:00:03.200
                    This transcript cue should be discovered from disk.
                    """
                ),
                encoding="utf-8",
            )

            windows, cues, words = load_transcript_timing(work_dir)

            self.assertEqual(len(cues), 1)
            self.assertEqual(cues[0].text, "This transcript cue should be discovered from disk.")
            self.assertTrue(windows)
            self.assertEqual(words, [])


if __name__ == "__main__":
    unittest.main()
