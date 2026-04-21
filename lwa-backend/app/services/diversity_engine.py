from typing import List, Dict, Set, Optional
from collections import defaultdict


class DiversityEngine:
    """
    Engine to ensure content diversity and prevent repetition.
    """
    
    def __init__(self):
        self.seen_hooks: Set[str] = set()
        self.seen_topics: Set[str] = set()
        self.seen_angles: Set[str] = set()
        self.topic_history: Dict[str, int] = defaultdict(int)
    
    def reset(self):
        """Reset the diversity tracking."""
        self.seen_hooks.clear()
        self.seen_topics.clear()
        self.seen_topics.clear()
        self.topic_history.clear()
    
    def is_duplicate_hook(self, hook: str, threshold: float = 0.8) -> bool:
        """
        Check if a hook is too similar to previously seen hooks.
        """
        hook_normalized = hook.lower().strip()
        
        # Exact match
        if hook_normalized in self.seen_hooks:
            return True
        
        # Word overlap check
        hook_words = set(hook_normalized.split())
        for seen in self.seen_hooks:
            seen_words = set(seen.split())
            overlap = len(hook_words & seen_words) / max(len(hook_words), len(seen_words))
            if overlap >= threshold:
                return True
        
        return False
    
    def record_hook(self, hook: str):
        """Record a hook to prevent future duplicates."""
        self.seen_hooks.add(hook.lower().strip())
    
    def record_topic(self, topic: str):
        """Record a topic usage."""
        topic_normalized = topic.lower().strip()
        self.seen_topics.add(topic_normalized)
        self.topic_history[topic_normalized] += 1
    
    def get_topic_frequency(self, topic: str) -> int:
        """Get how many times a topic has been used."""
        return self.topic_history.get(topic.lower().strip(), 0)
    
    def suggest_diverse_angle(self, base_topic: str, used_angles: List[str]) -> str:
        """
        Suggest an angle that hasn't been used recently.
        """
        all_angles = ["curiosity", "controversy", "story", "authority", "how", "why"]
        available = [a for a in all_angles if a not in used_angles]
        
        if available:
            return available[0]
        return "curiosity"  # Default fallback
    
    def enforce_diversity(self, hooks: List[str], min_new_ratio: float = 0.5) -> List[str]:
        """
        Filter hooks to ensure diversity ratio.
        """
        diverse = []
        new_count = 0
        
        for hook in hooks:
            if not self.is_duplicate_hook(hook):
                diverse.append(hook)
                self.record_hook(hook)
                new_count += 1
                
                if new_count / len(diverse) < min_new_ratio:
                    break
        
        return diverse


# Global instance for reuse
_diversity_engine = DiversityEngine()


def get_diversity_engine() -> DiversityEngine:
    """Get the global diversity engine instance."""
    return _diversity_engine