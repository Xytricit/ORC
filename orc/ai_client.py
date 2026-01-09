"""
Multi-Provider AI Client for ORC
Supports: Ollama (free/local), Groq, DeepSeek, Anthropic, OpenAI, Google Gemini
Users bring their own API keys!
"""

import os
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class AIResponse:
    """Structured AI response"""
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    finish_reason: str = "stop"
    model: str = ""
    provider: str = ""


class AIProvider(ABC):
    """Base class for AI providers"""
    
    name: str = "base"
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured and available"""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict], tools: Optional[List[Dict]], 
             temperature: float, max_tokens: int) -> AIResponse:
        """Send chat request"""
        pass
    
    def _parse_tool_calls(self, tool_calls) -> Optional[List[Dict]]:
        """Parse tool calls from response"""
        if not tool_calls:
            return None
        
        parsed = []
        for tc in tool_calls:
            try:
                parsed.append({
                    "id": getattr(tc, 'id', f"call_{len(parsed)}"),
                    "type": "function",
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                })
            except Exception:
                continue
        
        return parsed if parsed else None


class OllamaProvider(AIProvider):
    """Ollama - Free local AI"""
    
    name = "Ollama"
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.1")
        self._available = None
    
    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        
        try:
            import httpx
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            self._available = response.status_code == 200
        except Exception:
            self._available = False
        
        return self._available
    
    def chat(self, messages: List[Dict], tools: Optional[List[Dict]],
             temperature: float, max_tokens: int) -> AIResponse:
        import httpx
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        # Ollama tool support (if available)
        if tools:
            payload["tools"] = tools
        
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120.0
        )
        response.raise_for_status()
        data = response.json()
        
        message = data.get("message", {})
        tool_calls = None
        
        if "tool_calls" in message:
            tool_calls = [
                {
                    "id": f"call_{i}",
                    "type": "function",
                    "name": tc["function"]["name"],
                    "arguments": tc["function"]["arguments"]
                }
                for i, tc in enumerate(message["tool_calls"])
            ]
        
        return AIResponse(
            content=message.get("content", ""),
            tool_calls=tool_calls,
            finish_reason="stop",
            model=self.model,
            provider=self.name
        )


class GroqProvider(AIProvider):
    """Groq - Fast inference, free tier"""
    
    name = "Groq"
    
    def __init__(self, api_key=None, model=None):
        # Prioritize passed-in credentials (from web config) over env vars
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.client = None
        
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except ImportError:
                pass
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def chat(self, messages: List[Dict], tools: Optional[List[Dict]],
             temperature: float, max_tokens: int) -> AIResponse:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        try:
            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message
            
            return AIResponse(
                content=message.content or "",
                tool_calls=self._parse_tool_calls(getattr(message, 'tool_calls', None)),
                finish_reason=response.choices[0].finish_reason,
                model=self.model,
                provider=self.name
            )
        except Exception as e:
            # Re-raise with the actual error for better debugging
            error_msg = str(e)
            raise Exception(f"{error_msg}")


class DeepSeekProvider(AIProvider):
    """DeepSeek - Cheap, good for code"""
    
    name = "DeepSeek"
    
    def __init__(self, api_key=None, model=None):
        # Prioritize passed-in credentials (from web config) over env vars
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com/v1"
                )
            except ImportError:
                pass
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def chat(self, messages: List[Dict], tools: Optional[List[Dict]],
             temperature: float, max_tokens: int) -> AIResponse:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        response = self.client.chat.completions.create(**kwargs)
        message = response.choices[0].message
        
        return AIResponse(
            content=message.content or "",
            tool_calls=self._parse_tool_calls(getattr(message, 'tool_calls', None)),
            finish_reason=response.choices[0].finish_reason,
            model=self.model,
            provider=self.name
        )


class AnthropicProvider(AIProvider):
    """Anthropic Claude - High quality"""
    
    name = "Anthropic"
    
    def __init__(self, api_key=None, model=None):
        # Prioritize passed-in credentials (from web config) over env vars
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        self.client = None
        
        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                pass
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def chat(self, messages: List[Dict], tools: Optional[List[Dict]],
             temperature: float, max_tokens: int) -> AIResponse:
        # Separate system message from conversation
        system_msg = ""
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append(msg)
        
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": chat_messages,
        }
        
        if system_msg:
            kwargs["system"] = system_msg
        
        if tools:
            # Convert to Anthropic tool format
            anthropic_tools = []
            for tool in tools:
                if tool.get("type") == "function":
                    func = tool["function"]
                    anthropic_tools.append({
                        "name": func["name"],
                        "description": func.get("description", ""),
                        "input_schema": func.get("parameters", {})
                    })
            kwargs["tools"] = anthropic_tools
        
        response = self.client.messages.create(**kwargs)
        
        # Parse response
        content = ""
        tool_calls = []
        
        for block in response.content:
            if block.type == "text":
                content = block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "type": "function",
                    "name": block.name,
                    "arguments": block.input
                })
        
        return AIResponse(
            content=content,
            tool_calls=tool_calls if tool_calls else None,
            finish_reason=response.stop_reason,
            model=self.model,
            provider=self.name
        )


class OpenAIProvider(AIProvider):
    """OpenAI GPT models"""
    
    name = "OpenAI"
    
    def __init__(self, api_key=None, model=None):
        # Prioritize passed-in credentials (from web config) over env vars
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                pass
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def chat(self, messages: List[Dict], tools: Optional[List[Dict]],
             temperature: float, max_tokens: int) -> AIResponse:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        response = self.client.chat.completions.create(**kwargs)
        message = response.choices[0].message
        
        return AIResponse(
            content=message.content or "",
            tool_calls=self._parse_tool_calls(getattr(message, 'tool_calls', None)),
            finish_reason=response.choices[0].finish_reason,
            model=self.model,
            provider=self.name
        )


class GeminiProvider(AIProvider):
    """Google Gemini - Free tier available"""
    
    name = "Gemini"
    
    def __init__(self, api_key=None, model=None):
        # Prioritize passed-in credentials (from web config) over env vars
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.client = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai
            except ImportError:
                pass
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def chat(self, messages: List[Dict], tools: Optional[List[Dict]],
             temperature: float, max_tokens: int) -> AIResponse:
        # Convert messages to Gemini format
        system_instruction = ""
        gemini_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})
        
        model = self.client.GenerativeModel(
            self.model,
            system_instruction=system_instruction if system_instruction else None
        )
        
        # Gemini tool support
        gemini_tools = None
        if tools:
            tool_declarations = []
            for tool in tools:
                if tool.get("type") == "function":
                    func = tool["function"]
                    tool_declarations.append(self.client.protos.Tool(
                        function_declarations=[
                            self.client.protos.FunctionDeclaration(
                                name=func["name"],
                                description=func.get("description", ""),
                                parameters=func.get("parameters", {})
                            )
                        ]
                    ))
            if tool_declarations:
                gemini_tools = tool_declarations
        
        generation_config = self.client.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
        
        response = chat.send_message(
            gemini_messages[-1]["parts"][0] if gemini_messages else "",
            generation_config=generation_config,
            tools=gemini_tools
        )
        
        # Parse response
        content = response.text if hasattr(response, 'text') else ""
        tool_calls = None
        
        # Check for function calls
        if hasattr(response, 'candidates') and response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    fc = part.function_call
                    tool_calls = tool_calls or []
                    tool_calls.append({
                        "id": f"call_{len(tool_calls)}",
                        "type": "function",
                        "name": fc.name,
                        "arguments": dict(fc.args)
                    })
        
        return AIResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason="stop",
            model=self.model,
            provider=self.name
        )


class MultiProviderClient:
    """
    AI Client that supports multiple providers.
    
    BYOK (Bring Your Own Key) - This is open source software.
    Users provide their own API keys. No keys are included or required.
    
    Supported providers (in priority order):
    1. Ollama (free, local, no API key needed)
    2. Groq (free tier, 100k tokens/day)
    3. Gemini (free tier, 1M tokens/day, requires 18+)
    4. DeepSeek (cheap, $0.14/1M tokens)
    5. OpenAI (paid, GPT models)
    6. Anthropic (paid, Claude models)
    
    Configure via .env file or environment variables.
    """
    
    def __init__(self, web_configs=None):
        """
        Initialize MultiProviderClient
        
        Args:
            web_configs: Optional dict of {provider: {api_key, model_name}} from web interface
                        If provided, these configs take priority over .env variables
        """
        # Initialize providers with web configs if available
        if web_configs:
            self.providers: Dict[str, AIProvider] = {
                "ollama": OllamaProvider(),
                "groq": GroqProvider(
                    api_key=web_configs.get("groq", {}).get("api_key"),
                    model=web_configs.get("groq", {}).get("model_name")
                ) if "groq" in web_configs else GroqProvider(),
                "deepseek": DeepSeekProvider(
                    api_key=web_configs.get("deepseek", {}).get("api_key"),
                    model=web_configs.get("deepseek", {}).get("model_name")
                ) if "deepseek" in web_configs else DeepSeekProvider(),
                "gemini": GeminiProvider(
                    api_key=web_configs.get("gemini", {}).get("api_key"),
                    model=web_configs.get("gemini", {}).get("model_name")
                ) if "gemini" in web_configs else GeminiProvider(),
                "openai": OpenAIProvider(
                    api_key=web_configs.get("openai", {}).get("api_key"),
                    model=web_configs.get("openai", {}).get("model_name")
                ) if "openai" in web_configs else OpenAIProvider(),
                "anthropic": AnthropicProvider(
                    api_key=web_configs.get("anthropic", {}).get("api_key"),
                    model=web_configs.get("anthropic", {}).get("model_name")
                ) if "anthropic" in web_configs else AnthropicProvider(),
            }
        else:
            # No web configs - fall back to env vars only
            self.providers: Dict[str, AIProvider] = {
                "ollama": OllamaProvider(),
                "groq": GroqProvider(),
                "deepseek": DeepSeekProvider(),
                "gemini": GeminiProvider(),
                "openai": OpenAIProvider(),
                "anthropic": AnthropicProvider(),
            }
        
        # Load custom providers
        try:
            from .custom_provider import load_custom_providers
            custom_providers = load_custom_providers()
            self.providers.update(custom_providers)
        except ImportError:
            pass  # custom_provider module not available
        
        # Get preferred provider order from env
        preferred = os.getenv("ORC_AI_PROVIDER", "").lower()
        
        if preferred and preferred in self.providers:
            # User specified a preferred provider
            self.provider_order = [preferred] + [p for p in self.providers if p != preferred]
        else:
            # Default order: free/local first, then paid
            self.provider_order = ["ollama", "groq", "gemini", "deepseek", "openai", "anthropic"]
        
        # Find first available provider
        self.active_provider: Optional[AIProvider] = None
        for name in self.provider_order:
            if self.providers[name].is_available():
                self.active_provider = self.providers[name]
                break
    
    def is_available(self) -> bool:
        return self.active_provider is not None
    
    def get_status(self) -> str:
        if self.active_provider:
            return f"{self.active_provider.name} ({self.active_provider.model})"
        return "No AI provider available"
    
    def get_available_providers(self) -> List[str]:
        """Get list of all configured providers"""
        return [name for name, provider in self.providers.items() if provider.is_available()]
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AIResponse:
        """Send chat request, trying providers in order until one succeeds"""
        
        errors = []
        
        for name in self.provider_order:
            provider = self.providers[name]
            if not provider.is_available():
                continue
            
            try:
                return provider.chat(messages, tools, temperature, max_tokens)
            except Exception as e:
                error_str = str(e)
                errors.append(f"{provider.name}: {error_str}")
                continue
        
        # All providers failed - build helpful error message
        if not errors:
            error_msg = "No AI providers configured. Add API keys to your .env file."
        else:
            # Check what types of errors we have
            has_rate_limit = any("rate limit" in err.lower() or "429" in err for err in errors)
            has_insufficient_balance = any("insufficient balance" in err.lower() or "402" in err for err in errors)
            has_invalid_key = any("invalid" in err.lower() and "key" in err.lower() for err in errors)
            
            # Build error message
            error_msg = "All configured AI providers failed:\n\n"
            for err in errors:
                # Shorten long error messages
                if len(err) > 150:
                    err = err[:150] + "..."
                error_msg += f"  • {err}\n"
            
            error_msg += "\nQuick Solutions:\n"
            
            if has_rate_limit:
                error_msg += "  - Wait a few minutes for rate limit to reset\n"
            if has_insufficient_balance:
                error_msg += "  - Add credits to your provider account\n"
            if has_invalid_key:
                error_msg += "  - Check your API keys in .env file\n"
            
            # Always suggest alternatives
            error_msg += "  - Configure another provider with: /providers\n"
            error_msg += "  - Free options: Gemini (makersuite.google.com) or local Ollama\n"
        
        return AIResponse(
            content=error_msg,
            finish_reason="error"
        )


# Singleton instance
_client: Optional[MultiProviderClient] = None


def get_ai_client(force_new: bool = False, web_configs=None) -> MultiProviderClient:
    """
    Get or create the AI client singleton
    
    Args:
        force_new: Force creating a new client
        web_configs: Optional dict of provider configs from web interface
    """
    global _client
    if _client is None or force_new or web_configs:
        _client = MultiProviderClient(web_configs=web_configs)
    return _client


def reset_ai_client():
    """Reset the AI client (call after loading new env vars)"""
    global _client
    _client = None
