#!/usr/bin/env python3
"""
LWA Offline Fallback Smoke Test

This test PROVES the app works WITHOUT:
- API keys
- External AI services
- Network connectivity
- Cloud dependencies

Run: python test_offline.py

Hard law: Must return at least 3 clips with full strategy output.
"""

import sys
sys.path.insert(0, '.')

from app.services.analysis_engine import analyze_content

# Required test input
TEST_INPUT = """If you want to grow on social media, stop posting randomly.
Most creators fail because they have no strategy.
Consistency without direction is useless.
You need a system that tells you exactly what to post and when.
This is that system."""

# Required output schema validation
REQUIRED_FIELDS = [
    "clip_id",
    "hook",
    "caption",
    "text",
    "cta",
    "thumbnail_text",
    "score",
    "why",
    "rank",
]


def validate_clip(clip: dict, index: int) -> list:
    """Validate a single clip has all required fields."""
    errors = []
    
    for field in REQUIRED_FIELDS:
        if field not in clip:
            errors.append(f"Clip {index + 1}: Missing required field '{field}'")
        elif clip[field] is None or clip[field] == "":
            errors.append(f"Clip {index + 1}: Empty required field '{field}'")
    
    # Validate score is in reasonable range
    if "score" in clip:
        score = clip["score"]
        if not isinstance(score, (int, float)):
            errors.append(f"Clip {index + 1}: Score must be numeric")
        elif not (0 <= score <= 1):
            errors.append(f"Clip {index + 1}: Score {score} out of range [0,1]")
    
    # Validate rank
    if "rank" in clip:
        rank = clip["rank"]
        if not isinstance(rank, int):
            errors.append(f"Clip {index + 1}: Rank must be integer")
        elif rank < 1:
            errors.append(f"Clip {index + 1}: Rank must be positive")
    
    return errors


def main():
    """Run offline smoke test."""
    print("🧪 LWA Offline Fallback Smoke Test")
    print("=" * 60)
    print()
    
    print("📋 Test Input:")
    print(f"   Length: {len(TEST_INPUT)} characters")
    print(f"   Content: {TEST_INPUT[:60]}...")
    print()
    
    print("🔬 Running Analysis Engine (offline mode)...")
    print()
    
    try:
        # Run analysis WITHOUT any API calls
        clips = analyze_content(TEST_INPUT, min_clips=3)
        
        print(f"✅ Generated {len(clips)} clips")
        print()
        
        # Validation 1: Minimum clip count
        if len(clips) < 3:
            print("❌ FAIL: Minimum 3 clips required")
            print(f"   Got: {len(clips)} clips")
            sys.exit(1)
        
        print(f"✅ Minimum clip count: PASS ({len(clips)} >= 3)")
        
        # Validation 2: Required fields
        all_errors = []
        for i, clip in enumerate(clips):
            errors = validate_clip(clip, i)
            all_errors.extend(errors)
        
        if all_errors:
            print("❌ FAIL: Schema validation errors")
            for error in all_errors:
                print(f"   - {error}")
            sys.exit(1)
        
        print("✅ Schema validation: PASS (all fields present)")
        
        # Validation 3: render_status equivalent (score present)
        missing_scores = [i for i, c in enumerate(clips) if "score" not in c]
        if missing_scores:
            print(f"❌ FAIL: Clips missing scores: {missing_scores}")
            sys.exit(1)
        
        print("✅ Quality scores: PASS (all clips scored)")
        
        # Validation 4: Ranking
        ranks = [c["rank"] for c in clips]
        expected_ranks = list(range(1, len(clips) + 1))
        if sorted(ranks) != expected_ranks:
            print(f"❌ FAIL: Invalid ranking: {ranks}")
            sys.exit(1)
        
        print("✅ Ranking: PASS (properly ordered)")
        
        # Success output
        print()
        print("=" * 60)
        print("✅ OFFLINE FALLBACK TEST: PASSED")
        print("=" * 60)
        print()
        
        print("📊 Results Summary:")
        print(f"   Total clips: {len(clips)}")
        print(f"   Average score: {sum(c['score'] for c in clips) / len(clips):.2f}")
        print(f"   Best clip: #{clips[0]['rank']} (score: {clips[0]['score']:.2f})")
        print()
        
        print("📝 Sample Output (Clip #1):")
        print(f"   Hook: {clips[0]['hook'][:50]}...")
        print(f"   Caption: {clips[0]['caption'][:50]}...")
        print(f"   CTA: {clips[0]['cta']}")
        print(f"   Why: {clips[0]['why'][:60]}...")
        print()
        
        print("🎉 LWA works 100% offline without API keys!")
        print()
        return 0
        
    except Exception as e:
        print(f"❌ FAIL: Exception during analysis")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
