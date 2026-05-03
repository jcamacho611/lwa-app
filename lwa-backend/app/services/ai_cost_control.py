from __future__ import annotations

import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from ..core.config import Settings


# Model cost per 1K tokens (USD)
MODEL_COSTS_PER_1K_TOKENS = {
    "claude-opus-4-7": 0.015,  # $15 per 1M tokens
    "claude-sonnet-4-6": 0.003,  # $3 per 1M tokens
    "claude-haiku-4-5-20251001": 0.00025,  # $0.25 per 1M tokens
    "gpt-4.1-mini": 0.00015,  # $0.15 per 1M tokens
    "seedance-2.0": 0.002,  # $2 per 1M tokens
}


class AICostControl:
    """Enhanced AI cost control system with rate limiting and budget enforcement."""
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.usage_store_path = settings.usage_store_path
        self._load_usage_data()
    
    def _load_usage_data(self) -> None:
        """Load usage data from storage."""
        try:
            with open(self.usage_store_path, 'r') as f:
                self.usage_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.usage_data = {}
    
    def _save_usage_data(self) -> None:
        """Save usage data to storage."""
        try:
            with open(self.usage_store_path, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception:
            pass  # Fail silently to avoid breaking AI operations
    
    def check_rate_limit(self, user_id: str, operation: str = "ai_request") -> bool:
        """Check if user is within rate limits."""
        if not self.settings.ai_cost_control_enabled:
            return True
            
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"{operation}:{user_id}"
        
        daily_usage = self.usage_data.get(today, {}).get(key, 0)
        
        if user_id.startswith("guest:"):
            daily_limit = self.settings.ai_daily_requests_guest
        else:
            daily_limit = self.settings.ai_daily_requests_user
        
        return daily_usage < daily_limit
    
    def check_budget_limit(self, user_id: str, estimated_cost: float) -> bool:
        """Check if user is within budget limits."""
        if not self.settings.ai_cost_control_enabled:
            return True
            
        today = datetime.now().strftime("%Y-%m-%d")
        daily_cost_key = f"cost:{user_id}"
        
        current_daily_cost = self.usage_data.get(today, {}).get(daily_cost_key, 0.0)
        
        if user_id.startswith("guest:"):
            daily_budget = self.settings.ai_daily_budget_guest
        else:
            daily_budget = self.settings.ai_daily_budget_user
        
        return (current_daily_cost + estimated_cost) <= daily_budget
    
    def record_usage(self, user_id: str, operation: str, model: str, tokens_used: int) -> None:
        """Record AI usage for cost tracking."""
        today = datetime.now().strftime("%Y-%m-%d")
        cost_per_1k = MODEL_COSTS_PER_1K_TOKENS.get(model, 0.001)
        cost = (tokens_used / 1000) * cost_per_1k
        
        if today not in self.usage_data:
            self.usage_data[today] = {}
        
        # Record operation count
        op_key = f"{operation}:{user_id}"
        self.usage_data[today][op_key] = self.usage_data[today].get(op_key, 0) + 1
        
        # Record cost
        cost_key = f"cost:{user_id}"
        self.usage_data[today][cost_key] = self.usage_data[today].get(cost_key, 0.0) + cost
        
        # Record model usage
        model_key = f"model:{model}:{user_id}"
        self.usage_data[today][model_key] = self.usage_data[today].get(model_key, 0) + tokens_used
        
        self._save_usage_data()
    
    def get_user_cost_summary(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get cost summary for a user over the last N days."""
        summary = {
            "total_cost": 0.0,
            "total_requests": 0,
            "model_breakdown": {},
            "daily_costs": {},
        }
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if date in self.usage_data:
                daily_data = self.usage_data[date]
                
                # Daily cost
                cost_key = f"cost:{user_id}"
                daily_cost = daily_data.get(cost_key, 0.0)
                summary["daily_costs"][date] = daily_cost
                summary["total_cost"] += daily_cost
                
                # Daily requests
                for key, value in daily_data.items():
                    if key.startswith(("clip_packaging:", "classify_metadata:")) and key.endswith(f":{user_id}"):
                        summary["total_requests"] += value
                    
                    # Model breakdown
                    if key.startswith(f"model:") and key.endswith(f":{user_id}"):
                        model = key.split(":")[1]
                        tokens = value
                        cost_per_1k = MODEL_COSTS_PER_1K_TOKENS.get(model, 0.001)
                        cost = (tokens / 1000) * cost_per_1k
                        if model not in summary["model_breakdown"]:
                            summary["model_breakdown"][model] = {"tokens": 0, "cost": 0.0}
                        summary["model_breakdown"][model]["tokens"] += tokens
                        summary["model_breakdown"][model]["cost"] += cost
        
        return summary
    
    def get_system_cost_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get system-wide cost summary over the last N days."""
        summary = {
            "total_cost": 0.0,
            "total_requests": 0,
            "model_breakdown": {},
            "daily_costs": {},
            "top_users": [],
        }
        
        user_costs = {}
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if date in self.usage_data:
                daily_data = self.usage_data[date]
                daily_cost = 0.0
                
                for key, value in daily_data.items():
                    if key.startswith("cost:"):
                        user_id = key.split(":", 1)[1]
                        cost = value
                        daily_cost += cost
                        
                        if user_id not in user_costs:
                            user_costs[user_id] = 0.0
                        user_costs[user_id] += cost
                    
                    elif key.startswith(("clip_packaging:", "classify_metadata:")):
                        summary["total_requests"] += value
                    
                    elif key.startswith("model:"):
                        model = key.split(":")[1]
                        tokens = value
                        cost_per_1k = MODEL_COSTS_PER_1K_TOKENS.get(model, 0.001)
                        cost = (tokens / 1000) * cost_per_1k
                        
                        if model not in summary["model_breakdown"]:
                            summary["model_breakdown"][model] = {"tokens": 0, "cost": 0.0}
                        summary["model_breakdown"][model]["tokens"] += tokens
                        summary["model_breakdown"][model]["cost"] += cost
                
                summary["daily_costs"][date] = daily_cost
                summary["total_cost"] += daily_cost
        
        # Top users
        summary["top_users"] = sorted(user_costs.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return summary
    
    def estimate_request_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for an AI request."""
        cost_per_1k = MODEL_COSTS_PER_1K_TOKENS.get(model, 0.001)
        total_tokens = input_tokens + output_tokens
        return (total_tokens / 1000) * cost_per_1k
    
    @property
    def rate_limit_guest_rpm(self) -> int:
        """Get rate limit for guest users."""
        return self.settings.rate_limit_guest_rpm


# Global cost control instance
_cost_control_instance: Optional[AICostControl] = None


def get_cost_control(settings: Settings) -> AICostControl:
    """Get or create the AI cost control instance."""
    global _cost_control_instance
    if _cost_control_instance is None:
        _cost_control_instance = AICostControl(settings)
    return _cost_control_instance


def check_ai_limits(settings: Settings, user_id: str, model: str, estimated_tokens: int = 1000) -> bool:
    """Check if AI request is within limits."""
    cost_control = get_cost_control(settings)
    
    # Check rate limit
    if not cost_control.check_rate_limit(user_id):
        return False
    
    # Estimate cost and check budget
    estimated_cost = cost_control.estimate_request_cost(model, estimated_tokens, estimated_tokens)
    if not cost_control.check_budget_limit(user_id, estimated_cost):
        return False
    
    return True


def record_ai_usage(settings: Settings, user_id: str, operation: str, model: str, tokens_used: int) -> None:
    """Record AI usage for cost tracking."""
    cost_control = get_cost_control(settings)
    cost_control.record_usage(user_id, operation, model, tokens_used)
