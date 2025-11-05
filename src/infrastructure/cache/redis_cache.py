"""
Redis cache implementation for caching responses and session data
"""

from typing import Optional, Any
import json
import redis
from redis.exceptions import RedisError

from src.config import settings
from src.config.logging import get_logger

logger = get_logger(__name__)


class RedisCache:
    """Redis cache manager"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self.enabled = settings.enable_cache
        self.ttl = settings.cache_ttl
        self.client: Optional[redis.Redis] = None
        
        if self.enabled:
            try:
                self.client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                # Test connection
                self.client.ping()
                logger.info(f"Redis cache connected: {settings.redis_url}")
            except (RedisError, Exception) as e:
                logger.warning(f"Redis unavailable, caching disabled: {e}")
                self.enabled = False
                self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled or not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        nx: bool = False
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: settings.cache_ttl)
            nx: Only set if key doesn't exist
            
        Returns:
            True if set successfully
        """
        if not self.enabled or not self.client:
            return False
        
        try:
            ttl = ttl or self.ttl
            serialized = json.dumps(value)
            
            if nx:
                result = self.client.set(key, serialized, ex=ttl, nx=True)
            else:
                result = self.client.set(key, serialized, ex=ttl)
            
            return bool(result)
        except (RedisError, TypeError) as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled or not self.client:
            return False
        
        try:
            return bool(self.client.delete(key))
        except RedisError as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled or not self.client:
            return False
        
        try:
            return bool(self.client.exists(key))
        except RedisError as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache (use with caution!)"""
        if not self.enabled or not self.client:
            return False
        
        try:
            self.client.flushdb()
            logger.warning("Cache cleared")
            return True
        except RedisError as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache"""
        if not self.enabled or not self.client:
            return None
        
        try:
            return self.client.incrby(key, amount)
        except RedisError as e:
            logger.error(f"Cache increment error for key '{key}': {e}")
            return None
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled or not self.client:
            return {"enabled": False}
        
        try:
            info = self.client.info("stats")
            return {
                "enabled": True,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "keys": self.client.dbsize(),
            }
        except RedisError as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"enabled": True, "error": str(e)}


# Global cache instance
cache = RedisCache()


def get_cache() -> RedisCache:
    """Get cache instance (for dependency injection)"""
    return cache

