"""
ORC Index Service - Production Ready

Unified façade coordinating ParallelIndexer, Cache, and Config.
Entry point for all indexing operations.

Security: No unsafe operations, validates all inputs.
Architecture: Clean separation of concerns, dependency injection ready.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

try:
    from .config import ORCConfig
    from .cache import Cache
    from .parallel_indexer import ParallelIndexer
except ImportError:
    from config import ORCConfig
    from cache import Cache
    from parallel_indexer import ParallelIndexer

logger = logging.getLogger(__name__)


class IndexService:
    """
    Unified indexing service coordinating all components.
    
    Why façade pattern:
    - Single entry point for CLI and other consumers
    - Hides complexity of coordinating indexer, cache, and config
    - Easier to test (mock the service, not individual components)
    - Clear API contract for consumers
    
    Responsibilities:
    1. Load configuration
    2. Manage caching layer
    3. Orchestrate parallel indexing
    4. Return comprehensive statistics
    """
    
    def __init__(self, config: Optional[ORCConfig] = None, cache: Optional[Cache] = None):
        """
        Initialize index service.
        
        Why optional parameters: Allows dependency injection for testing.
        Production code calls with no args (uses defaults).
        
        Args:
            config: Configuration instance (None = load from default location)
            cache: Cache instance (None = create from config)
            
        Raises:
            ValueError: If configuration is invalid
            PermissionError: If cache directory cannot be created
        """
        # Load or use provided config
        if config is None:
            logger.debug("Loading configuration from default location")
            self.config = ORCConfig()
        else:
            self.config = config
        
        # Create or use provided cache
        if cache is None:
            logger.debug(f"Initializing cache: {self.config.cache_dir}")
            self.cache = Cache(
                cache_dir=self.config.cache_dir,
                default_ttl=self.config.cache_ttl
            )
        else:
            self.cache = cache
        
        logger.info(f"IndexService initialized for project: {self.config.project_root}")
    
    def index_project(self, force_refresh: bool = False, 
                     extensions: Optional[list] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Index entire project with caching.
        
        Why caching: Prevents re-parsing unchanged files (major performance win).
        Why force_refresh: Allows user to rebuild index after config changes.
        
        Process:
        1. Check if cached index exists and is fresh
        2. If cache valid and not force_refresh, return cached data
        3. Otherwise, run parallel indexer
        4. Cache the results
        5. Return index + statistics
        
        Args:
            force_refresh: If True, bypass cache and re-index all files
            extensions: File extensions to index (None = use config defaults)
            
        Returns:
            Tuple of (index_dict, stats_dict)
            - index_dict: Complete code index
            - stats_dict: Indexing statistics
            
        Raises:
            ValueError: If project root is invalid
            PermissionError: If files cannot be accessed
        """
        logger.info(f"Starting project indexing (force_refresh={force_refresh})...")
        
        # Use configured extensions if not specified
        if extensions is None:
            extensions = self.config.file_extensions
        
        # Generate cache key based on project root and extensions
        cache_key = self._generate_cache_key(extensions)
        
        # Check cache unless force refresh
        if not force_refresh:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.info("Using cached index data")
                
                # Cached data is tuple of (index, stats)
                index, stats = cached_data
                stats['cache_hit'] = True
                return index, stats
        
        # Cache miss or force refresh - run indexer
        logger.info("Cache miss or force refresh, running indexer...")
        
        indexer = ParallelIndexer(
            root_path=self.config.project_root,
            ignore_patterns=self.config.ignore_patterns,
            max_workers=self.config.max_workers
        )
        
        index, stats = indexer.index(
            force_refresh=force_refresh,
            extensions=extensions
        )
        
        # Add cache information to stats
        stats['cache_hit'] = False
        stats['cache_key'] = cache_key
        
        # Cache the results (with project root as source path)
        try:
            self.cache.set(
                key=cache_key,
                value=(index, stats),
                ttl=self.config.cache_ttl,
                source_path=self.config.project_root
            )
            logger.debug(f"Cached index data with key: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to cache index data: {e}")
            # Continue anyway - caching is optional optimization
        
        return index, stats
    
    def invalidate_cache(self, cache_key: Optional[str] = None) -> None:
        """
        Invalidate cached index data.
        
        Use cases:
        - After modifying .orcignore
        - After changing configuration
        - Manual cache clear command
        
        Args:
            cache_key: Specific cache key to invalidate (None = clear all)
        """
        if cache_key:
            logger.info(f"Invalidating cache key: {cache_key}")
        else:
            logger.info("Invalidating entire cache")
        
        self.cache.invalidate(cache_key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return self.cache.get_stats()
    
    def _generate_cache_key(self, extensions: list) -> str:
        """
        Generate cache key for index data.
        
        Why include extensions: Different extension sets = different index.
        Why include root: Multi-project support (different roots, different caches).
        
        Args:
            extensions: File extensions being indexed
            
        Returns:
            Cache key string
        """
        # Include project root and extensions in key
        root_str = str(self.config.project_root)
        ext_str = ','.join(sorted(extensions))
        return f"index:{root_str}:{ext_str}"
    
    def is_cache_fresh(self, extensions: Optional[list] = None) -> bool:
        """
        Check if cached index is still fresh.
        
        Useful for CLI to show cache status before indexing.
        
        Args:
            extensions: File extensions to check (None = use config defaults)
            
        Returns:
            True if cache exists and is fresh
        """
        if extensions is None:
            extensions = self.config.file_extensions
        
        cache_key = self._generate_cache_key(extensions)
        return self.cache.is_fresh(cache_key, self.config.project_root)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get configuration summary for display/debugging.
        
        Returns:
            Dictionary with configuration values
        """
        return {
            'project_root': str(self.config.project_root),
            'cache_dir': str(self.config.cache_dir),
            'cache_ttl': self.config.cache_ttl,
            'max_workers': self.config.max_workers,
            'ignore_patterns_count': len(self.config.ignore_patterns),
            'file_extensions': self.config.file_extensions,
            'log_level': self.config.log_level,
        }
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"IndexService(project={self.config.project_root})"


def create_index_service(config_path: Optional[Path] = None) -> IndexService:
    """
    Factory function to create IndexService with configuration.
    
    Convenience function for simple use cases.
    
    Args:
        config_path: Path to config YAML file (None = use defaults)
        
    Returns:
        IndexService instance
        
    Raises:
        ValueError: If configuration is invalid
        PermissionError: If required directories cannot be created
    """
    config = ORCConfig(config_path=config_path)
    return IndexService(config=config)
