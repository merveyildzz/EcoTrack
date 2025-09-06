"""
Performance optimization utilities for EcoTrack
"""
import time
from functools import wraps
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('ecotrack.performance')


def cache_result(timeout=300, key_prefix="cache"):
    """
    Decorator to cache function results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return result
            
            # Execute function and cache result
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            cache.set(cache_key, result, timeout)
            logger.debug(f"Cache miss for {func.__name__}, execution time: {execution_time:.2f}s")
            
            return result
        return wrapper
    return decorator


def performance_monitor(threshold=1.0):
    """
    Decorator to monitor function performance
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > threshold:
                    logger.warning(f"Slow execution: {func.__name__} took {execution_time:.2f}s")
                
                # Update performance metrics in cache
                perf_key = f"performance:{func.__name__}"
                current_metrics = cache.get(perf_key, {'count': 0, 'total_time': 0, 'max_time': 0})
                current_metrics['count'] += 1
                current_metrics['total_time'] += execution_time
                current_metrics['max_time'] = max(current_metrics['max_time'], execution_time)
                cache.set(perf_key, current_metrics, 3600)  # 1 hour
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Error in {func.__name__} after {execution_time:.2f}s: {e}")
                raise
        return wrapper
    return decorator


class QueryOptimizer:
    """
    Database query optimization utilities
    """
    
    @staticmethod
    def optimize_activity_queries():
        """
        Create database indexes for optimal activity queries
        """
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Index for user activity queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activities_user_created 
                ON activities_activity(user_id, created_at DESC)
            """)
            
            # Index for date range queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activities_date_range 
                ON activities_activity(created_at, user_id) 
                WHERE created_at >= NOW() - INTERVAL 30 DAY
            """)
            
            # Index for carbon calculations
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_carbon_activity_user 
                ON carbon_carboncalculation(activity_id, user_id)
            """)
            
            logger.info("Activity query indexes created/verified")
    
    @staticmethod
    def get_slow_queries():
        """
        Get information about slow queries (PostgreSQL specific)
        """
        from django.db import connection
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT query, calls, total_time, mean_time 
                    FROM pg_stat_statements 
                    ORDER BY total_time DESC 
                    LIMIT 10
                """)
                return cursor.fetchall()
        except:
            # Not PostgreSQL or pg_stat_statements not enabled
            return []


class CacheManager:
    """
    Advanced caching management
    """
    
    CACHE_KEYS = {
        'user_stats': 'user_stats:{user_id}',
        'leaderboard': 'leaderboard:{type}:{period}',
        'dashboard_data': 'dashboard:{user_id}:{date}',
        'activity_summary': 'activity_summary:{user_id}:{period}',
        'carbon_insights': 'carbon_insights:{user_id}',
    }
    
    @classmethod
    def get_user_stats(cls, user_id, use_cache=True):
        """
        Get cached user stats with fallback
        """
        if not use_cache:
            return cls._compute_user_stats(user_id)
        
        cache_key = cls.CACHE_KEYS['user_stats'].format(user_id=user_id)
        stats = cache.get(cache_key)
        
        if stats is None:
            stats = cls._compute_user_stats(user_id)
            # Cache for 30 minutes
            cache.set(cache_key, stats, 1800)
        
        return stats
    
    @classmethod
    def invalidate_user_cache(cls, user_id):
        """
        Invalidate all cache entries for a user
        """
        patterns = [
            cls.CACHE_KEYS['user_stats'].format(user_id=user_id),
            cls.CACHE_KEYS['dashboard_data'].format(user_id=user_id, date='*'),
            cls.CACHE_KEYS['activity_summary'].format(user_id=user_id, period='*'),
            cls.CACHE_KEYS['carbon_insights'].format(user_id=user_id),
        ]
        
        for pattern in patterns:
            if '*' in pattern:
                # For wildcard patterns, would need Redis SCAN
                # For now, just delete specific common keys
                for period in ['daily', 'weekly', 'monthly']:
                    specific_key = pattern.replace('*', period)
                    cache.delete(specific_key)
            else:
                cache.delete(pattern)
    
    @staticmethod
    def _compute_user_stats(user_id):
        """
        Compute user statistics from database
        """
        from social.services import SocialService
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            return SocialService.update_user_stats(user)
        except User.DoesNotExist:
            return None
    
    @classmethod
    def warm_cache(cls, user_id):
        """
        Pre-populate cache for a user
        """
        # Get user stats
        cls.get_user_stats(user_id, use_cache=False)
        
        # Pre-calculate common dashboard queries
        today = timezone.now().date()
        cls.get_dashboard_data(user_id, today)
        
        logger.info(f"Cache warmed for user {user_id}")
    
    @classmethod
    def get_dashboard_data(cls, user_id, date):
        """
        Get cached dashboard data
        """
        cache_key = cls.CACHE_KEYS['dashboard_data'].format(
            user_id=user_id, 
            date=date.strftime('%Y-%m-%d')
        )
        
        data = cache.get(cache_key)
        if data is None:
            data = cls._compute_dashboard_data(user_id, date)
            # Cache for 1 hour
            cache.set(cache_key, data, 3600)
        
        return data
    
    @staticmethod
    def _compute_dashboard_data(user_id, date):
        """
        Compute dashboard data for a specific date
        """
        from activities.models import Activity
        from carbon.models import CarbonCalculation
        
        # Get activities for the date
        activities = Activity.objects.filter(
            user_id=user_id,
            created_at__date=date
        ).select_related('category')
        
        # Get carbon calculations
        carbon_data = CarbonCalculation.objects.filter(
            activity__user_id=user_id,
            activity__created_at__date=date
        ).aggregate(
            total_co2=models.Sum('co2_equivalent_kg'),
            total_saved=models.Sum('co2_saved_kg')
        )
        
        return {
            'activities_count': activities.count(),
            'total_co2': carbon_data['total_co2'] or 0,
            'co2_saved': carbon_data['total_saved'] or 0,
            'categories': list(activities.values_list('category__name', flat=True).distinct()),
            'date': date.isoformat()
        }


class BackgroundTaskOptimizer:
    """
    Optimize background tasks and batch operations
    """
    
    @staticmethod
    def batch_update_user_stats(batch_size=100):
        """
        Update user stats in batches
        """
        from django.contrib.auth import get_user_model
        from social.services import SocialService
        
        User = get_user_model()
        
        # Get users who need stats updates
        cutoff_time = timezone.now() - timedelta(hours=24)
        users_to_update = User.objects.filter(
            models.Q(social_stats__last_updated__lt=cutoff_time) |
            models.Q(social_stats__isnull=True)
        ).values_list('id', flat=True)
        
        updated_count = 0
        for i in range(0, len(users_to_update), batch_size):
            batch = users_to_update[i:i+batch_size]
            
            for user_id in batch:
                try:
                    user = User.objects.get(id=user_id)
                    SocialService.update_user_stats(user)
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Failed to update stats for user {user_id}: {e}")
        
        logger.info(f"Updated stats for {updated_count} users")
        return updated_count
    
    @staticmethod
    def cleanup_old_data():
        """
        Clean up old data to maintain performance
        """
        from social.models import SocialFeed
        from activities.models import Activity
        
        # Remove old social feed entries (keep last 90 days)
        cutoff_date = timezone.now() - timedelta(days=90)
        old_feed_count = SocialFeed.objects.filter(created_at__lt=cutoff_date).count()
        SocialFeed.objects.filter(created_at__lt=cutoff_date).delete()
        
        # Archive old activities (keep last 2 years)
        archive_cutoff = timezone.now() - timedelta(days=730)
        old_activities = Activity.objects.filter(created_at__lt=archive_cutoff)
        old_activity_count = old_activities.count()
        
        # In a real scenario, you'd move these to an archive table
        # For now, just log what would be archived
        logger.info(f"Would archive {old_activity_count} old activities")
        
        logger.info(f"Cleanup completed: removed {old_feed_count} old feed entries")
        
        return {
            'feed_entries_removed': old_feed_count,
            'activities_to_archive': old_activity_count
        }