import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages local data cache and download verification."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def is_cached(self, key: str) -> bool:
        """Check if a key is present in the cache."""
        return (self.cache_dir / key).exists()

    def get_cache_path(self, key: str) -> Path:
        """Get the absolute path to a cached item."""
        return self.cache_dir / key

    def clear_cache(self) -> None:
        """Clear all cached files."""
        for item in self.cache_dir.glob("*"):
            if item.is_file():
                item.unlink()
        logger.info(f"Cleared cache directory: {self.cache_dir}")
