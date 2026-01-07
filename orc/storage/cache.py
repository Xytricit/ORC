"""
ORC Storage: Caching Layer
"""
import pickle
import time
from pathlib import Path
from typing import Any, Optional
import hashlib

class Cache:
    """Caching layer to avoid re-parsing unchanged files"""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self.cache_dir / "index.pkl"
        self._index = self._load_index()

    def _load_index(self) -> dict:
        """Load cache index from disk"""
        if self._index_file.exists():
            try:
                with open(self._index_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return {}
        return {}

    def _save_index(self):
        """Save cache index to disk"""
        with open(self._index_file, 'wb') as f:
            pickle.dump(self._index, f)

    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key"""
        # Use hash of key to avoid filesystem issues with special characters
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def get(self, key: str) -> Optional[Any]:
        """Get cached value by key"""
        if key not in self._index:
            return None

        cache_info = self._index[key]
        cache_path = self._get_cache_path(key)

        # Check if cache is still valid (not expired)
        if time.time() - cache_info['timestamp'] > cache_info['ttl']:
            self._remove(key)
            return None

        # Check if source file is still newer than cache
        if 'source_path' in cache_info:
            try:
                source_mtime = Path(cache_info['source_path']).stat().st_mtime
                if source_mtime > cache_info['timestamp']:
                    self._remove(key)
                    return None
            except FileNotFoundError:
                self._remove(key)
                return None

        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except:
            self._remove(key)
            return None

    def set(self, key: str, value: Any, ttl: int = 3600, source_path: str = None):
        """Set cached value with TTL and optional source file path"""
        cache_path = self._get_cache_path(key)

        # Save the value to cache file
        with open(cache_path, 'wb') as f:
            pickle.dump(value, f)

        # Update index
        self._index[key] = {
            'timestamp': time.time(),
            'ttl': ttl,
            'source_path': source_path
        }
        self._save_index()

    def _remove(self, key: str):
        """Remove a key from cache"""
        if key in self._index:
            del self._index[key]
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
            self._save_index()

    def invalidate(self, key: str = None):
        """Invalidate specific key or all cache"""
        if key:
            self._remove(key)
        else:
            # Clear all cache files
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            self._index = {}
            self._save_index()

    def is_fresh(self, key: str, source_path: str) -> bool:
        """Check if cached version is fresh compared to source"""
        if key not in self._index:
            return False

        cache_info = self._index[key]
        try:
            source_mtime = Path(source_path).stat().st_mtime
            return source_mtime <= cache_info['timestamp']
        except FileNotFoundError:
            return False
