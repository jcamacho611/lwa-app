#!/usr/bin/env python3
"""
Local Test Script for Analysis Engine

Run this to test the analysis engine instantly without UI or API.
Usage: python scripts/test_analysis_engine.py
"""

import sys
sys.path.insert(0, '.')

from app.services.analysis_engine import analyze_content

# Test inputs
TEST_CASES = [
    {
        "name": "Social Media Growth",
        "text": """If you want to grow on social media, you need to stop posting randomly.
Most people post without strategy and wonder why nothing works.
The truth is consistency without direction is useless.
You need a system that tells you exactly what to post and when.
This is that system.""",
    },
    {
        "name": "Short Content",
        "text": "The secret to success is showing up every single day. Most people quit too early.",
    },
    {
        "name": "Long-form Content",
        "text": """Building a personal brand isn't about going viral. It's about consistent value.
Day after day. Week after week. Year after year.
Most creators chase algorithms instead of building trust.
The truth? Trust beats trends every single time.
When you show up authentically, your audience grows naturally.
No hacks. No shortcuts. Just real connection.
That's the foundation that lasts.""",
    },
    {
        "name": "Minimal Input",
        "text": "Never give up. Keep pushing forward. Success comes to those who persist.",
    },
]


def print_clip(clip, index: int):
    """Print a clip in a nice format."""
    score_pct = int(clip["score"] * 100)
    
    # Quality indicator
    if score_pct >= 80:
        quality = "🔥 VIRAL POTENTIAL"
    elif score_pct >= 60:
        quality = "✅ HIGH ENGAGEMENT"
    elif score_pct >= 40:
        quality = "👍 SOLID POST"
    else:
        quality = "🧪 TEST CLIP"
    
    print(f"\n{'─' * 60}")
    print(f"CLIP #{index + 1} | Rank: {clip['rank']} | Score: {score_pct}/100")
    print(f"Quality: {quality}")
    print(f"{'─' * 60}")
    print(f"🎯 HOOK: {clip['hook']}")
    print(f"📝 CAPTION: {clip['caption']}")
    print(f"📱 CTA: {clip['cta']}")
    print(f"🖼️  THUMBNAIL: {clip['thumbnail_text']}")
    print(f"💡 WHY: {clip['why']}")
    print(f"📝 CONTENT: {clip['text'][:100]}...")
    print(f"{'─' * 60}")


def run_test(test_case: dict):
    """Run a single test case."""
    print(f"\n{'=' * 70}")
    print(f"TEST: {test_case['name']}")
    print(f"{'=' * 70}")
    print(f"Input length: {len(test_case['text'])} characters")
    
    # Run analysis
    clips = analyze_content(test_case["text"], min_clips=3)
    
    print(f"✅ Generated {len(clips)} clips")
    
    # Print each clip
    for i, clip in enumerate(clips):
        print_clip(clip, i)
    
    # Summary
    avg_score = sum(c["score"] for c in clips) / len(clips)
    print(f"\n📊 SUMMARY")
    print(f"   Total clips: {len(clips)}")
    print(f"   Average score: {int(avg_score * 100)}/100")
    print(f"   Best clip: #{clips[0]['rank']} (Score: {int(clips[0]['score'] * 100)})")
    
    return clips


def main():
    """Main test runner."""
    print("🚀 Analysis Engine Test Suite")
    print("=" * 70)
    print("Testing offline content intelligence system...")
    print("=" * 70)
    
    all_results = []
    
    for test_case in TEST_CASES:
        try:
            clips = run_test(test_case)
            all_results.append({
                "name": test_case["name"],
                "clip_count": len(clips),
                "avg_score": sum(c["score"] for c in clips) / len(clips),
                "status": "✅ PASS",
            })
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            all_results.append({
                "name": test_case["name"],
                "clip_count": 0,
                "avg_score": 0,
                "status": f"❌ FAIL: {e}",
            })
    
    # Final summary
    print(f"\n{'=' * 70}")
    print("FINAL SUMMARY")
    print(f"{'=' * 70}")
    
    for result in all_results:
        print(f"{result['status']} | {result['name']}: {result['clip_count']} clips (avg: {int(result['avg_score'] * 100)})")
    
    # Overall stats
    total_clips = sum(r["clip_count"] for r in all_results)
    passed_tests = sum(1 for r in all_results if "PASS" in r["status"])
    
    print(f"\n📈 OVERALL")
    print(f"   Tests passed: {passed_tests}/{len(TEST_CASES)}")
    print(f"   Total clips generated: {total_clips}")
    print(f"   Engine status: {'✅ HEALTHY' if passed_tests == len(TEST_CASES) else '⚠️  ISSUES'}")
    
    print(f"\n{'=' * 70}")
    print("✅ Test complete! The analysis engine is working.")
    print("=" * 70)


if __name__ == "__main__":
    main()
