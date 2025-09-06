"""
Monitoring and observability API endpoints
"""
import json
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .metrics import MetricsCollector, AlertManager


@api_view(['GET'])
@permission_classes([IsAdminUser])
def metrics_endpoint(request):
    """
    Get system metrics (admin only)
    """
    metrics = MetricsCollector.collect_all_metrics()
    
    # Check for alerts
    alerts = AlertManager.check_thresholds(metrics)
    if alerts:
        metrics['alerts'] = alerts
    
    return Response(metrics)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def health_detailed(request):
    """
    Detailed health check (admin only)
    """
    try:
        from django.db import connection
        from django.core.cache import cache
        import time
        
        # Database check
        with connection.cursor() as cursor:
            start_time = time.time()
            cursor.execute("SELECT 1")
            db_response_time = (time.time() - start_time) * 1000
        
        # Cache check
        start_time = time.time()
        cache.set('health_test', 'ok', 60)
        cache_result = cache.get('health_test')
        cache_response_time = (time.time() - start_time) * 1000
        
        # Get basic metrics
        system_metrics = MetricsCollector.get_system_metrics()
        business_metrics = MetricsCollector.get_business_metrics()
        
        health_data = {
            'status': 'healthy',
            'timestamp': time.time(),
            'checks': {
                'database': {
                    'status': 'ok',
                    'response_time_ms': round(db_response_time, 2)
                },
                'cache': {
                    'status': 'ok' if cache_result == 'ok' else 'error',
                    'response_time_ms': round(cache_response_time, 2)
                }
            },
            'system': system_metrics,
            'business': business_metrics
        }
        
        return Response(health_data)
        
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'timestamp': time.time(),
            'error': str(e)
        }, status=503)


@staff_member_required
@cache_page(60)  # Cache for 1 minute
def dashboard_metrics(request):
    """
    Dashboard metrics for admin interface
    """
    metrics = MetricsCollector.collect_all_metrics()
    
    # Format for dashboard display
    dashboard_data = {
        'summary': {
            'total_users': metrics['business']['total_users'],
            'active_users_30d': metrics['business']['active_users_30d'],
            'total_activities': metrics['business']['total_activities'],
            'activities_today': metrics['business']['activities_today'],
            'total_co2_saved': round(metrics['business']['total_co2_saved'], 2),
        },
        'system': {
            'cpu_usage': metrics['system']['cpu_percent'],
            'memory_usage': metrics['system']['memory_percent'],
            'disk_usage': metrics['system']['disk_usage_percent'],
        },
        'api': metrics['api'],
        'timestamp': metrics['timestamp']
    }
    
    return JsonResponse(dashboard_data)


@require_http_methods(["GET"])
def uptime_check(request):
    """
    Simple uptime check endpoint (no auth required)
    """
    return JsonResponse({
        'status': 'ok',
        'timestamp': time.time()
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def trigger_alert_test(request):
    """
    Test alert system (admin only)
    """
    test_alert = {
        'type': 'test',
        'severity': 'info',
        'message': 'Test alert triggered manually',
        'timestamp': time.time()
    }
    
    AlertManager.send_alert(test_alert)
    
    return Response({
        'message': 'Test alert sent successfully',
        'alert': test_alert
    })