"""
Deployment and Launch Readiness utilities
"""
import logging
import subprocess
import os
from pathlib import Path
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.core.cache import cache
import json

logger = logging.getLogger('ecotrack.deployment')


class HealthChecker:
    """Production readiness health checks"""
    
    @staticmethod
    def run_all_checks():
        """Run all health checks"""
        checks = [
            ('Database Connection', HealthChecker.check_database),
            ('Cache Connection', HealthChecker.check_cache),
            ('Environment Variables', HealthChecker.check_environment),
            ('Static Files', HealthChecker.check_static_files),
            ('Migrations', HealthChecker.check_migrations),
            ('Dependencies', HealthChecker.check_dependencies),
            ('Security Settings', HealthChecker.check_security),
            ('External Services', HealthChecker.check_external_services),
        ]
        
        results = []
        all_passed = True
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                results.append({
                    'name': check_name,
                    'status': 'PASS' if result['success'] else 'FAIL',
                    'message': result['message'],
                    'details': result.get('details', {})
                })
                if not result['success']:
                    all_passed = False
            except Exception as e:
                results.append({
                    'name': check_name,
                    'status': 'ERROR',
                    'message': str(e),
                    'details': {}
                })
                all_passed = False
        
        return {
            'overall_status': 'PASS' if all_passed else 'FAIL',
            'checks': results,
            'timestamp': timezone.now().isoformat()
        }
    
    @staticmethod
    def check_database():
        """Check database connection and readiness"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            return {
                'success': result[0] == 1,
                'message': 'Database connection successful',
                'details': {
                    'engine': settings.DATABASES['default']['ENGINE'],
                    'name': settings.DATABASES['default'].get('NAME', 'N/A')
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Database connection failed: {e}',
                'details': {}
            }
    
    @staticmethod
    def check_cache():
        """Check cache connection"""
        try:
            test_key = 'health_check_test'
            cache.set(test_key, 'test_value', 30)
            value = cache.get(test_key)
            cache.delete(test_key)
            
            return {
                'success': value == 'test_value',
                'message': 'Cache connection successful',
                'details': {
                    'backend': settings.CACHES['default']['BACKEND']
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Cache connection failed: {e}',
                'details': {}
            }
    
    @staticmethod
    def check_environment():
        """Check required environment variables"""
        required_vars = [
            'SECRET_KEY',
            'DATABASE_URL',
            'REDIS_URL',
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            return {
                'success': False,
                'message': f'Missing environment variables: {", ".join(missing_vars)}',
                'details': {'missing': missing_vars}
            }
        
        return {
            'success': True,
            'message': 'All required environment variables present',
            'details': {'checked': required_vars}
        }
    
    @staticmethod
    def check_static_files():
        """Check static files collection"""
        static_root = Path(settings.STATIC_ROOT)
        
        if not static_root.exists():
            return {
                'success': False,
                'message': 'Static files directory does not exist',
                'details': {'static_root': str(static_root)}
            }
        
        # Check for key static files
        key_files = ['admin/css/base.css', 'rest_framework/css/bootstrap.min.css']
        missing_files = []
        
        for file in key_files:
            if not (static_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            return {
                'success': False,
                'message': f'Missing static files: {", ".join(missing_files)}',
                'details': {'missing_files': missing_files}
            }
        
        return {
            'success': True,
            'message': 'Static files properly collected',
            'details': {'static_root': str(static_root)}
        }
    
    @staticmethod
    def check_migrations():
        """Check if all migrations are applied"""
        from django.db.migrations.executor import MigrationExecutor
        
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            return {
                'success': False,
                'message': f'{len(plan)} unapplied migrations found',
                'details': {'unapplied': [f"{migration[0]}.{migration[1]}" for migration in plan]}
            }
        
        return {
            'success': True,
            'message': 'All migrations applied',
            'details': {}
        }
    
    @staticmethod
    def check_dependencies():
        """Check critical dependencies are installed"""
        try:
            import django
            import rest_framework
            import channels
            import celery
            import redis
            
            return {
                'success': True,
                'message': 'All critical dependencies available',
                'details': {
                    'django': django.VERSION,
                    'drf': rest_framework.VERSION,
                }
            }
        except ImportError as e:
            return {
                'success': False,
                'message': f'Missing dependency: {e}',
                'details': {}
            }
    
    @staticmethod
    def check_security():
        """Check security settings"""
        issues = []
        
        if settings.DEBUG:
            issues.append('DEBUG is True')
        
        if settings.SECRET_KEY.startswith('django-insecure'):
            issues.append('Using insecure SECRET_KEY')
        
        if 'localhost' in settings.ALLOWED_HOSTS and not settings.DEBUG:
            issues.append('localhost in ALLOWED_HOSTS for production')
        
        if not hasattr(settings, 'SECURE_SSL_REDIRECT') or not settings.SECURE_SSL_REDIRECT:
            if not settings.DEBUG:
                issues.append('SSL redirect not enabled')
        
        if issues:
            return {
                'success': False,
                'message': f'Security issues found: {", ".join(issues)}',
                'details': {'issues': issues}
            }
        
        return {
            'success': True,
            'message': 'Security settings properly configured',
            'details': {}
        }
    
    @staticmethod
    def check_external_services():
        """Check external service connections"""
        checks = []
        
        # Check AI service
        try:
            if settings.GEMINI_API_KEY:
                # Would test actual connection in real implementation
                checks.append(('AI Service', True, 'API key configured'))
            else:
                checks.append(('AI Service', False, 'API key missing'))
        except:
            checks.append(('AI Service', False, 'Configuration error'))
        
        # Check email service (if configured)
        if hasattr(settings, 'EMAIL_HOST'):
            checks.append(('Email Service', True, 'SMTP configured'))
        else:
            checks.append(('Email Service', False, 'No email configuration'))
        
        failed_checks = [check for check in checks if not check[1]]
        
        return {
            'success': len(failed_checks) == 0,
            'message': f'External services: {len(checks) - len(failed_checks)}/{len(checks)} OK',
            'details': {
                'services': [{'name': name, 'status': 'OK' if status else 'FAIL', 'message': msg} 
                           for name, status, msg in checks]
            }
        }


class DeploymentManager:
    """Manage deployment tasks"""
    
    @staticmethod
    def run_deployment_tasks():
        """Run all deployment tasks"""
        tasks = [
            ('Collect Static Files', DeploymentManager.collect_static),
            ('Run Migrations', DeploymentManager.migrate_database),
            ('Create Superuser', DeploymentManager.create_superuser),
            ('Load Initial Data', DeploymentManager.load_initial_data),
            ('Warm Cache', DeploymentManager.warm_cache),
        ]
        
        results = []
        
        for task_name, task_func in tasks:
            try:
                result = task_func()
                results.append({
                    'task': task_name,
                    'status': 'SUCCESS' if result['success'] else 'FAILED',
                    'message': result['message']
                })
            except Exception as e:
                results.append({
                    'task': task_name,
                    'status': 'ERROR',
                    'message': str(e)
                })
        
        return results
    
    @staticmethod
    def collect_static():
        """Collect static files"""
        try:
            call_command('collectstatic', '--noinput', verbosity=0)
            return {'success': True, 'message': 'Static files collected'}
        except Exception as e:
            return {'success': False, 'message': f'Failed to collect static files: {e}'}
    
    @staticmethod
    def migrate_database():
        """Run database migrations"""
        try:
            call_command('migrate', verbosity=0)
            return {'success': True, 'message': 'Database migrations completed'}
        except Exception as e:
            return {'success': False, 'message': f'Migration failed: {e}'}
    
    @staticmethod
    def create_superuser():
        """Create superuser if needed"""
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            if User.objects.filter(is_superuser=True).exists():
                return {'success': True, 'message': 'Superuser already exists'}
            
            # Create superuser from environment variables
            email = os.environ.get('SUPERUSER_EMAIL')
            password = os.environ.get('SUPERUSER_PASSWORD')
            
            if not email or not password:
                return {'success': True, 'message': 'No superuser credentials provided'}
            
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
            
            return {'success': True, 'message': 'Superuser created'}
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to create superuser: {e}'}
    
    @staticmethod
    def load_initial_data():
        """Load initial data"""
        try:
            from social.services import LeaderboardService, BadgeService
            
            # Create default leaderboards and badges
            LeaderboardService.create_default_leaderboards()
            BadgeService.create_default_badges()
            
            return {'success': True, 'message': 'Initial data loaded'}
        except Exception as e:
            return {'success': False, 'message': f'Failed to load initial data: {e}'}
    
    @staticmethod
    def warm_cache():
        """Warm application cache"""
        try:
            # Warm frequently accessed data
            cache.set('app_startup', timezone.now().isoformat(), 3600)
            
            return {'success': True, 'message': 'Cache warmed'}
        except Exception as e:
            return {'success': False, 'message': f'Failed to warm cache: {e}'}


class BackupManager:
    """Database backup and restore utilities"""
    
    @staticmethod
    def create_backup(backup_name=None):
        """Create database backup"""
        if not backup_name:
            from datetime import datetime
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = Path(settings.BASE_DIR) / 'backups' / f"{backup_name}.sql"
        backup_path.parent.mkdir(exist_ok=True)
        
        try:
            # This is a simplified version - would use actual database tools
            call_command('dumpdata', '--output', str(backup_path), '--format', 'json')
            
            return {
                'success': True,
                'message': f'Backup created: {backup_name}',
                'path': str(backup_path)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Backup failed: {e}',
                'path': None
            }
    
    @staticmethod
    def list_backups():
        """List available backups"""
        backup_dir = Path(settings.BASE_DIR) / 'backups'
        
        if not backup_dir.exists():
            return []
        
        backups = []
        for backup_file in backup_dir.glob('*.sql'):
            stat = backup_file.stat()
            backups.append({
                'name': backup_file.stem,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'path': str(backup_file)
            })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)