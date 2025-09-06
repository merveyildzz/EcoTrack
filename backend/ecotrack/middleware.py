"""
Security and monitoring middleware for EcoTrack
"""
import time
import logging
import json
from django.http import JsonResponse
from django.conf import settings
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('ecotrack.security')
api_logger = logging.getLogger('ecotrack.api')


class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # CSP for API responses
        if request.path.startswith('/api/'):
            response['Content-Security-Policy'] = "default-src 'none'; frame-ancestors 'none';"
        
        return response


class RateLimitMiddleware:
    """Rate limiting middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip rate limiting for certain paths
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return self.get_response(request)
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Different limits for different endpoints
        if request.path.startswith('/api/v1/auth/'):
            limit = 5  # 5 requests per minute for auth
            window = 60
        elif request.path.startswith('/api/'):
            limit = 100  # 100 requests per minute for API
            window = 60
        else:
            limit = 200  # 200 requests per minute for general
            window = 60
        
        # Check rate limit
        cache_key = f"rate_limit:{client_ip}:{request.path_info}"
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= limit:
            logger.warning(f"Rate limit exceeded for IP {client_ip} on path {request.path}")
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'retry_after': window
            }, status=429)
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, window)
        
        response = self.get_response(request)
        
        # Add rate limit headers
        response['X-RateLimit-Limit'] = str(limit)
        response['X-RateLimit-Remaining'] = str(max(0, limit - current_requests - 1))
        
        return response
    
    def get_client_ip(self, request):
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APILoggingMiddleware:
    """Log all API requests and responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip logging for non-API requests
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        start_time = time.time()
        
        # Log request
        request_data = {
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous',
            'ip': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'timestamp': time.time()
        }
        
        response = self.get_response(request)
        
        # Log response
        end_time = time.time()
        response_data = {
            **request_data,
            'status_code': response.status_code,
            'response_time_ms': round((end_time - start_time) * 1000, 2),
            'response_size': len(response.content) if hasattr(response, 'content') else 0
        }
        
        # Log level based on status code
        if response.status_code >= 500:
            api_logger.error(json.dumps(response_data))
        elif response.status_code >= 400:
            api_logger.warning(json.dumps(response_data))
        else:
            api_logger.info(json.dumps(response_data))
        
        return response
    
    def get_client_ip(self, request):
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class HealthCheckMiddleware:
    """Health check endpoint middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/health/':
            try:
                # Basic health checks
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                
                # Check cache
                cache.set('health_check', 'ok', 10)
                cache_status = cache.get('health_check') == 'ok'
                
                health_data = {
                    'status': 'healthy',
                    'timestamp': time.time(),
                    'database': 'ok',
                    'cache': 'ok' if cache_status else 'error',
                    'version': settings.VERSION if hasattr(settings, 'VERSION') else '1.0.0'
                }
                
                return JsonResponse(health_data)
                
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return JsonResponse({
                    'status': 'unhealthy',
                    'timestamp': time.time(),
                    'error': str(e)
                }, status=503)
        
        return self.get_response(request)