"""
ORC AI Client

Multi-provider AI client with support for:
- Groq (free, rate-limited)
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude Opus, Sonnet, Haiku)
- Ollama (local models)
- DeepSeek
- Gemini

Author: ORC Team
Date: 2026-01-14
"""

import os
import json
from typing import Dict, List, Optional, Iterator, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available - AI features will not work")


@dataclass
class AIMessage:
    """Represents an AI message."""
    role: str  # 'system', 'user', 'assistant'
    content: str


@dataclass
class AIResponse:
    """Represents an AI response."""
    content: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None


class AIClient:
    """
    Multi-provider AI client.
    
    Supports multiple AI providers with consistent interface.
    """
    
    # Provider endpoints
    ENDPOINTS = {
        'groq': 'https://api.groq.com/openai/v1/chat/completions',
        'openai': 'https://api.openai.com/v1/chat/completions',
        'anthropic': 'https://api.anthropic.com/v1/messages',
        'deepseek': 'https://api.deepseek.com/v1/chat/completions',
        'ollama': 'http://localhost:11434/api/chat',
    }
    
    # Default models per provider
    DEFAULT_MODELS = {
        'groq': 'llama-3.1-70b-versatile',
        'openai': 'gpt-4-turbo-preview',
        'anthropic': 'claude-3-sonnet-20240229',
        'deepseek': 'deepseek-chat',
        'ollama': 'llama2',
    }
    
    def __init__(
        self,
        provider: str = 'groq',
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """
        Initialize AI client.
        
        Args:
            provider: AI provider name
            model: Model name (None = use default)
            api_key: API key (None = load from env)
            temperature: Response randomness (0-1)
            max_tokens: Maximum response tokens
        """
        self.provider = provider.lower()
        self.model = model or self.DEFAULT_MODELS.get(self.provider)
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Load API key
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = self._load_api_key()
        
        # Validate
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for AI features: pip install requests")
        
        if self.provider not in self.ENDPOINTS:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _load_api_key(self) -> Optional[str]:
        """
        Load API key from environment variables.
        
        Returns:
            str: API key or None
        """
        env_vars = {
            'groq': 'GROQ_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'deepseek': 'DEEPSEEK_API_KEY',
        }
        
        env_var = env_vars.get(self.provider)
        if env_var:
            return os.getenv(env_var)
        
        return None
    
    def chat(
        self,
        messages: List[AIMessage],
        stream: bool = False,
        tools: Optional[List[Dict]] = None
    ) -> AIResponse:
        """
        Send chat completion request.
        
        Args:
            messages: List of AIMessage objects
            stream: Stream response (not implemented yet)
            tools: Tool definitions for function calling
        
        Returns:
            AIResponse object
        """
        if stream:
            raise NotImplementedError("Streaming not yet implemented")
        
        # Route to provider-specific method
        if self.provider in ['groq', 'openai', 'deepseek']:
            return self._openai_compatible_chat(messages, tools)
        elif self.provider == 'anthropic':
            return self._anthropic_chat(messages, tools)
        elif self.provider == 'ollama':
            return self._ollama_chat(messages, tools)
        else:
            raise ValueError(f"Provider {self.provider} not supported")
    
    def _openai_compatible_chat(
        self,
        messages: List[AIMessage],
        tools: Optional[List[Dict]] = None
    ) -> AIResponse:
        """
        OpenAI-compatible API call (Groq, OpenAI, DeepSeek).
        
        Args:
            messages: Conversation messages
            tools: Tool definitions
        
        Returns:
            AIResponse
        """
        # Build request
        payload = {
            'model': self.model,
            'messages': [{'role': msg.role, 'content': msg.content} for msg in messages],
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
        }
        
        if tools:
            payload['tools'] = tools
            payload['tool_choice'] = 'auto'
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        # Make request
        try:
            response = requests.post(
                self.ENDPOINTS[self.provider],
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            # Parse response
            choice = data['choices'][0]
            message = choice['message']
            
            return AIResponse(
                content=message.get('content', ''),
                provider=self.provider,
                model=self.model,
                input_tokens=data.get('usage', {}).get('prompt_tokens', 0),
                output_tokens=data.get('usage', {}).get('completion_tokens', 0),
                finish_reason=choice.get('finish_reason'),
                tool_calls=message.get('tool_calls')
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"AI request failed: {e}")
            
            # Fallback to mock response
            return AIResponse(
                content=f"Error: Could not reach {self.provider}. {str(e)}",
                provider=self.provider,
                model=self.model
            )
    
    def _anthropic_chat(
        self,
        messages: List[AIMessage],
        tools: Optional[List[Dict]] = None
    ) -> AIResponse:
        """
        Anthropic API call.
        
        Args:
            messages: Conversation messages
            tools: Tool definitions
        
        Returns:
            AIResponse
        """
        # Anthropic uses different format
        system_msg = next((m.content for m in messages if m.role == 'system'), '')
        conversation = [
            {'role': msg.role, 'content': msg.content}
            for msg in messages
            if msg.role != 'system'
        ]
        
        payload = {
            'model': self.model,
            'messages': conversation,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
        }
        
        if system_msg:
            payload['system'] = system_msg
        
        if tools:
            payload['tools'] = tools
        
        headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json',
        }
        
        try:
            response = requests.post(
                self.ENDPOINTS['anthropic'],
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            return AIResponse(
                content=data['content'][0]['text'],
                provider='anthropic',
                model=self.model,
                input_tokens=data.get('usage', {}).get('input_tokens', 0),
                output_tokens=data.get('usage', {}).get('output_tokens', 0),
                finish_reason=data.get('stop_reason')
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Anthropic request failed: {e}")
            
            return AIResponse(
                content=f"Error: Could not reach Anthropic. {str(e)}",
                provider='anthropic',
                model=self.model
            )
    
    def _ollama_chat(
        self,
        messages: List[AIMessage],
        tools: Optional[List[Dict]] = None
    ) -> AIResponse:
        """
        Ollama (local) API call.
        
        Args:
            messages: Conversation messages
            tools: Tool definitions
        
        Returns:
            AIResponse
        """
        payload = {
            'model': self.model,
            'messages': [{'role': msg.role, 'content': msg.content} for msg in messages],
            'stream': False,
        }
        
        try:
            response = requests.post(
                self.ENDPOINTS['ollama'],
                json=payload,
                timeout=120  # Local can be slow
            )
            response.raise_for_status()
            data = response.json()
            
            return AIResponse(
                content=data['message']['content'],
                provider='ollama',
                model=self.model,
                finish_reason=data.get('done_reason')
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            
            return AIResponse(
                content=f"Error: Could not reach Ollama (is it running?). {str(e)}",
                provider='ollama',
                model=self.model
            )


# Convenience function
def create_client(provider: str = 'groq', **kwargs) -> AIClient:
    """
    Create AI client with sensible defaults.
    
    Args:
        provider: Provider name
        **kwargs: Additional arguments for AIClient
    
    Returns:
        AIClient instance
    """
    return AIClient(provider=provider, **kwargs)
