from typing import Dict, List, Optional
from datetime import datetime, timezone
import json


class AntiRepetitionMemory:
    """
    Memory shape for tracking and preventing content repetition.
    """
    
    def __init__(self, memory_file: Optional[str] = None):
        self.memory_file = memory_file
        self.session_hooks: List[str] = []
        self.session_topics: List[str] = []
        self.session_angles: List[str] = []
        self.clip_history: List[Dict] = []
        self.last_cleanup = self._utcnow()
    
    def _utcnow(self) -> str:
        return datetime.now(timezone.utc).isoformat()
    
    def record_generation(
        self,
        hooks: List[str],
        topics: List[str],
        angles: List[str],
        clip_ids: List[str],
    ):
        """Record a generation session for repetition tracking."""
        self.session_hooks.extend([h.lower() for h in hooks])
        self.session_topics.extend([t.lower() for t in topics])
        self.session_angles.extend([a.lower() for a in angles])
        
        for clip_id in clip_ids:
            self.clip_history.append({
                "clip_id": clip_id,
                "timestamp": self._utcnow(),
            })
    
    def get_hook_frequency(self, hook: str) -> int:
        """Get how many times a hook (or similar) was used."""
        hook_lower = hook.lower()
        return sum(1 for h in self.session_hooks if hook_lower in h or h in hook_lower)
    
    def get_topic_frequency(self, topic: str) -> int:
        """Get how many times a topic was used."""
        topic_lower = topic.lower()
        return sum(1 for t in self.session_topics if topic_lower in t)
    
    def get_angle_usage(self, angle: str) -> int:
        """Get how many times an angle was used."""
        return self.session_angles.count(angle.lower())
    
    def should_regenerate(self, hook: str, topic: str, angle: str) -> Dict[str, bool]:
        """
        Determine if regeneration is needed due to repetition.
        """
        hook_freq = self.get_hook_frequency(hook)
        topic_freq = self.get_topic_frequency(topic)
        angle_freq = self.get_angle_usage(angle)
        
        return {
            "hook_overused": hook_freq >= 3,
            "topic_overused": topic_freq >= 5,
            "angle_overused": angle_freq >= 4,
        }
    
    def get_diversity_score(self) -> float:
        """
        Calculate a diversity score for the current session (0-100).
        """
        if not self.session_hooks:
            return 100.0
        
        unique_hooks = len(set(self.session_hooks))
        unique_topics = len(set(self.session_topics))
        unique_angles = len(set(self.session_angles))
        
        total = len(self.session_hooks) + len(self.session_topics) + len(self.session_angles)
        unique = unique_hooks + unique_topics + unique_angles
        
        if total == 0:
            return 100.0
        
        return round((unique / total) * 100, 1)
    
    def get_memory_summary(self) -> Dict:
        """Get a summary of the current memory state."""
        return {
            "total_hooks": len(self.session_hooks),
            "unique_hooks": len(set(self.session_hooks)),
            "total_topics": len(self.session_topics),
            "unique_topics": len(set(self.session_topics)),
            "total_angles": len(self.session_angles),
            "unique_angles": len(set(self.session_angles)),
            "clips_generated": len(self.clip_history),
            "diversity_score": self.get_diversity_score(),
            "last_cleanup": self.last_cleanup,
        }
    
    def cleanup_old_entries(self, max_entries: int = 1000):
        """Trim history to prevent unbounded growth."""
        if len(self.session_hooks) > max_entries:
            self.session_hooks = self.session_hooks[-max_entries:]
            self.session_topics = self.session_topics[-max_entries:]
            self.session_angles = self.session_angles[-max_entries:]
            self.clip_history = self.clip_history[-max_entries:]
            self.last_cleanup = self._utcnow()
    
    def to_dict(self) -> Dict:
        """Serialize memory to dict."""
        return {
            "session_hooks": self.session_hooks,
            "session_topics": self.session_topics,
            "session_angles": self.session_angles,
            "clip_history": self.clip_history,
            "last_cleanup": self.last_cleanup,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AntiRepetitionMemory":
        """Deserialize memory from dict."""
        memory = cls()
        memory.session_hooks = data.get("session_hooks", [])
        memory.session_topics = data.get("session_topics", [])
        memory.session_angles = data.get("session_angles", [])
        memory.clip_history = data.get("clip_history", [])
        memory.last_cleanup = data.get("last_cleanup", memory._utcnow())
        return memory


# Global instance
_anti_repetition_memory = AntiRepetitionMemory()


def get_anti_repetition_memory() -> AntiRepetitionMemory:
    """Get the global anti-repetition memory instance."""
    return _anti_repetition_memory