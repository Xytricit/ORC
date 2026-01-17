"""
ORC Token Tracker Module

Track token usage and estimate costs across different AI providers.

Author: ORC Team
Date: 2026-01-14
"""

from datetime import datetime
from typing import Dict, List, Optional


class TokenTracker:
    """Track token usage and estimate costs."""
    
    # Pricing per 1M tokens (as of January 2026)
    PRICING = {
        'groq': {
            'input': 0.0,
            'output': 0.0,
            'rate_limited': True
        },
        'openai-gpt4': {
            'input': 30.0,
            'output': 60.0
        },
        'openai-gpt4-turbo': {
            'input': 10.0,
            'output': 30.0
        },
        'openai-gpt35': {
            'input': 0.50,
            'output': 1.50
        },
        'anthropic-opus': {
            'input': 15.0,
            'output': 75.0
        },
        'anthropic-sonnet': {
            'input': 3.0,
            'output': 15.0
        },
        'anthropic-haiku': {
            'input': 0.25,
            'output': 1.25
        },
        'ollama': {
            'input': 0.0,
            'output': 0.0,
            'local': True
        },
        'deepseek': {
            'input': 0.14,
            'output': 0.28
        },
        'gemini': {
            'input': 0.0,
            'output': 0.0,
            'free_tier': True
        },
        'gemini-pro': {
            'input': 0.50,
            'output': 1.50
        }
    }
    
    def __init__(self):
        """Initialize token tracker."""
        self.requests: List[Dict] = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
    def add_request(
        self, 
        provider: str, 
        model: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> Dict:
        """
        Add a request to tracking.
        
        Args:
            provider: Provider name (groq, openai, etc.)
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            dict: Request record with cost estimate
        """
        cost = self.estimate_cost(provider, model, input_tokens, output_tokens)
        
        request = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'cost': cost
        }
        
        self.requests.append(request)
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost
        
        return request
    
    def estimate_cost(
        self, 
        provider: str, 
        model: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> float:
        """
        Estimate cost for token usage.
        
        Args:
            provider: Provider name
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            float: Estimated cost in USD
        """
        # Normalize provider-model key
        key = f"{provider}-{model}".lower() if model else provider.lower()
        
        # Try exact match first
        pricing = self.PRICING.get(key)
        
        # Fall back to provider only
        if not pricing:
            pricing = self.PRICING.get(provider.lower())
        
        # Default to free if unknown
        if not pricing:
            return 0.0
        
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']
        
        return input_cost + output_cost
    
    def get_statistics(self) -> Dict:
        """
        Get comprehensive statistics.
        
        Returns:
            dict: Statistics including totals and per-provider breakdown
        """
        stats = {
            'total_requests': len(self.requests),
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'total_cost': self.total_cost,
            'by_provider': {},
            'by_model': {}
        }
        
        # Aggregate by provider
        for request in self.requests:
            provider = request['provider']
            if provider not in stats['by_provider']:
                stats['by_provider'][provider] = {
                    'requests': 0,
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'total_tokens': 0,
                    'cost': 0.0
                }
            
            stats['by_provider'][provider]['requests'] += 1
            stats['by_provider'][provider]['input_tokens'] += request['input_tokens']
            stats['by_provider'][provider]['output_tokens'] += request['output_tokens']
            stats['by_provider'][provider]['total_tokens'] += request['total_tokens']
            stats['by_provider'][provider]['cost'] += request['cost']
        
        # Aggregate by model
        for request in self.requests:
            model = request['model']
            if model not in stats['by_model']:
                stats['by_model'][model] = {
                    'requests': 0,
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'total_tokens': 0,
                    'cost': 0.0
                }
            
            stats['by_model'][model]['requests'] += 1
            stats['by_model'][model]['input_tokens'] += request['input_tokens']
            stats['by_model'][model]['output_tokens'] += request['output_tokens']
            stats['by_model'][model]['total_tokens'] += request['total_tokens']
            stats['by_model'][model]['cost'] += request['cost']
        
        return stats
    
    def get_provider_stats(self, provider: str) -> Optional[Dict]:
        """
        Get statistics for specific provider.
        
        Args:
            provider: Provider name
        
        Returns:
            dict: Provider statistics or None if no requests
        """
        stats = self.get_statistics()
        return stats['by_provider'].get(provider)
    
    def get_recent_requests(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent requests.
        
        Args:
            limit: Number of recent requests to return
        
        Returns:
            list: Recent request records
        """
        return self.requests[-limit:]
    
    def reset(self) -> None:
        """Reset all tracking data."""
        self.requests = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
    def format_stats(self) -> str:
        """
        Format statistics as readable string.
        
        Returns:
            str: Formatted statistics
        """
        stats = self.get_statistics()
        
        lines = [
            "Token Usage Statistics",
            "=" * 50,
            f"Total Requests: {stats['total_requests']}",
            f"Total Tokens: {stats['total_tokens']:,}",
            f"  Input: {stats['total_input_tokens']:,}",
            f"  Output: {stats['total_output_tokens']:,}",
            f"Estimated Cost: ${stats['total_cost']:.4f}",
            "",
            "By Provider:",
            "-" * 50
        ]
        
        for provider, data in stats['by_provider'].items():
            lines.append(f"  {provider}:")
            lines.append(f"    Requests: {data['requests']}")
            lines.append(f"    Tokens: {data['total_tokens']:,}")
            lines.append(f"    Cost: ${data['cost']:.4f}")
        
        return "\n".join(lines)
    
    def get_average_tokens_per_request(self) -> float:
        """
        Get average tokens per request.
        
        Returns:
            float: Average tokens
        """
        if not self.requests:
            return 0.0
        
        total_tokens = self.total_input_tokens + self.total_output_tokens
        return total_tokens / len(self.requests)
    
    def get_cost_per_request(self) -> float:
        """
        Get average cost per request.
        
        Returns:
            float: Average cost
        """
        if not self.requests:
            return 0.0
        
        return self.total_cost / len(self.requests)
