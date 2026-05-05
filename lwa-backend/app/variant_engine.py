"""
Variant Generator Engine
Creates alternate clip edits without reprocessing video.
Uses existing clips to generate new combinations.
"""
import random
from typing import List, Dict
from pydantic import BaseModel


class VariantClip(BaseModel):
    variant_id: str
    clip_order: List[str]  # Ordered list of clip IDs
    hooks: List[str]
    total_duration: float
    strategy_notes: str


def generate_reorder_variants(
    base_clip_ids: List[str],
    request_id: str,
    count: int = 3
) -> List[VariantClip]:
    """
    Generate variants by reordering existing clips.
    Keeps content the same, changes narrative flow.
    """
    variants = []
    
    for i in range(count):
        # Shuffle clip order
        shuffled = base_clip_ids.copy()
        random.shuffle(shuffled)
        
        variant_id = f"{request_id}-var-{i+1:02d}"
        
        # Generate strategy notes
        strategies = [
            "Lead with strongest hook",
            "Build tension progressively",
            "Start with payoff, then explain",
            "Problem → Solution format",
            "Story → Lesson format"
        ]
        
        # Generate hooks for this variant
        hooks = [
            f"Take {i+1}: The reordered edit",
            f"Variant {i+1}: Different flow",
            f"Alternative cut #{i+1}"
        ]
        
        variant = VariantClip(
            variant_id=variant_id,
            clip_order=shuffled,
            hooks=hooks,
            total_duration=0.0,  # Would calculate from actual clips
            strategy_notes=random.choice(strategies)
        )
        variants.append(variant)
    
    return variants


def generate_hook_variants(
    base_clip_ids: List[str],
    base_hooks: List[str],
    request_id: str,
    count: int = 3
) -> List[VariantClip]:
    """
    Generate variants with different hooks/captions for same clips.
    Content order stays same, messaging changes.
    """
    variants = []
    
    hook_styles = [
        ["You won't believe...", "The truth about...", "Stop making this mistake..."],
        ["Here's why...", "The secret to...", "What nobody tells you..."],
        ["I was today years old...", "This changes everything...", "Mind = blown..."]
    ]
    
    for i in range(count):
        variant_id = f"{request_id}-hook-var-{i+1:02d}"
        
        variant = VariantClip(
            variant_id=variant_id,
            clip_order=base_clip_ids,
            hooks=hook_styles[i % len(hook_styles)],
            total_duration=0.0,
            strategy_notes=f"Hook variant set {i+1}: Testing different emotional triggers"
        )
        variants.append(variant)
    
    return variants


def generate_length_variants(
    base_clip_ids: List[str],
    request_id: str,
    target_durations: List[float] = [15.0, 30.0, 60.0]
) -> List[VariantClip]:
    """
    Generate variants at different lengths.
    Shorter = more punchy, longer = more context.
    """
    variants = []
    
    for i, target_duration in enumerate(target_durations):
        variant_id = f"{request_id}-len-var-{i+1:02d}"
        
        # For MVP, use all clips (in production, select subset to hit duration)
        selected_clips = base_clip_ids[:max(1, int(target_duration / 30))]
        
        variant = VariantClip(
            variant_id=variant_id,
            clip_order=selected_clips,
            hooks=[f"{int(target_duration)}s punchy version", "Quick hit", "Fast takeaway"],
            total_duration=target_duration,
            strategy_notes=f"Optimized for {int(target_duration)}s attention span"
        )
        variants.append(variant)
    
    return variants


def suggest_variants_by_goal(
    base_clip_ids: List[str],
    goal: str,  # "engagement", "conversion", "awareness"
    request_id: str
) -> List[VariantClip]:
    """
    Generate variants optimized for specific goals.
    """
    if goal == "engagement":
        return generate_reorder_variants(base_clip_ids, request_id, count=3)
    elif goal == "conversion":
        return generate_hook_variants(base_clip_ids, [], request_id, count=3)
    elif goal == "awareness":
        return generate_length_variants(base_clip_ids, request_id, [15.0, 30.0])
    else:
        return generate_reorder_variants(base_clip_ids, request_id, count=2)


def generate_strategy_pack(
    base_clip_ids: List[str],
    request_id: str,
    user_goal: str = "engagement"
) -> Dict:
    """
    Generate complete strategy pack with multiple variant types.
    Returns structured pack for frontend display.
    """
    # Generate different variant types
    reorder_variants = generate_reorder_variants(base_clip_ids, request_id, count=2)
    hook_variants = generate_hook_variants(base_clip_ids, [], request_id, count=2)
    length_variants = generate_length_variants(base_clip_ids, request_id)
    
    # Goal-optimized variants
    goal_variants = suggest_variants_by_goal(base_clip_ids, user_goal, request_id)
    
    return {
        "request_id": request_id,
        "total_clips": len(base_clip_ids),
        "variants": {
            "reorder": [v.dict() for v in reorder_variants],
            "hooks": [v.dict() for v in hook_variants],
            "lengths": [v.dict() for v in length_variants],
            "goal_optimized": [v.dict() for v in goal_variants]
        },
        "recommendation": {
            "post_first": reorder_variants[0].variant_id if reorder_variants else None,
            "test_a_b": [reorder_variants[0].variant_id, hook_variants[0].variant_id] if reorder_variants and hook_variants else [],
            "best_for_platforms": {
                "tiktok": length_variants[0].variant_id if length_variants else None,
                "youtube": length_variants[-1].variant_id if length_variants else None
            }
        }
    }
