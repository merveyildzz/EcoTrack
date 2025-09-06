"""
Metrics collection for EcoTrack monitoring
"""
import time
import psutil
from datetime import datetime, timedelta
from django.db import connection
from django.core.cache import cache
from django.contrib.auth import get_user_model
from activities.models import Activity
from social.models import UserStats, ChallengeParticipation
from carbon.models import CarbonCalculation

User = get_user_model()


class MetricsCollector:
    """Collect system and business metrics"""
    
    @staticmethod
    def get_system_metrics():
        """Get system performance metrics"""
        return {
            'timestamp': time.time(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
        }
    
    @staticmethod
    def get_database_metrics():
        """Get database connection and performance metrics"""
        with connection.cursor() as cursor:
            # Active connections
            cursor.execute("""
                SELECT count(*) 
                FROM information_schema.processlist 
                WHERE db = DATABASE()
            """)
            active_connections = cursor.fetchone()[0]
            
            # Database size (if MySQL/PostgreSQL)
            try:
                cursor.execute("""
                    SELECT 
                        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS db_size_mb
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE()
                """)
                db_size = cursor.fetchone()[0] or 0
            except:
                db_size = 0
            
            return {
                'active_connections': active_connections,
                'database_size_mb': db_size,
                'connection_test': True
            }
    
    @staticmethod
    def get_business_metrics():
        """Get business KPI metrics"""
        now = datetime.now()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        return {
            'total_users': User.objects.count(),
            'active_users_7d': User.objects.filter(last_login__gte=week_ago).count(),
            'active_users_30d': User.objects.filter(last_login__gte=month_ago).count(),
            'total_activities': Activity.objects.count(),
            'activities_today': Activity.objects.filter(created_at__date=today).count(),
            'activities_7d': Activity.objects.filter(created_at__date__gte=week_ago).count(),
            'total_co2_saved': CarbonCalculation.objects.aggregate(
                total=models.Sum('co2_equivalent_kg')
            )['total'] or 0,
            'active_challenges': ChallengeParticipation.objects.filter(
                is_active=True
            ).count(),
            'completed_challenges': ChallengeParticipation.objects.filter(
                is_completed=True
            ).count(),
        }
    
    @staticmethod
    def get_api_metrics():
        """Get API usage metrics from cache"""
        # These would be populated by middleware
        return {
            'requests_per_minute': cache.get('api_requests_per_minute', 0),
            'error_rate': cache.get('api_error_rate', 0),
            'avg_response_time': cache.get('api_avg_response_time', 0),
            'rate_limited_requests': cache.get('rate_limited_requests', 0),
        }
    
    @classmethod
    def collect_all_metrics(cls):
        """Collect all metrics"""
        try:
            return {
                'system': cls.get_system_metrics(),
                'database': cls.get_database_metrics(),
                'business': cls.get_business_metrics(),
                'api': cls.get_api_metrics(),
                'timestamp': time.time(),
                'status': 'healthy'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }


class AlertManager:
    """Handle alerts and notifications"""
    
    THRESHOLDS = {
        'cpu_percent': 80,
        'memory_percent': 85,
        'disk_usage_percent': 90,
        'error_rate': 5,  # 5%
        'response_time': 2000,  # 2 seconds
    }
    
    @staticmethod
    def check_thresholds(metrics):
        """Check if any metrics exceed thresholds"""
        alerts = []
        
        system = metrics.get('system', {})
        api = metrics.get('api', {})
        
        # System alerts
        if system.get('cpu_percent', 0) > AlertManager.THRESHOLDS['cpu_percent']:
            alerts.append({
                'type': 'system',
                'severity': 'warning',
                'message': f"High CPU usage: {system['cpu_percent']}%",
                'timestamp': time.time()
            })
        
        if system.get('memory_percent', 0) > AlertManager.THRESHOLDS['memory_percent']:
            alerts.append({
                'type': 'system',
                'severity': 'warning',
                'message': f"High memory usage: {system['memory_percent']}%",
                'timestamp': time.time()
            })
        
        if system.get('disk_usage_percent', 0) > AlertManager.THRESHOLDS['disk_usage_percent']:
            alerts.append({
                'type': 'system',
                'severity': 'critical',
                'message': f"High disk usage: {system['disk_usage_percent']}%",
                'timestamp': time.time()
            })
        
        # API alerts
        if api.get('error_rate', 0) > AlertManager.THRESHOLDS['error_rate']:
            alerts.append({
                'type': 'api',
                'severity': 'warning',
                'message': f"High API error rate: {api['error_rate']}%",
                'timestamp': time.time()
            })
        
        if api.get('avg_response_time', 0) > AlertManager.THRESHOLDS['response_time']:
            alerts.append({
                'type': 'api',
                'severity': 'warning',
                'message': f"High API response time: {api['avg_response_time']}ms",
                'timestamp': time.time()
            })
        
        return alerts
    
    @staticmethod
    def send_alert(alert):
        """Send alert notification (placeholder for webhook/email/Slack)"""
        # This would integrate with external alerting systems
        # For now, just log the alert
        import logging
        logger = logging.getLogger('ecotrack.security')
        logger.warning(f"ALERT: {alert['message']} (severity: {alert['severity']})")
        
        # Could integrate with:
        # - Slack webhooks
        # - Email notifications
        # - PagerDuty
        # - Discord webhooks
        return True