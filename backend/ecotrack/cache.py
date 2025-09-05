"""
Advanced caching layer for EcoTrack
Implements Redis-based caching with smart invalidation
"""
import json
from functools import wraps
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import hashlib


class CacheManager:
    """Advanced cache management with tagging and smart invalidation"""
    
    # Cache timeouts (in seconds)
    TIMEOUTS = {
        'user_stats': 3600,        # 1 hour
        'leaderboards': 1800,      # 30 minutes  
        'activities': 300,         # 5 minutes
        'dashboard': 900,          # 15 minutes
        'badges': 7200,           # 2 hours
        'challenges': 600,         # 10 minutes
        'co2_calculations': 86400, # 24 hours
    }
    
    @classmethod
    def get_cache_key(cls, category, identifier, **kwargs):
        """Generate consistent cache keys"""
        key_parts = [category, str(identifier)]
        
        # Add additional parameters to key
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
            
        key = ":".join(key_parts)
        
        # Hash long keys to avoid Redis key length limits
        if len(key) > 200:
            key = hashlib.md5(key.encode()).hexdigest()
            
        return f"ecotrack:{key}"
    
    @classmethod
    def cache_user_data(cls, user_id, data_type, data, timeout=None):
        """Cache user-specific data with automatic timeout"""
        if timeout is None:
            timeout = cls.TIMEOUTS.get(data_type, 300)
            
        key = cls.get_cache_key(data_type, f"user:{user_id}")
        cache.set(key, data, timeout)
        
        # Also cache by tag for bulk invalidation
        tag_key = cls.get_cache_key('tags', data_type)
        tagged_keys = cache.get(tag_key, [])
        if key not in tagged_keys:
            tagged_keys.append(key)
            cache.set(tag_key, tagged_keys, timeout * 2)
    
    @classmethod
    def get_user_data(cls, user_id, data_type):
        """Retrieve user-specific cached data"""
        key = cls.get_cache_key(data_type, f"user:{user_id}")
        return cache.get(key)
    
    @classmethod
    def invalidate_user_cache(cls, user_id, data_types=None):
        """Invalidate cache for specific user"""
        if data_types is None:
            data_types = cls.TIMEOUTS.keys()
            
        for data_type in data_types:
            key = cls.get_cache_key(data_type, f"user:{user_id}")
            cache.delete(key)
    
    @classmethod
    def invalidate_by_tag(cls, tag):
        """Invalidate all keys associated with a tag"""
        tag_key = cls.get_cache_key('tags', tag)
        tagged_keys = cache.get(tag_key, [])
        
        if tagged_keys:
            cache.delete_many(tagged_keys)
            cache.delete(tag_key)


def cached_method(timeout=300, key_prefix="method"):
    """
    Decorator for caching method results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key_parts = [key_prefix, func.__name__]
            
            # Add positional args (skip self/cls)
            for arg in args[1:]:  # Skip self/cls
                if hasattr(arg, 'id'):
                    cache_key_parts.append(str(arg.id))
                else:
                    cache_key_parts.append(str(arg))
            
            # Add keyword args
            for k, v in sorted(kwargs.items()):
                cache_key_parts.append(f"{k}:{v}")
                
            cache_key = CacheManager.get_cache_key("method", ":".join(cache_key_parts))
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def cache_leaderboard(timeout=1800):
    """Specific caching for leaderboard data"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key based on leaderboard parameters
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args[1:])  # Skip self
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            
            cache_key = CacheManager.get_cache_key("leaderboard", ":".join(key_parts))
            
            # Try cache first
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Generate and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            # Tag for bulk invalidation
            CacheManager.cache_user_data("global", "leaderboards", result, timeout)
            
            return result
        return wrapper
    return decorator


class ActivityCacheInvalidator:
    """Handles cache invalidation when activities change"""
    
    @classmethod
    def on_activity_created(cls, user_id):
        """Invalidate relevant caches when new activity is created"""
        CacheManager.invalidate_user_cache(user_id, [
            'user_stats', 'dashboard', 'activities'
        ])
        # Invalidate global caches
        CacheManager.invalidate_by_tag('leaderboards')
    
    @classmethod  
    def on_activity_updated(cls, user_id):
        """Invalidate caches when activity is updated"""
        cls.on_activity_created(user_id)  # Same invalidation pattern
    
    @classmethod
    def on_activity_deleted(cls, user_id):
        """Invalidate caches when activity is deleted"""
        cls.on_activity_created(user_id)  # Same invalidation pattern


# Convenience functions for common caching patterns
def cache_user_dashboard(user_id, data, timeout=900):
    """Cache user dashboard data"""
    CacheManager.cache_user_data(user_id, 'dashboard', data, timeout)

def get_user_dashboard(user_id):
    """Get cached user dashboard data"""
    return CacheManager.get_user_data(user_id, 'dashboard')

def cache_user_stats(user_id, stats, timeout=3600):
    """Cache user statistics"""
    CacheManager.cache_user_data(user_id, 'user_stats', stats, timeout)

def get_user_stats(user_id):
    """Get cached user statistics"""
    return CacheManager.get_user_data(user_id, 'user_stats')