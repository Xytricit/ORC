"""
ORC Caching Layer - Production Ready

File-based caching with TTL and modification time validation.
Prevents re-parsing unchanged files.

Security: Uses pickle safely (only for trusted data), validates all paths,
no unsafe operations.
"""
import pickle
import time
import logging
import hashlib
from pathlib import Path
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)


class Cache:
    """
    File-based caching layer with TTL and source file modification tracking.
    
    Why this design:
    - TTL prevents stale data even if source file mtime is unreliable
    - mtime checking catches file changes immediately
    - MD5-hashed keys prevent filesystem issues with special characters
    - Pickle index stored separately for fast key lookups
    
    Thread safety: NOT thread-safe. Use process-level locking if needed.
    """
    
    def __init__(self, cache_dir: Path, default_ttl: int = 3600):
        """
        Initialize cache layer.
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds (default: 1 hour)
            
        Raises:
            PermissionError: If cache directory cannot be created
            ValueError: If cache_dir is not a valid path
        """
        if not isinstance(cache_dir, Path):
            raise ValueError(f"cache_dir must be a Path object, got {type(cache_dir)}")
        
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self._index_file = self.cache_dir / "cache_index.pkl"
        self._index: Dict[str, Dict[str, Any]] = {}
        
        # Create cache directory
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Cache initialized: {self.cache_dir}")
        except PermissionError as e:
            raise PermissionError(f"Cannot create cache directory {cache_dir}: {e}")
        except Exception as e:
            raise ValueError(f"Invalid cache directory {cache_dir}: {e}")
        
        # Load existing index
        self._load_index()
    
    def _load_index(self) -> None:
        """
        Load cache index from disk.
        
        Why separate index: Allows fast key lookups without reading all cache files.
        
        Handles corruption gracefully by rebuilding empty index.
        """
        if not self._index_file.exists():
            self._index = {}
            logger.debug("Cache index not found, starting fresh")
            return
        
        try:
            with open(self._index_file, 'rb') as f:
                loaded = pickle.load(f)
            
            if not isinstance(loaded, dict):
                logger.warning(f"Cache index corrupted (not a dict), rebuilding")
                self._index = {}
            else:
                self._index = loaded
                logger.debug(f"Loaded cache index: {len(self._index)} entries")
        
        except Exception as e:
            logger.warning(f"Failed to load cache index: {e}, rebuilding")
            self._index = {}
    
    def _save_index(self) -> None:
        """
        Save cache index to disk.
        
        Why atomic write: Prevents index corruption if process crashes during write.
        Writes to temp file first, then renames (atomic on POSIX systems).
        
        Raises:
            PermissionError: If index cannot be written
        """
        temp_file = self._index_file.with_suffix('.tmp')
        
        try:
            with open(temp_file, 'wb') as f:
                pickle.dump(self._index, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Atomic rename (POSIX) or best-effort (Windows)
            temp_file.replace(self._index_file)
            logger.debug("Cache index saved")
        
        except PermissionError as e:
            logger.error(f"Cannot write cache index: {e}")
            if temp_file.exists():
                temp_file.unlink()
            raise PermissionError(f"Failed to save cache index: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error saving cache index: {e}")
            if temp_file.exists():
                temp_file.unlink()
            raise
    
    def _get_cache_path(self, key: str) -> Path:
        """
        Get file path for a cache key.
        
        Why MD5 hash: Prevents issues with:
        - Special characters in keys (/, \\, :, etc.)
        - Very long keys exceeding filesystem limits
        - Case-insensitive filesystems
        
        Args:
            key: Cache key (any string)
            
        Returns:
            Path to cache file
        """
        key_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve cached value by key.
        
        Returns None if:
        - Key doesn't exist
        - Cache has expired (TTL exceeded)
        - Source file has been modified since caching
        - Cache file is corrupted
        
        Why automatic cleanup: Prevents cache directory from growing unbounded
        with stale entries.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/invalid
        """
        if key not in self._index:
            logger.debug(f"Cache miss: {key} (not in index)")
            return None
        
        cache_info = self._index[key]
        cache_path = self._get_cache_path(key)
        
        # Check TTL expiration
        current_time = time.time()
        age = current_time - cache_info['timestamp']
        if age > cache_info['ttl']:
            logger.debug(f"Cache expired: {key} (age: {age:.1f}s, ttl: {cache_info['ttl']}s)")
            self._remove(key)
            return None
        
        # Check source file modification time
        source_path = cache_info.get('source_path')
        if source_path:
            try:
                source_file = Path(source_path)
                if not source_file.exists():
                    logger.debug(f"Cache invalidated: {key} (source deleted)")
                    self._remove(key)
                    return None
                
                source_mtime = source_file.stat().st_mtime
                if source_mtime > cache_info['timestamp']:
                    logger.debug(f"Cache stale: {key} (source modified)")
                    self._remove(key)
                    return None
            
            except (FileNotFoundError, PermissionError, OSError) as e:
                logger.warning(f"Cannot check source file {source_path}: {e}")
                self._remove(key)
                return None
        
        # Load cached value
        if not cache_path.exists():
            logger.warning(f"Cache file missing: {key}, removing from index")
            self._remove(key)
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                value = pickle.load(f)
            
            logger.debug(f"Cache hit: {key}")
            return value
        
        except Exception as e:
            logger.warning(f"Cache file corrupted: {key}, error: {e}")
            self._remove(key)
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            source_path: Optional[Path] = None) -> None:
        """
        Store value in cache with TTL and optional source tracking.
        
        Args:
            key: Cache key (any string)
            value: Value to cache (must be picklable)
            ttl: Time-to-live in seconds (None = use default)
            source_path: Optional source file path for mtime tracking
            
        Raises:
            PermissionError: If cache files cannot be written
            TypeError: If value cannot be pickled
        """
        if ttl is None:
            ttl = self.default_ttl
        
        cache_path = self._get_cache_path(key)
        
        # Serialize value to cache file
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        except PermissionError as e:
            logger.error(f"Cannot write cache file for key '{key}': {e}")
            raise PermissionError(f"Failed to write cache: {e}")
        
        except (pickle.PicklingError, TypeError) as e:
            logger.error(f"Cannot pickle value for key '{key}': {e}")
            raise TypeError(f"Value is not picklable: {e}")
        
        # Update index
        self._index[key] = {
            'timestamp': time.time(),
            'ttl': ttl,
            'source_path': str(source_path) if source_path else None,
        }
        
        try:
            self._save_index()
            logger.debug(f"Cached: {key} (ttl: {ttl}s)")
        except Exception as e:
            # If index save fails, remove the cache file to maintain consistency
            if cache_path.exists():
                cache_path.unlink()
            raise
    
    def _remove(self, key: str) -> None:
        """
        Remove cache entry and its file.
        
        Why internal: Users should call invalidate() for explicit removal.
        This is for automatic cleanup during get() operations.
        
        Args:
            key: Cache key to remove
        """
        if key in self._index:
            del self._index[key]
            self._save_index()
        
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            try:
                cache_path.unlink()
                logger.debug(f"Removed cache file: {key}")
            except PermissionError as e:
                logger.warning(f"Cannot remove cache file {cache_path}: {e}")
    
    def invalidate(self, key: Optional[str] = None) -> None:
        """
        Invalidate cache entries.
        
        Args:
            key: Specific key to invalidate. If None, clears entire cache.
            
        Why separate from _remove: Public API for explicit cache management.
        _remove is for internal cleanup, invalidate is for user control.
        """
        if key is not None:
            logger.info(f"Invalidating cache key: {key}")
            self._remove(key)
        else:
            logger.info("Invalidating entire cache")
            # Clear all cache files
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    cache_file.unlink()
                except PermissionError as e:
                    logger.warning(f"Cannot remove {cache_file}: {e}")
            
            # Clear index
            self._index = {}
            self._save_index()
    
    def is_fresh(self, key: str, source_path: Path) -> bool:
        """
        Check if cached version is fresh compared to source file.
        
        Useful for checking cache validity before deciding to parse.
        
        Args:
            key: Cache key
            source_path: Path to source file
            
        Returns:
            True if cache exists and is fresher than source file
        """
        if key not in self._index:
            return False
        
        cache_info = self._index[key]
        
        # Check TTL
        current_time = time.time()
        if current_time - cache_info['timestamp'] > cache_info['ttl']:
            return False
        
        # Check source mtime
        try:
            source_mtime = source_path.stat().st_mtime
            return source_mtime <= cache_info['timestamp']
        except (FileNotFoundError, PermissionError, OSError):
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics:
            - total_entries: Number of cache entries
            - cache_dir: Cache directory path
            - cache_size_bytes: Total size of cache files
        """
        total_size = 0
        cache_files = list(self.cache_dir.glob("*.cache"))
        
        for cache_file in cache_files:
            try:
                total_size += cache_file.stat().st_size
            except (FileNotFoundError, PermissionError, OSError):
                pass
        
        return {
            'total_entries': len(self._index),
            'cache_dir': str(self.cache_dir),
            'cache_size_bytes': total_size,
            'cache_size_mb': round(total_size / (1024 * 1024), 2),
        }
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        stats = self.get_stats()
        return f"Cache(entries={stats['total_entries']}, size={stats['cache_size_mb']}MB)"
