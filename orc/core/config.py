"""
ORC Configuration System - Production Ready

Handles YAML configuration files with environment variable overrides.
No hardcoded paths. Cross-platform compatible.

Security: No eval/exec, validates all inputs, safe YAML loading only.
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml

logger = logging.getLogger(__name__)


class ORCConfig:
    """
    Configuration manager for ORC indexing system.
    
    Loads configuration from:
    1. Default values (lowest priority)
    2. YAML config file (if exists)
    3. Environment variables (highest priority)
    
    Why this design: Allows flexible deployment - developers use YAML files,
    production systems use environment variables, sensible defaults for quick start.
    """
    
    # Default configuration values
    DEFAULTS = {
        'project_root': '.',
        'cache_dir': '.orc/cache',
        'cache_ttl': 3600,  # 1 hour in seconds
        'max_workers': None,  # None = auto-detect CPU count
        'ignore_patterns': [
            'node_modules/',
            '__pycache__/',
            '*.pyc',
            '.git/',
            '.venv/',
            'venv/',
            'dist/',
            'build/',
            '*.min.js',
            '*.bundle.js',
            'coverage/',
            '.pytest_cache/',
            '.mypy_cache/',
        ],
        'file_extensions': ['.py', '.js', '.ts', '.jsx', '.tsx'],
        'log_level': 'INFO',
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration system.
        
        Args:
            config_path: Path to YAML config file. If None, looks for 
                        'orc_config.yaml' in current directory.
        
        Raises:
            ValueError: If config file exists but is malformed
            PermissionError: If config file exists but cannot be read
        """
        self._config: Dict[str, Any] = self.DEFAULTS.copy()
        
        # Load from YAML file if exists
        if config_path is None:
            config_path = Path.cwd() / 'orc_config.yaml'
        
        if config_path and Path(config_path).exists():
            self._load_yaml(Path(config_path))
        
        # Override with environment variables
        self._load_env_vars()
        
        # Validate and normalize paths
        self._normalize_paths()
        
        logger.info(f"Configuration loaded: {self._config.get('project_root')}")
    
    def _load_yaml(self, config_path: Path) -> None:
        """
        Load configuration from YAML file.
        
        Why safe_load: Prevents code injection through YAML deserialization.
        Only loads basic Python types (dict, list, str, int, etc.)
        
        Args:
            config_path: Path to YAML file
            
        Raises:
            ValueError: If YAML is malformed or contains invalid values
            PermissionError: If file cannot be read
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
            
            if not isinstance(yaml_config, dict):
                raise ValueError(f"Config file must contain a YAML dictionary, got {type(yaml_config)}")
            
            # Merge with defaults (YAML values override defaults)
            for key, value in yaml_config.items():
                if key in self.DEFAULTS:
                    self._config[key] = value
                else:
                    logger.warning(f"Unknown config key '{key}' in {config_path}, ignoring")
            
            logger.debug(f"Loaded configuration from {config_path}")
            
        except PermissionError as e:
            logger.error(f"Permission denied reading config file: {config_path}")
            raise PermissionError(f"Cannot read config file {config_path}: {e}")
        
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in config file: {e}")
            raise ValueError(f"Malformed YAML in {config_path}: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}")
            raise ValueError(f"Failed to load config from {config_path}: {e}")
    
    def _load_env_vars(self) -> None:
        """
        Load configuration from environment variables.
        
        Environment variables have highest priority and override YAML values.
        
        Format: ORC_<KEY_NAME> (e.g., ORC_CACHE_TTL=7200)
        
        Why this approach: Standard practice for containerized deployments,
        allows secrets to be injected without files.
        """
        env_mappings = {
            'ORC_PROJECT_ROOT': ('project_root', str),
            'ORC_CACHE_DIR': ('cache_dir', str),
            'ORC_CACHE_TTL': ('cache_ttl', int),
            'ORC_MAX_WORKERS': ('max_workers', lambda x: None if x.lower() == 'auto' else int(x)),
            'ORC_LOG_LEVEL': ('log_level', str),
        }
        
        for env_var, (config_key, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    self._config[config_key] = converter(value)
                    logger.debug(f"Loaded {config_key} from environment: {value}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid value for {env_var}='{value}': {e}, using default")
        
        # Handle list-type environment variables
        ignore_patterns_env = os.getenv('ORC_IGNORE_PATTERNS')
        if ignore_patterns_env:
            # Split by comma or semicolon
            patterns = [p.strip() for p in ignore_patterns_env.replace(';', ',').split(',') if p.strip()]
            self._config['ignore_patterns'] = patterns
            logger.debug(f"Loaded ignore patterns from environment: {len(patterns)} patterns")
        
        file_extensions_env = os.getenv('ORC_FILE_EXTENSIONS')
        if file_extensions_env:
            extensions = [e.strip() for e in file_extensions_env.replace(';', ',').split(',') if e.strip()]
            self._config['file_extensions'] = extensions
            logger.debug(f"Loaded file extensions from environment: {extensions}")
    
    def _normalize_paths(self) -> None:
        """
        Convert string paths to Path objects and resolve relative paths.
        
        Why: Ensures all paths are absolute and platform-independent.
        Uses pathlib for cross-platform compatibility.
        
        Raises:
            ValueError: If project_root doesn't exist
        """
        # Resolve project root
        project_root = Path(self._config['project_root']).resolve()
        if not project_root.exists():
            raise ValueError(f"Project root does not exist: {project_root}")
        if not project_root.is_dir():
            raise ValueError(f"Project root is not a directory: {project_root}")
        
        self._config['project_root'] = project_root
        
        # Resolve cache directory (relative to project root if not absolute)
        cache_dir = Path(self._config['cache_dir'])
        if not cache_dir.is_absolute():
            cache_dir = project_root / cache_dir
        
        self._config['cache_dir'] = cache_dir
        
        # Ensure cache directory exists
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Cache directory: {cache_dir}")
        except PermissionError:
            raise PermissionError(f"Cannot create cache directory: {cache_dir}")
    
    # Public API - read-only property access
    
    @property
    def project_root(self) -> Path:
        """Project root directory (absolute path)."""
        return self._config['project_root']
    
    @property
    def cache_dir(self) -> Path:
        """Cache directory (absolute path)."""
        return self._config['cache_dir']
    
    @property
    def cache_ttl(self) -> int:
        """Cache time-to-live in seconds."""
        return self._config['cache_ttl']
    
    @property
    def max_workers(self) -> Optional[int]:
        """Maximum worker processes for parallel indexing (None = auto-detect)."""
        return self._config['max_workers']
    
    @property
    def ignore_patterns(self) -> List[str]:
        """List of patterns to ignore during indexing."""
        return self._config['ignore_patterns'].copy()  # Return copy to prevent modification
    
    @property
    def file_extensions(self) -> List[str]:
        """List of file extensions to index."""
        return self._config['file_extensions'].copy()
    
    @property
    def log_level(self) -> str:
        """Logging level (DEBUG, INFO, WARNING, ERROR)."""
        return self._config['log_level']
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Export configuration as dictionary.
        
        Returns:
            Dictionary with all configuration values (copy, not reference)
        """
        return self._config.copy()
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"ORCConfig(project_root={self.project_root}, cache_dir={self.cache_dir})"


def load_config(config_path: Optional[Path] = None) -> ORCConfig:
    """
    Convenience function to load configuration.
    
    Args:
        config_path: Optional path to YAML config file
        
    Returns:
        ORCConfig instance
        
    Raises:
        ValueError: If configuration is invalid
        PermissionError: If files cannot be accessed
    """
    return ORCConfig(config_path=config_path)
