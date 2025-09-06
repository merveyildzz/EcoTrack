"""
Django management command for performance optimization
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import connection
from ecotrack.performance import QueryOptimizer, BackgroundTaskOptimizer, CacheManager


class Command(BaseCommand):
    help = 'Run performance optimization tasks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--task',
            type=str,
            choices=['indexes', 'cache-warm', 'cleanup', 'stats-update', 'all'],
            default='all',
            help='Specific optimization task to run'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Batch size for bulk operations'
        )
    
    def handle(self, *args, **options):
        task = options['task']
        batch_size = options['batch_size']
        
        if task in ['indexes', 'all']:
            self.stdout.write('Creating/updating database indexes...')
            QueryOptimizer.optimize_activity_queries()
            self.stdout.write(self.style.SUCCESS('✓ Database indexes optimized'))
        
        if task in ['cache-warm', 'all']:
            self.stdout.write('Warming cache for active users...')
            self.warm_cache_for_active_users()
            self.stdout.write(self.style.SUCCESS('✓ Cache warmed for active users'))
        
        if task in ['stats-update', 'all']:
            self.stdout.write('Updating user statistics...')
            updated = BackgroundTaskOptimizer.batch_update_user_stats(batch_size)
            self.stdout.write(self.style.SUCCESS(f'✓ Updated stats for {updated} users'))
        
        if task in ['cleanup', 'all']:
            self.stdout.write('Cleaning up old data...')
            results = BackgroundTaskOptimizer.cleanup_old_data()
            self.stdout.write(self.style.SUCCESS(
                f'✓ Cleanup completed: {results["feed_entries_removed"]} entries removed'
            ))
        
        if task == 'all':
            self.stdout.write(self.style.SUCCESS('\n🚀 All performance optimization tasks completed!'))
    
    def warm_cache_for_active_users(self):
        """Warm cache for recently active users"""
        from django.contrib.auth import get_user_model
        from datetime import timedelta
        from django.utils import timezone
        
        User = get_user_model()
        
        # Get users active in last 7 days
        cutoff = timezone.now() - timedelta(days=7)
        active_users = User.objects.filter(
            last_login__gte=cutoff
        ).values_list('id', flat=True)[:100]  # Limit to 100 most active
        
        for user_id in active_users:
            try:
                CacheManager.warm_cache(user_id)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Failed to warm cache for user {user_id}: {e}')
                )
        
        return len(active_users)