"""
Security utilities for EcoTrack
"""
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger('ecotrack.security')


class SecurityUtils:
    """Security utilities and helpers"""
    
    @staticmethod
    def hash_email_for_privacy(email):
        """Hash email for privacy-compliant logging"""
        if not email:
            return 'anonymous'
        
        # Use SHA-256 with salt for consistent but private logging
        salt = settings.SECRET_KEY[:16]
        return hashlib.sha256((email + salt).encode()).hexdigest()[:16]
    
    @staticmethod
    def generate_audit_token():
        """Generate cryptographically secure audit token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def log_security_event(event_type, user=None, details=None, ip_address=None):
        """Log security-relevant events"""
        event_data = {
            'event_type': event_type,
            'timestamp': timezone.now().isoformat(),
            'user_id': user.id if user else None,
            'user_email_hash': SecurityUtils.hash_email_for_privacy(
                user.email if user else None
            ),
            'ip_address': ip_address,
            'details': details or {},
            'audit_token': SecurityUtils.generate_audit_token()
        }
        
        logger.warning(f"SECURITY_EVENT: {event_data}")
        
        # Store in cache for recent events dashboard
        cache_key = f"security_events:{timezone.now().strftime('%Y%m%d')}"
        events = cache.get(cache_key, [])
        events.append(event_data)
        # Keep only last 100 events per day
        if len(events) > 100:
            events = events[-100:]
        cache.set(cache_key, events, 86400)  # 24 hours
        
        return event_data
    
    @staticmethod
    def check_suspicious_activity(user, request):
        """Check for suspicious user activity patterns"""
        if not user or not user.is_authenticated:
            return False
        
        # Check for rapid successive logins from different IPs
        cache_key = f"login_ips:{user.id}"
        recent_ips = cache.get(cache_key, set())
        current_ip = SecurityUtils.get_client_ip(request)
        
        if len(recent_ips) > 3:  # More than 3 different IPs in short time
            SecurityUtils.log_security_event(
                'suspicious_multi_ip_access',
                user=user,
                details={'ip_count': len(recent_ips), 'current_ip': current_ip},
                ip_address=current_ip
            )
            return True
        
        # Add current IP to recent set
        recent_ips.add(current_ip)
        cache.set(cache_key, recent_ips, 3600)  # 1 hour window
        
        return False
    
    @staticmethod
    def get_client_ip(request):
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DataPrivacyManager:
    """Handle data privacy and GDPR compliance"""
    
    @staticmethod
    def anonymize_user_data(user_id):
        """Anonymize user data for GDPR compliance"""
        try:
            user = User.objects.get(id=user_id)
            
            # Log the anonymization request
            SecurityUtils.log_security_event(
                'data_anonymization',
                user=user,
                details={'reason': 'user_request'}
            )
            
            # Anonymize user data
            anonymous_email = f"anonymous_{secrets.token_hex(8)}@deleted.local"
            user.email = anonymous_email
            user.first_name = "Anonymous"
            user.last_name = "User"
            user.is_active = False
            user.save()
            
            # Keep activity data but remove PII
            from activities.models import Activity
            Activity.objects.filter(user=user).update(
                location_name='Anonymized',
                latitude=None,
                longitude=None,
                notes='Data anonymized upon user request'
            )
            
            logger.info(f"User data anonymized for user ID: {user_id}")
            return True
            
        except User.DoesNotExist:
            logger.error(f"Attempted to anonymize non-existent user ID: {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error anonymizing user data: {e}")
            return False
    
    @staticmethod
    def export_user_data(user_id):
        """Export all user data for GDPR compliance"""
        try:
            user = User.objects.get(id=user_id)
            
            # Log the export request
            SecurityUtils.log_security_event(
                'data_export',
                user=user,
                details={'reason': 'user_request'}
            )
            
            # Collect user data
            user_data = {
                'profile': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'date_joined': user.date_joined.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                },
                'activities': [],
                'social_stats': {},
                'challenges': []
            }
            
            # Get activities
            from activities.models import Activity
            activities = Activity.objects.filter(user=user)
            for activity in activities:
                user_data['activities'].append({
                    'id': str(activity.id),
                    'category': activity.category.name,
                    'activity_type': activity.activity_type,
                    'value': float(activity.value),
                    'unit': activity.unit,
                    'start_timestamp': activity.start_timestamp.isoformat(),
                    'location_name': activity.location_name,
                    'co2_kg': float(activity.co2_kg) if activity.co2_kg else None,
                    'created_at': activity.created_at.isoformat(),
                })
            
            # Get social stats
            try:
                from social.models import UserStats
                stats = UserStats.objects.get(user=user)
                user_data['social_stats'] = {
                    'total_activities': stats.total_activities,
                    'total_co2_saved': stats.total_co2_saved,
                    'current_streak': stats.current_streak,
                    'longest_streak': stats.longest_streak,
                    'badges_earned': stats.badges_earned,
                    'challenges_completed': stats.challenges_completed,
                }
            except UserStats.DoesNotExist:
                pass
            
            return user_data
            
        except User.DoesNotExist:
            logger.error(f"Attempted to export data for non-existent user ID: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            return None


class InputSanitizer:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_string(value, max_length=255):
        """Sanitize string input"""
        if not isinstance(value, str):
            return str(value)
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n\r')
        
        # Truncate to max length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_email(email):
        """Sanitize email address"""
        if not email:
            return None
        
        email = SecurityUtils.sanitize_string(email, 254).lower()
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return None
        
        return email
    
    @staticmethod
    def sanitize_location_name(location):
        """Sanitize location name input"""
        if not location:
            return None
        
        # Remove potentially dangerous characters
        sanitized = SecurityUtils.sanitize_string(location, 200)
        
        # Remove HTML-like tags
        import re
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        return sanitized if sanitized else None