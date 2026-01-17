"""
Test suite for index_service.py - Index Service Façade

Tests service coordination, caching integration, and unified API.
"""
import pytest
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from orc.core.index_service import IndexService, create_index_service
from orc.core.config import ORCConfig
from orc.core.cache import Cache


class TestIndexServiceInitialization:
    """Test service initialization."""
    
    def test_service_initializes_with_defaults(self, sample_project):
        """Test service initializes with default config and cache."""
        import os
        os.chdir(sample_project)
        
        service = IndexService()
        
        assert service.config is not None
        assert service.cache is not None
    
    def test_service_accepts_custom_config(self, sample_project):
        """Test service accepts custom config."""
        config = ORCConfig(config_path=None)
        service = IndexService(config=config)
        
        assert service.config is config
    
    def test_service_accepts_custom_cache(self, temp_dir):
        """Test service accepts custom cache."""
        cache = Cache(cache_dir=temp_dir / "cache")
        service = IndexService(cache=cache)
        
        assert service.cache is cache


class TestIndexServiceIndexing:
    """Test indexing operations."""
    
    def test_service_indexes_project(self, sample_project):
        """Test basic project indexing through service."""
        import os
        os.chdir(sample_project)
        
        service = IndexService()
        index, stats = service.index_project()
        
        assert 'files' in index
        assert stats['total_files'] > 0
    
    def test_service_caches_index_results(self, sample_project):
        """Test that index results are cached."""
        import os
        os.chdir(sample_project)
        
        service = IndexService()
        
        # First index - should be cache miss
        index1, stats1 = service.index_project()
        assert stats1['cache_hit'] is False
        
        # Second index - should be cache hit
        index2, stats2 = service.index_project()
        assert stats2['cache_hit'] is True
        
        # Results should be the same
        assert len(index1['files']) == len(index2['files'])
    
    def test_service_force_refresh_bypasses_cache(self, sample_project):
        """Test that force_refresh bypasses cache."""
        import os
        os.chdir(sample_project)
        
        service = IndexService()
        
        # First index
        index1, stats1 = service.index_project()
        assert stats1['cache_hit'] is False
        
        # Force refresh - should bypass cache
        index2, stats2 = service.index_project(force_refresh=True)
        assert stats2['cache_hit'] is False
    
    def test_service_respects_custom_extensions(self, sample_project):
        """Test indexing with custom file extensions."""
        import os
        os.chdir(sample_project)
        
        # Create a JS file
        (sample_project / "app.js").write_text("console.log('test');")
        
        service = IndexService()
        index, stats = service.index_project(extensions=['.js'])
        
        # Should only index JS files
        assert all('.js' in str(f) for f in index['files'].keys())


class TestIndexServiceCacheManagement:
    """Test cache management operations."""
    
    def test_service_invalidates_cache(self, sample_project):
        """Test cache invalidation."""
        import os
        os.chdir(sample_project)
        
        service = IndexService()
        
        # Index and cache
        service.index_project()
        
        # Invalidate cache
        service.invalidate_cache()
        
        # Next index should be cache miss
        index, stats = service.index_project()
        assert stats['cache_hit'] is False
    
    def test_service_invalidates_specific_cache_key(self, sample_project):
        """Test invalidating specific cache key."""
        import os
        os.chdir(sample_project)
        
        service = IndexService()
        
        # Index with different extensions
        service.index_project(extensions=['.py'])
        service.index_project(extensions=['.js'])
        
        # Invalidate only .py cache
        cache_key = service._generate_cache_key(['.py'])
        service.invalidate_cache(cache_key)
        
        # .py should be cache miss, .js should be cache hit
        index1, stats1 = service.index_project(extensions=['.py'])
        assert stats1['cache_hit'] is False
    
    def test_service_is_cache_fresh(self, sample_project):
        """Test is_cache_fresh() method."""
        import os
        os.chdir(sample_project)
        
        service = IndexService()
        
        # No cache yet
        assert service.is_cache_fresh() is False
        
        # Index to create cache
        service.index_project()
        
        # Cache should be fresh
        assert service.is_cache_fresh() is True
    
    def test_service_get_cache_stats(self, sample_project):
        """Test getting cache statistics."""
        import os
        os.chdir(sample_project)
        
        service = IndexService()
        service.index_project()
        
        stats = service.get_cache_stats()
        
        assert 'total_entries' in stats
        assert stats['total_entries'] > 0


class TestIndexServiceConfigSummary:
    """Test configuration summary."""
    
    def test_service_get_config_summary(self, sample_project):
        """Test getting configuration summary."""
        import os
        os.chdir(sample_project)
        
        service = IndexService()
        summary = service.get_config_summary()
        
        assert 'project_root' in summary
        assert 'cache_dir' in summary
        assert 'max_workers' in summary
        assert 'file_extensions' in summary


class TestIndexServiceFactoryFunction:
    """Test create_index_service factory function."""
    
    def test_create_index_service(self, sample_project, sample_config_yaml):
        """Test factory function creates service."""
        import os
        os.chdir(sample_project)
        
        service = create_index_service(config_path=sample_config_yaml)
        
        assert isinstance(service, IndexService)
        assert service.config.cache_ttl == 1800  # From sample config


class TestIndexServiceRepr:
    """Test string representation."""
    
    def test_service_repr(self, sample_project):
        """Test service __repr__ for debugging."""
        import os
        os.chdir(sample_project)
        
        service = IndexService()
        repr_str = repr(service)
        
        assert 'IndexService' in repr_str
        assert 'project=' in repr_str


class TestIndexServiceIntegration:
    """Integration tests combining all components."""
    
    def test_service_full_workflow(self, sample_project):
        """Test complete indexing workflow."""
        import os
        os.chdir(sample_project)
        
        # Initialize service
        service = IndexService()
        
        # Get config summary
        config_summary = service.get_config_summary()
        assert config_summary['project_root'] == str(sample_project)
        
        # Index project
        index, stats = service.index_project()
        assert stats['total_files'] > 0
        assert stats['cache_hit'] is False
        
        # Second index should hit cache
        index2, stats2 = service.index_project()
        assert stats2['cache_hit'] is True
        
        # Get cache stats
        cache_stats = service.get_cache_stats()
        assert cache_stats['total_entries'] > 0
        
        # Invalidate and re-index
        service.invalidate_cache()
        index3, stats3 = service.index_project()
        assert stats3['cache_hit'] is False



