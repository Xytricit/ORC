"""
ORC Configuration Manager
Handles user-defined AI providers and models
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class CustomProvider:
    """User-defined AI provider configuration"""
    name: str
    api_key: str
    base_url: str
    model: str
    headers: Dict[str, str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    supports_tools: bool = True
    auth_type: str = "bearer"  # bearer, api_key, custom
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


class ORCConfig:
    """Configuration manager for ORC"""
    
    def __init__(self):
        self.config_dir = Path.cwd() / ".orc"
        self.config_file = self.config_dir / "config.json"
        self.custom_providers_file = self.config_dir / "custom_providers.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Create .orc directory if it doesn't exist"""
        self.config_dir.mkdir(exist_ok=True)
    
    def load_custom_providers(self) -> Dict[str, CustomProvider]:
        """Load user-defined custom providers"""
        if not self.custom_providers_file.exists():
            return {}
        
        try:
            with open(self.custom_providers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            providers = {}
            for name, config in data.items():
                providers[name] = CustomProvider(**config)
            
            return providers
        except Exception:
            return {}
    
    def save_custom_provider(self, provider: CustomProvider):
        """Save a custom provider configuration"""
        providers = self.load_custom_providers()
        providers[provider.name] = provider
        
        # Convert to dict for JSON serialization
        providers_dict = {name: asdict(provider) for name, provider in providers.items()}
        
        with open(self.custom_providers_file, 'w', encoding='utf-8') as f:
            json.dump(providers_dict, f, indent=2, ensure_ascii=False)
    
    def remove_custom_provider(self, name: str) -> bool:
        """Remove a custom provider"""
        providers = self.load_custom_providers()
        if name in providers:
            del providers[name]
            
            providers_dict = {name: asdict(provider) for name, provider in providers.items()}
            
            with open(self.custom_providers_file, 'w', encoding='utf-8') as f:
                json.dump(providers_dict, f, indent=2, ensure_ascii=False)
            return True
        return False
    
    def get_env_providers(self) -> Dict[str, Dict[str, str]]:
        """Get providers defined in environment variables"""
        env_providers = {}
        
        # Scan for provider patterns like CUSTOM_PROVIDER_NAME, CUSTOM_PROVIDER_API_KEY, etc.
        env_vars = [v for v in os.environ.keys() if v.startswith('CUSTOM_')]
        
        provider_names = set()
        for var in env_vars:
            parts = var.split('_')
            if len(parts) >= 3 and parts[1] == 'PROVIDER':
                provider_names.add(parts[2].lower())
        
        for provider_name in provider_names:
            prefix = f"CUSTOM_PROVIDER_{provider_name.upper()}"
            config = {
                'name': provider_name,
                'api_key': os.getenv(f"{prefix}_API_KEY", ""),
                'base_url': os.getenv(f"{prefix}_BASE_URL", ""),
                'model': os.getenv(f"{prefix}_MODEL", "default"),
                'headers': {},
                'supports_tools': os.getenv(f"{prefix}_SUPPORTS_TOOLS", "true").lower() == "true",
                'auth_type': os.getenv(f"{prefix}_AUTH_TYPE", "bearer").lower()
            }
            
            # Parse custom headers
            headers_str = os.getenv(f"{prefix}_HEADERS", "")
            if headers_str:
                try:
                    config['headers'] = json.loads(headers_str)
                except json.JSONDecodeError:
                    pass
            
            # Only add if we have essential config
            if config['api_key'] and config['base_url']:
                env_providers[provider_name] = config
        
        return env_providers
    
    def list_all_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all available providers (built-in + custom + env)"""
        all_providers = {}
        
        # Built-in providers
        all_providers.update({
            'ollama': {'type': 'builtin', 'name': 'Ollama', 'description': 'Free local AI'},
            'groq': {'type': 'builtin', 'name': 'Groq', 'description': 'Fast inference'},
            'openai': {'type': 'builtin', 'name': 'OpenAI', 'description': 'GPT models'},
            'anthropic': {'type': 'builtin', 'name': 'Anthropic', 'description': 'Claude models'},
            'deepseek': {'type': 'builtin', 'name': 'DeepSeek', 'description': 'Affordable code models'},
            'gemini': {'type': 'builtin', 'name': 'Gemini', 'description': 'Google AI models'}
        })
        
        # Custom providers
        custom_providers = self.load_custom_providers()
        for name, provider in custom_providers.items():
            all_providers[name] = {
                'type': 'custom',
                'name': provider.name,
                'description': f'Custom: {provider.base_url}',
                'model': provider.model,
                'supports_tools': provider.supports_tools
            }
        
        # Environment providers
        env_providers = self.get_env_providers()
        for name, config in env_providers.items():
            all_providers[name] = {
                'type': 'environment',
                'name': config['name'],
                'description': f'Env: {config["base_url"]}',
                'model': config['model'],
                'supports_tools': config['supports_tools']
            }
        
        return all_providers


# Singleton instance
_config: Optional[ORCConfig] = None


def get_config() -> ORCConfig:
    """Get or create the config singleton"""
    global _config
    if _config is None:
        _config = ORCConfig()
    return _config