"""
Test suite for config.py - Configuration Management System

Tests configuration loading, environment variable overrides, validation, and error handling.
"""
import pytest
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orc.core.config import ORCConfig, load_config


class TestConfigDefaults:
    """Test default configuration values."""
    
    def test_config_loads_defaults(self, temp_dir):
        """Test that config initializes with default values."""
        os.chdir(temp_dir)
        config = ORCConfig()
        
        assert config.project_root == temp_dir
        assert config.cache_ttl == 3600
        assert config.max_workers is None
        assert len(config.ignore_patterns) > 0
        assert '.py' in config.file_extensions
    
    def test_config_creates_cache_dir(self, temp_dir):
        """Test that cache directory is created automatically."""
        os.chdir(temp_dir)
        config = ORCConfig()
        
        assert config.cache_dir.exists()
        assert config.cache_dir.is_dir()


class TestConfigYAMLLoading:
    """Test YAML configuration file loading."""
    
    def test_config_loads_from_yaml(self, temp_dir, sample_config_yaml):
        """Test loading configuration from YAML file."""
        os.chdir(temp_dir)
        config = ORCConfig(config_path=sample_config_yaml)
        
        assert config.cache_ttl == 1800
        assert config.max_workers == 2
        assert config.log_level == 'DEBUG'
    
    def test_config_handles_missing_yaml(self, temp_dir):
        """Test that missing YAML file uses defaults."""
        os.chdir(temp_dir)
        non_existent = temp_dir / "nonexistent.yaml"
        config = ORCConfig(config_path=non_existent)
        
        # Should use defaults
        assert config.cache_ttl == 3600
    
    def test_config_rejects_malformed_yaml(self, temp_dir, malformed_yaml):
        """Test that malformed YAML raises ValueError."""
        os.chdir(temp_dir)
        with pytest.raises(ValueError, match="Malformed YAML"):
            ORCConfig(config_path=malformed_yaml)
    
    def test_config_rejects_non_dict_yaml(self, temp_dir):
        """Test that YAML containing non-dict raises ValueError."""
        os.chdir(temp_dir)
        bad_yaml = temp_dir / "list.yaml"
        bad_yaml.write_text("- item1\n- item2\n")
        
        with pytest.raises(ValueError, match="must contain a YAML dictionary"):
            ORCConfig(config_path=bad_yaml)


class TestConfigEnvironmentVariables:
    """Test environment variable overrides."""
    
    def test_config_env_var_overrides_yaml(self, temp_dir, sample_config_yaml, monkeypatch):
        """Test that environment variables override YAML values."""
        os.chdir(temp_dir)
        monkeypatch.setenv('ORC_CACHE_TTL', '7200')
        
        config = ORCConfig(config_path=sample_config_yaml)
        
        # YAML has 1800, env var has 7200
        assert config.cache_ttl == 7200
    
    def test_config_env_var_max_workers_auto(self, temp_dir, monkeypatch):
        """Test that ORC_MAX_WORKERS=auto sets None."""
        os.chdir(temp_dir)
        monkeypatch.setenv('ORC_MAX_WORKERS', 'auto')
        
        config = ORCConfig()
        assert config.max_workers is None
    
    def test_config_env_var_max_workers_number(self, temp_dir, monkeypatch):
        """Test that ORC_MAX_WORKERS with number sets value."""
        os.chdir(temp_dir)
        monkeypatch.setenv('ORC_MAX_WORKERS', '4')
        
        config = ORCConfig()
        assert config.max_workers == 4
    
    def test_config_env_var_ignore_patterns(self, temp_dir, monkeypatch):
        """Test loading ignore patterns from environment."""
        os.chdir(temp_dir)
        monkeypatch.setenv('ORC_IGNORE_PATTERNS', 'test/,*.tmp,dist/')
        
        config = ORCConfig()
        assert 'test/' in config.ignore_patterns
        assert '*.tmp' in config.ignore_patterns
        assert 'dist/' in config.ignore_patterns
    
    def test_config_env_var_file_extensions(self, temp_dir, monkeypatch):
        """Test loading file extensions from environment."""
        os.chdir(temp_dir)
        monkeypatch.setenv('ORC_FILE_EXTENSIONS', '.py,.js,.go')
        
        config = ORCConfig()
        assert config.file_extensions == ['.py', '.js', '.go']
    
    def test_config_env_var_invalid_value_uses_default(self, temp_dir, monkeypatch):
        """Test that invalid env var values use defaults."""
        os.chdir(temp_dir)
        monkeypatch.setenv('ORC_CACHE_TTL', 'not_a_number')
        
        config = ORCConfig()
        # Should use default
        assert config.cache_ttl == 3600


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_config_rejects_nonexistent_project_root(self, temp_dir):
        """Test that non-existent project root raises ValueError."""
        os.chdir(temp_dir)
        bad_yaml = temp_dir / "bad.yaml"
        bad_yaml.write_text("project_root: /nonexistent/path/that/does/not/exist\n")
        
        with pytest.raises(ValueError, match="does not exist"):
            ORCConfig(config_path=bad_yaml)
    
    def test_config_rejects_file_as_project_root(self, temp_dir):
        """Test that file path as project root raises ValueError."""
        os.chdir(temp_dir)
        file_path = temp_dir / "file.txt"
        file_path.write_text("content")
        
        bad_yaml = temp_dir / "bad.yaml"
        bad_yaml.write_text(f"project_root: {file_path}\n")
        
        with pytest.raises(ValueError, match="not a directory"):
            ORCConfig(config_path=bad_yaml)
    
    def test_config_normalizes_relative_paths(self, temp_dir):
        """Test that relative paths are normalized to absolute."""
        os.chdir(temp_dir)
        config = ORCConfig()
        
        assert config.project_root.is_absolute()
        assert config.cache_dir.is_absolute()


class TestConfigAPI:
    """Test configuration public API."""
    
    def test_config_properties_are_readonly_copies(self, temp_dir):
        """Test that returned lists are copies (not mutable references)."""
        os.chdir(temp_dir)
        config = ORCConfig()
        
        patterns1 = config.ignore_patterns
        patterns2 = config.ignore_patterns
        
        # Should be different list objects
        assert patterns1 is not patterns2
        
        # Modifying one shouldn't affect the other
        patterns1.append('test/')
        assert 'test/' not in patterns2
    
    def test_config_get_method(self, temp_dir):
        """Test config.get() method."""
        os.chdir(temp_dir)
        config = ORCConfig()
        
        assert config.get('cache_ttl') == 3600
        assert config.get('nonexistent_key', 'default') == 'default'
    
    def test_config_to_dict(self, temp_dir):
        """Test config.to_dict() exports all values."""
        os.chdir(temp_dir)
        config = ORCConfig()
        
        config_dict = config.to_dict()
        
        assert 'project_root' in config_dict
        assert 'cache_dir' in config_dict
        assert 'cache_ttl' in config_dict
        assert isinstance(config_dict, dict)
    
    def test_config_repr(self, temp_dir):
        """Test config __repr__ for debugging."""
        os.chdir(temp_dir)
        config = ORCConfig()
        
        repr_str = repr(config)
        assert 'ORCConfig' in repr_str
        assert str(config.project_root) in repr_str


class TestLoadConfigFunction:
    """Test convenience load_config() function."""
    
    def test_load_config_function(self, temp_dir, sample_config_yaml):
        """Test load_config() convenience function."""
        os.chdir(temp_dir)
        config = load_config(config_path=sample_config_yaml)
        
        assert isinstance(config, ORCConfig)
        assert config.cache_ttl == 1800


