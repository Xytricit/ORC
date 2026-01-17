"""
Test suite for cache.py - Caching Layer

Tests TTL expiration, mtime validation, cache invalidation, and error handling.
"""
import pytest
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from orc.core.cache import Cache


class TestCacheBasics:
    """Test basic cache operations."""
    
    def test_cache_initializes(self, temp_dir):
        """Test cache initialization creates directory."""
        cache_dir = temp_dir / "cache"
        cache = Cache(cache_dir=cache_dir, default_ttl=3600)
        
        assert cache.cache_dir.exists()
        assert cache.cache_dir.is_dir()
    
    def test_cache_set_and_get(self, temp_dir):
        """Test basic set/get operations."""
        cache = Cache(cache_dir=temp_dir / "cache")
        
        cache.set('test_key', {'data': 'value'}, ttl=3600)
        result = cache.get('test_key')
        
        assert result == {'data': 'value'}
    
    def test_cache_get_nonexistent_key(self, temp_dir):
        """Test getting non-existent key returns None."""
        cache = Cache(cache_dir=temp_dir / "cache")
        
        result = cache.get('nonexistent')
        assert result is None
    
    def test_cache_handles_various_data_types(self, temp_dir):
        """Test caching various Python data types."""
        cache = Cache(cache_dir=temp_dir / "cache")
        
        test_data = {
            'string': 'hello',
            'int': 42,
            'float': 3.14,
            'list': [1, 2, 3],
            'dict': {'nested': 'value'},
            'tuple': (1, 2, 3),
            'bool': True,
            'none': None,
        }
        
        cache.set('test', test_data)
        result = cache.get('test')
        
        assert result == test_data


class TestCacheTTL:
    """Test TTL (time-to-live) expiration."""
    
    def test_cache_respects_ttl(self, temp_dir):
        """Test that cache expires after TTL."""
        cache = Cache(cache_dir=temp_dir / "cache")
        
        # Set with 1 second TTL
        cache.set('test_key', 'value', ttl=1)
        
        # Should exist immediately
        assert cache.get('test_key') == 'value'
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get('test_key') is None
    
    def test_cache_uses_default_ttl(self, temp_dir):
        """Test that default TTL is used when not specified."""
        cache = Cache(cache_dir=temp_dir / "cache", default_ttl=3600)
        
        cache.set('test_key', 'value')  # No TTL specified
        result = cache.get('test_key')
        
        assert result == 'value'


class TestCacheMtimeValidation:
    """Test modification time validation."""
    
    def test_cache_invalidates_on_source_modification(self, temp_dir):
        """Test that cache invalidates when source file is modified."""
        cache = Cache(cache_dir=temp_dir / "cache")
        source_file = temp_dir / "source.txt"
        source_file.write_text("original content")
        
        # Cache with source tracking
        cache.set('test', 'cached_value', ttl=3600, source_path=source_file)
        
        assert cache.get('test') == 'cached_value'
        
        # Modify source file
        time.sleep(0.1)  # Ensure mtime changes
        source_file.write_text("modified content")
        
        # Cache should be invalidated
        assert cache.get('test') is None
    
    def test_cache_invalidates_if_source_deleted(self, temp_dir):
        """Test that cache invalidates when source file is deleted."""
        cache = Cache(cache_dir=temp_dir / "cache")
        source_file = temp_dir / "source.txt"
        source_file.write_text("content")
        
        cache.set('test', 'value', source_path=source_file)
        assert cache.get('test') == 'value'
        
        # Delete source
        source_file.unlink()
        
        # Cache should be invalidated
        assert cache.get('test') is None
    
    def test_cache_is_fresh_method(self, temp_dir):
        """Test is_fresh() method for cache validity checking."""
        cache = Cache(cache_dir=temp_dir / "cache")
        source_file = temp_dir / "source.txt"
        source_file.write_text("content")
        
        cache.set('test', 'value', ttl=3600, source_path=source_file)
        
        # Should be fresh
        assert cache.is_fresh('test', source_file) is True
        
        # Modify source
        time.sleep(0.1)
        source_file.write_text("modified")
        
        # Should not be fresh
        assert cache.is_fresh('test', source_file) is False


class TestCacheInvalidation:
    """Test cache invalidation operations."""
    
    def test_cache_invalidate_specific_key(self, temp_dir):
        """Test invalidating specific cache key."""
        cache = Cache(cache_dir=temp_dir / "cache")
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        cache.invalidate('key1')
        
        assert cache.get('key1') is None
        assert cache.get('key2') == 'value2'
    
    def test_cache_invalidate_all(self, temp_dir):
        """Test invalidating entire cache."""
        cache = Cache(cache_dir=temp_dir / "cache")
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        cache.invalidate()  # No key = invalidate all
        
        assert cache.get('key1') is None
        assert cache.get('key2') is None
        assert cache.get('key3') is None


class TestCacheErrorHandling:
    """Test cache error handling and edge cases."""
    
    def test_cache_handles_corrupted_cache_file(self, temp_dir):
        """Test that corrupted cache files are handled gracefully."""
        cache = Cache(cache_dir=temp_dir / "cache")
        
        # Create a valid cache entry
        cache.set('test', 'value')
        
        # Corrupt the cache file
        cache_path = cache._get_cache_path('test')
        cache_path.write_bytes(b'corrupted data')
        
        # Should return None and clean up
        assert cache.get('test') is None
    
    def test_cache_handles_corrupted_index(self, temp_dir):
        """Test that corrupted index is rebuilt."""
        cache_dir = temp_dir / "cache"
        cache = Cache(cache_dir=cache_dir)
        
        # Corrupt the index
        cache._index_file.write_text("not pickle data")
        
        # Should rebuild index
        cache2 = Cache(cache_dir=cache_dir)
        assert isinstance(cache2._index, dict)
    
    def test_cache_rejects_invalid_cache_dir(self):
        """Test that invalid cache_dir raises ValueError."""
        with pytest.raises(ValueError, match="must be a Path object"):
            Cache(cache_dir="not_a_path_object")
    
    def test_cache_handles_unpicklable_value(self, temp_dir):
        """Test that unpicklable values raise error."""
        cache = Cache(cache_dir=temp_dir / "cache")
        
        # Lambda functions cannot be pickled
        with pytest.raises((TypeError, AttributeError)):
            cache.set('test', lambda x: x)


class TestCacheStats:
    """Test cache statistics."""
    
    def test_cache_get_stats(self, temp_dir):
        """Test getting cache statistics."""
        cache = Cache(cache_dir=temp_dir / "cache")
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        stats = cache.get_stats()
        
        assert stats['total_entries'] == 2
        assert stats['cache_size_bytes'] > 0
        assert stats['cache_size_mb'] >= 0
        assert 'cache_dir' in stats
    
    def test_cache_repr(self, temp_dir):
        """Test cache __repr__ for debugging."""
        cache = Cache(cache_dir=temp_dir / "cache")
        cache.set('key1', 'value1')
        
        repr_str = repr(cache)
        assert 'Cache' in repr_str
        assert 'entries=' in repr_str

