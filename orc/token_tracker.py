"""
Token Tracking and Cost Estimation for ORC
Tracks token usage and estimates costs across different AI providers
"""

from typing import Dict, Optional, List
from datetime import datetime


# Pricing per 1M tokens (as of 2026-01)
PRICING = {
    # Groq (free tier - no cost)
    "groq": {
        "llama-3.1-70b-versatile": {"input": 0.0, "output": 0.0},
        "llama-3.1-8b-instant": {"input": 0.0, "output": 0.0},
        "mixtral-8x7b-32768": {"input": 0.0, "output": 0.0},
    },
    
    # OpenAI
    "openai": {
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        "gpt-4o": {"input": 5.0, "output": 15.0},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    },
    
    # Anthropic
    "anthropic": {
        "claude-3-opus": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet": {"input": 3.0, "output": 15.0},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        "claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
    },
    
    # DeepSeek
    "deepseek": {
        "deepseek-chat": {"input": 0.14, "output": 0.28},
        "deepseek-coder": {"input": 0.14, "output": 0.28},
    },
    
    # Google Gemini
    "google": {
        "gemini-pro": {"input": 0.125, "output": 0.375},
        "gemini-1.5-pro": {"input": 1.25, "output": 5.0},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    },
    
    # Ollama (local - no cost)
    "ollama": {
        "default": {"input": 0.0, "output": 0.0}
    }
}

# Context window sizes (in tokens)
CONTEXT_WINDOWS = {
    "groq/llama-3.1-70b-versatile": 131072,
    "groq/llama-3.1-8b-instant": 131072,
    "groq/mixtral-8x7b-32768": 32768,
    "openai/gpt-4": 8192,
    "openai/gpt-4-turbo": 128000,
    "openai/gpt-3.5-turbo": 16385,
    "openai/gpt-4o": 128000,
    "openai/gpt-4o-mini": 128000,
    "anthropic/claude-3-opus": 200000,
    "anthropic/claude-3-sonnet": 200000,
    "anthropic/claude-3-haiku": 200000,
    "anthropic/claude-3.5-sonnet": 200000,
    "deepseek/deepseek-chat": 64000,
    "deepseek/deepseek-coder": 64000,
    "google/gemini-pro": 32768,
    "google/gemini-1.5-pro": 1048576,
    "google/gemini-1.5-flash": 1048576,
    "ollama": 8192,  # Default for local models
}


class TokenTracker:
    """Track token usage and estimate costs"""
    
    def __init__(self):
        """Initialize token tracker"""
        self.session_start = datetime.now()
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.request_history: List[Dict] = []
    
    def add_request(self, provider: str, model: str, 
                   input_tokens: int, output_tokens: int):
        """
        Add a request to tracking
        
        Args:
            provider: AI provider name (groq, openai, etc.)
            model: Model name
            input_tokens: Input tokens used
            output_tokens: Output tokens generated
        """
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        
        # Calculate cost
        cost = self._calculate_cost(provider, model, input_tokens, output_tokens)
        self.total_cost += cost
        
        # Add to history
        self.request_history.append({
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        })
    
    def _calculate_cost(self, provider: str, model: str, 
                       input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a request"""
        try:
            # Get pricing for provider/model
            provider_pricing = PRICING.get(provider.lower(), {})
            model_pricing = None
            
            # Try exact model match
            for model_key, pricing in provider_pricing.items():
                if model_key in model.lower():
                    model_pricing = pricing
                    break
            
            if not model_pricing:
                # Use default pricing if available
                model_pricing = provider_pricing.get("default", {"input": 0.0, "output": 0.0})
            
            # Calculate cost (pricing is per 1M tokens)
            input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
            output_cost = (output_tokens / 1_000_000) * model_pricing["output"]
            
            return input_cost + output_cost
            
        except Exception:
            return 0.0
    
    def get_stats(self) -> Dict:
        """Get current session statistics"""
        session_duration = (datetime.now() - self.session_start).total_seconds()
        
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": self.total_cost,
            "request_count": len(self.request_history),
            "session_duration": session_duration,
            "avg_tokens_per_request": (
                (self.total_input_tokens + self.total_output_tokens) / len(self.request_history)
                if self.request_history else 0
            )
        }
    
    def estimate_context_usage(self, conversation_history: List[Dict], 
                              model: str) -> Dict:
        """
        Estimate context window usage
        
        Args:
            conversation_history: List of message dicts
            model: Current model (format: "provider/model")
        
        Returns:
            Dict with tokens_used, tokens_total, percentage
        """
        # Rough estimation: ~4 chars per token
        estimated_tokens = sum(
            len(msg.get("content", "")) // 4 
            for msg in conversation_history
        )
        
        # Get context window size
        context_total = CONTEXT_WINDOWS.get(model, 8192)
        
        # Add buffer for system prompt and tool definitions (~2000 tokens)
        estimated_tokens += 2000
        
        return {
            "tokens_used": estimated_tokens,
            "tokens_total": context_total,
            "percentage": (estimated_tokens / context_total * 100) if context_total > 0 else 0,
            "remaining": max(0, context_total - estimated_tokens)
        }
    
    def reset(self):
        """Reset tracker for new session"""
        self.session_start = datetime.now()
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.request_history = []
    
    def export_stats(self) -> Dict:
        """Export full statistics including history"""
        return {
            "session_stats": self.get_stats(),
            "request_history": self.request_history
        }
