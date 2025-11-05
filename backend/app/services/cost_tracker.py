"""Cost tracking service for LLM API calls"""
from typing import Dict
from datetime import datetime
from uuid import UUID


class CostTracker:
    """Track and calculate costs for LLM API usage"""
    
    # Anthropic Claude pricing (per 1M tokens)
    PRICING = {
        "claude-3-opus-20240229": {
            "input": 15.00,   # $15 per 1M input tokens
            "output": 75.00    # $75 per 1M output tokens
        },
        "claude-3-sonnet-20240229": {
            "input": 3.00,
            "output": 15.00
        },
        "claude-3-haiku-20240307": {
            "input": 0.25,
            "output": 1.25
        }
    }
    
    def __init__(self):
        self.usage_cache = {}
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD for a single API call"""
        pricing = self.PRICING.get(model, self.PRICING["claude-3-haiku-20240307"])
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return round(input_cost + output_cost, 6)
    
    async def track_usage(
        self, 
        site_id: UUID, 
        job_id: UUID, 
        model: str, 
        input_tokens: int, 
        output_tokens: int,
        operation: str
    ) -> Dict:
        """Track usage and return cost info"""
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        
        usage_record = {
            "site_id": str(site_id),
            "job_id": str(job_id),
            "model": model,
            "operation": operation,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store in cache (in production, write to DB)
        cache_key = f"{site_id}:{job_id}"
        if cache_key not in self.usage_cache:
            self.usage_cache[cache_key] = []
        self.usage_cache[cache_key].append(usage_record)
        
        return usage_record
    
    async def get_site_costs(self, site_id: UUID) -> Dict:
        """Get total costs for a site"""
        total_cost = 0.0
        total_tokens = 0
        calls = 0
        
        for key, records in self.usage_cache.items():
            if str(site_id) in key:
                for record in records:
                    total_cost += record["cost_usd"]
                    total_tokens += record["input_tokens"] + record["output_tokens"]
                    calls += 1
        
        return {
            "site_id": str(site_id),
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "api_calls": calls,
            "average_cost_per_call": round(total_cost / calls, 4) if calls > 0 else 0
        }
    
    async def check_budget(self, site_id: UUID, budget_limit: float) -> Dict:
        """Check if site has exceeded budget"""
        costs = await self.get_site_costs(site_id)
        exceeded = costs["total_cost_usd"] > budget_limit
        
        return {
            "site_id": str(site_id),
            "current_cost": costs["total_cost_usd"],
            "budget_limit": budget_limit,
            "exceeded": exceeded,
            "remaining": max(0, budget_limit - costs["total_cost_usd"]),
            "percentage_used": round((costs["total_cost_usd"] / budget_limit) * 100, 2) if budget_limit > 0 else 0
        }


cost_tracker = CostTracker()

