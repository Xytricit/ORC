"""
Custom AI Provider for user-defined models and APIs
"""

import json
import httpx
from typing import Optional, List, Dict, Any
from .ai_client import AIProvider, AIResponse
from .config import get_config, CustomProvider


class CustomAIProvider(AIProvider):
    """User-defined AI provider"""
    
    def __init__(self, config: CustomProvider):
        self.config = config
        self.name = config.name
        self.model = config.model
        self._available = None
    
    def is_available(self) -> bool:
        """Check if provider is configured and available"""
        if self._available is not None:
            return self._available
        
        if not self.config.api_key or not self.config.base_url:
            self._available = False
            return False
        
        try:
            # Test connection with a simple request
            headers = self._get_auth_headers()
            response = httpx.get(
                f"{self.config.base_url.rstrip('/')}/models" if self.config.supports_tools else f"{self.config.base_url.rstrip('/')}/",
                headers=headers,
                timeout=5.0
            )
            self._available = response.status_code in [200, 404, 405]  # 404/405 might mean endpoint exists but different path
        except Exception:
            self._available = False
        
        return self._available
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        headers = {}
        
        if self.config.auth_type == "bearer":
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        elif self.config.auth_type == "api_key":
            headers["X-API-Key"] = self.config.api_key
        elif self.config.auth_type == "custom":
            # For custom auth, use the headers from config
            headers.update(self.config.headers)
            # Replace API key placeholder if present
            for key, value in headers.items():
                if "{API_KEY}" in value:
                    headers[key] = value.replace("{API_KEY}", self.config.api_key)
        
        # Add any additional headers
        headers.update(self.config.headers)
        
        # Remove auth headers that were already handled
        if self.config.auth_type in ["bearer", "api_key"] and "Authorization" in self.config.headers:
            del self.config.headers["Authorization"]
        if self.config.auth_type == "api_key" and "X-API-Key" in self.config.headers:
            del self.config.headers["X-API-Key"]
        
        headers.update(self.config.headers)
        
        # Set content type
        headers["Content-Type"] = "application/json"
        
        return headers
    
    def chat(self, messages: List[Dict], tools: Optional[List[Dict]],
             temperature: float, max_tokens: int) -> AIResponse:
        """Send chat request to custom provider"""
        
        headers = self._get_auth_headers()
        
        # Build payload based on common API patterns
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
        }
        
        # Add tools if supported
        if tools and self.config.supports_tools:
            payload["tools"] = tools
        
        try:
            response = httpx.post(
                f"{self.config.base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                return AIResponse(
                    content=f"API Error: {response.status_code} - {response.text}",
                    finish_reason="error"
                )
            
            data = response.json()
            
            # Parse response (try common formats)
            content = ""
            tool_calls = None
            finish_reason = "stop"
            
            # OpenAI-compatible format
            if "choices" in data:
                choice = data["choices"][0]
                message = choice.get("message", {})
                content = message.get("content", "")
                tool_calls = message.get("tool_calls")
                finish_reason = choice.get("finish_reason", "stop")
            
            # Anthropic-compatible format
            elif "content" in data and isinstance(data["content"], list):
                for block in data["content"]:
                    if block.get("type") == "text":
                        content += block.get("text", "")
                    elif block.get("type") == "tool_use":
                        if tool_calls is None:
                            tool_calls = []
                        tool_calls.append({
                            "id": block.get("id", ""),
                            "type": "function",
                            "function": {
                                "name": block.get("name", ""),
                                "arguments": json.dumps(block.get("input", {}))
                            }
                        })
            
            # Generic format
            elif "message" in data:
                content = data["message"].get("content", "")
                tool_calls = data["message"].get("tool_calls")
            
            # Parse tool calls
            parsed_tool_calls = None
            if tool_calls:
                parsed_tool_calls = self._parse_tool_calls(tool_calls)
            
            return AIResponse(
                content=content,
                tool_calls=parsed_tool_calls,
                finish_reason=finish_reason,
                model=self.model,
                provider=self.name
            )
            
        except httpx.TimeoutException:
            return AIResponse(
                content="Request timeout - the API took too long to respond",
                finish_reason="error"
            )
        except Exception as e:
            return AIResponse(
                content=f"API Error: {str(e)}",
                finish_reason="error"
            )


def load_custom_providers() -> Dict[str, CustomAIProvider]:
    """Load all custom providers from config and environment"""
    providers = {}
    config = get_config()
    
    # Load custom providers from config file
    custom_configs = config.load_custom_providers()
    for name, custom_config in custom_configs.items():
        providers[name] = CustomAIProvider(custom_config)
    
    # Load providers from environment variables
    env_providers = config.get_env_providers()
    for name, env_config in env_providers.items():
        custom_config = CustomProvider(
            name=env_config['name'],
            api_key=env_config['api_key'],
            base_url=env_config['base_url'],
            model=env_config['model'],
            headers=env_config['headers'],
            supports_tools=env_config['supports_tools'],
            auth_type=env_config['auth_type']
        )
        providers[name] = CustomAIProvider(custom_config)
    
    return providers