"""
Real-time notification system for EcoTrack
Handles push notifications, in-app notifications, and email alerts
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Notification, NotificationPreference, NotificationTemplate
from social.models import UserStats, Challenge, ChallengeParticipation

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """Central service for managing all types of notifications"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def send_notification(self, user, notification_type, title, message, 
                         data=None, channels=None, priority='normal'):
        """
        Send notification through multiple channels
        
        Args:
            user: Target user
            notification_type: Type of notification (badge_earned, challenge_complete, etc.)
            title: Notification title
            message: Notification message
            data: Additional data payload
            channels: List of channels ['push', 'email', 'in_app', 'websocket']
            priority: Priority level ('low', 'normal', 'high', 'urgent')
        """
        # Check user preferences
        preferences = self._get_user_preferences(user, notification_type)
        if not preferences.enabled:
            logger.info(f"Notification {notification_type} disabled for user {user.id}")
            return
        
        # Default channels based on notification type
        if channels is None:
            channels = self._get_default_channels(notification_type)
        
        # Create notification record
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data or {},
            priority=priority,
            channels=channels
        )
        
        # Send through each channel
        results = {}
        
        if 'in_app' in channels:
            results['in_app'] = self._send_in_app_notification(notification)
        
        if 'websocket' in channels:
            results['websocket'] = self._send_websocket_notification(notification)
        
        if 'push' in channels and preferences.push_enabled:
            results['push'] = self._send_push_notification(notification)
        
        if 'email' in channels and preferences.email_enabled:
            results['email'] = self._send_email_notification(notification)
        
        # Update notification with delivery status
        notification.delivery_status = results
        notification.save()
        
        return notification
    
    def send_achievement_notification(self, user, badge):
        """Send notification when user earns a badge"""
        return self.send_notification(
            user=user,
            notification_type='badge_earned',
            title='🏆 Achievement Unlocked!',
            message=f'Congratulations! You earned the "{badge.name}" badge!',
            data={
                'badge_id': str(badge.id),
                'badge_name': badge.name,
                'points': badge.points,
                'rarity': badge.rarity
            },
            channels=['in_app', 'websocket', 'push'],
            priority='high'
        )
    
    def send_challenge_notification(self, user, challenge, notification_type='challenge_reminder'):
        """Send challenge-related notifications"""
        messages = {
            'challenge_reminder': f"Don't forget about the '{challenge.title}' challenge!",
            'challenge_complete': f"🎉 Congratulations! You completed '{challenge.title}'!",
            'challenge_deadline': f"⏰ Only 24 hours left for '{challenge.title}'!",
        }
        
        titles = {
            'challenge_reminder': '🎯 Challenge Reminder',
            'challenge_complete': '🏆 Challenge Complete!',
            'challenge_deadline': '⏰ Challenge Deadline',
        }
        
        return self.send_notification(
            user=user,
            notification_type=notification_type,
            title=titles.get(notification_type, '🎯 Challenge Update'),
            message=messages.get(notification_type, 'Challenge update available'),
            data={
                'challenge_id': str(challenge.id),
                'challenge_title': challenge.title,
                'challenge_type': challenge.challenge_type
            },
            channels=['in_app', 'websocket', 'push'] if notification_type != 'challenge_reminder' else ['in_app'],
            priority='high' if notification_type == 'challenge_complete' else 'normal'
        )
    
    def send_milestone_notification(self, user, milestone_type, milestone_data):
        """Send milestone achievement notifications"""
        milestone_messages = {
            'first_week': "🎉 Congratulations on completing your first week of tracking!",
            'co2_milestone': f"🌱 Amazing! You've saved {milestone_data.get('co2_saved', 0)}kg of CO₂!",
            'streak_milestone': f"🔥 Incredible! You're on a {milestone_data.get('streak_days', 0)}-day streak!",
            'activity_milestone': f"📊 Fantastic! You've logged {milestone_data.get('activity_count', 0)} activities!"
        }
        
        return self.send_notification(
            user=user,
            notification_type='milestone_reached',
            title='🎉 Milestone Reached!',
            message=milestone_messages.get(milestone_type, 'You reached a new milestone!'),
            data=milestone_data,
            channels=['in_app', 'websocket', 'push'],
            priority='high'
        )
    
    def send_leaderboard_notification(self, user, rank, leaderboard_name):
        """Send leaderboard ranking notifications"""
        if rank <= 3:
            emoji = ['🥇', '🥈', '🥉'][rank - 1]
            title = f'{emoji} Top 3!'
            message = f"You're #{rank} on the {leaderboard_name} leaderboard!"
            priority = 'high'
        elif rank <= 10:
            title = '🏅 Top 10!'
            message = f"You made it to #{rank} on the {leaderboard_name} leaderboard!"
            priority = 'normal'
        else:
            return  # Don't notify for ranks below 10
        
        return self.send_notification(
            user=user,
            notification_type='leaderboard_rank',
            title=title,
            message=message,
            data={
                'rank': rank,
                'leaderboard': leaderboard_name
            },
            channels=['in_app', 'websocket', 'push'],
            priority=priority
        )
    
    def send_weekly_summary(self, user, summary_data):
        """Send weekly summary notification"""
        return self.send_notification(
            user=user,
            notification_type='weekly_summary',
            title='📊 Your Weekly Eco Summary',
            message=f"You saved {summary_data.get('co2_saved', 0):.1f}kg CO₂ this week!",
            data=summary_data,
            channels=['in_app', 'email'],
            priority='normal'
        )
    
    def _get_user_preferences(self, user, notification_type):
        """Get user notification preferences"""
        try:
            return NotificationPreference.objects.get(user=user, notification_type=notification_type)
        except NotificationPreference.DoesNotExist:
            # Create default preferences
            return NotificationPreference.objects.create(
                user=user,
                notification_type=notification_type,
                enabled=True,
                push_enabled=True,
                email_enabled=False,  # Email disabled by default
                in_app_enabled=True
            )
    
    def _get_default_channels(self, notification_type):
        """Get default channels for notification type"""
        channel_map = {
            'badge_earned': ['in_app', 'websocket', 'push'],
            'challenge_complete': ['in_app', 'websocket', 'push'],
            'challenge_reminder': ['in_app'],
            'milestone_reached': ['in_app', 'websocket', 'push'],
            'leaderboard_rank': ['in_app', 'websocket'],
            'weekly_summary': ['in_app', 'email'],
            'system_message': ['in_app', 'websocket']
        }
        return channel_map.get(notification_type, ['in_app'])
    
    def _send_in_app_notification(self, notification):
        """Store notification for in-app display"""
        try:
            # Notification is already saved to database
            return {'status': 'success', 'timestamp': timezone.now().isoformat()}
        except Exception as e:
            logger.error(f"Failed to send in-app notification: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _send_websocket_notification(self, notification):
        """Send real-time notification via WebSocket"""
        try:
            if self.channel_layer:
                async_to_sync(self.channel_layer.group_send)(
                    f'user_{notification.user.id}',
                    {
                        'type': 'notification_message',
                        'notification': {
                            'id': str(notification.id),
                            'type': notification.notification_type,
                            'title': notification.title,
                            'message': notification.message,
                            'data': notification.data,
                            'priority': notification.priority,
                            'created_at': notification.created_at.isoformat()
                        }
                    }
                )
                return {'status': 'success', 'timestamp': timezone.now().isoformat()}
            else:
                return {'status': 'failed', 'error': 'Channel layer not available'}
        except Exception as e:
            logger.error(f"Failed to send websocket notification: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _send_push_notification(self, notification):
        """Send push notification to mobile device"""
        try:
            # This would integrate with FCM, APNS, or other push service
            # For now, just log the attempt
            logger.info(f"Push notification sent to user {notification.user.id}: {notification.title}")
            return {'status': 'success', 'timestamp': timezone.now().isoformat()}
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _send_email_notification(self, notification):
        """Send email notification"""
        try:
            # Get email template
            template = self._get_email_template(notification.notification_type)
            
            context = {
                'user': notification.user,
                'notification': notification,
                'title': notification.title,
                'message': notification.message,
                'data': notification.data
            }
            
            html_content = render_to_string(template, context)
            
            send_mail(
                subject=notification.title,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                html_message=html_content,
                fail_silently=False
            )
            
            return {'status': 'success', 'timestamp': timezone.now().isoformat()}
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _get_email_template(self, notification_type):
        """Get email template for notification type"""
        template_map = {
            'badge_earned': 'notifications/email/badge_earned.html',
            'challenge_complete': 'notifications/email/challenge_complete.html',
            'milestone_reached': 'notifications/email/milestone.html',
            'weekly_summary': 'notifications/email/weekly_summary.html',
        }
        return template_map.get(notification_type, 'notifications/email/default.html')
    
    def get_user_notifications(self, user, limit=50, unread_only=False):
        """Get notifications for user"""
        queryset = Notification.objects.filter(user=user)
        
        if unread_only:
            queryset = queryset.filter(read_at__isnull=True)
        
        return queryset.order_by('-created_at')[:limit]
    
    def mark_notification_read(self, notification_id, user):
        """Mark notification as read"""
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.read_at = timezone.now()
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    def mark_all_read(self, user):
        """Mark all notifications as read for user"""
        return Notification.objects.filter(
            user=user,
            read_at__isnull=True
        ).update(read_at=timezone.now())


class NotificationTrigger:
    """Handles automatic notification triggers based on events"""
    
    def __init__(self):
        self.service = NotificationService()
    
    def check_milestone_achievements(self, user):
        """Check if user has reached any milestones"""
        stats, _ = UserStats.objects.get_or_create(user=user)
        
        milestones_to_check = [
            (7, 'week_1', 'first_week'),
            (30, 'month_1', 'first_month'),
            (100, 'activities_100', 'activity_milestone'),
            (50.0, 'co2_50kg', 'co2_milestone'),
        ]
        
        for threshold, milestone_key, milestone_type in milestones_to_check:
            if not self._milestone_already_achieved(user, milestone_key):
                if self._check_milestone_condition(stats, milestone_type, threshold):
                    self._record_milestone_achievement(user, milestone_key)
                    self.service.send_milestone_notification(
                        user, milestone_type, {'threshold': threshold}
                    )
    
    def _milestone_already_achieved(self, user, milestone_key):
        """Check if milestone was already achieved"""
        # This would check a milestone tracking table
        return False  # Simplified for now
    
    def _check_milestone_condition(self, stats, milestone_type, threshold):
        """Check if milestone condition is met"""
        if milestone_type == 'activity_milestone':
            return stats.total_activities >= threshold
        elif milestone_type == 'co2_milestone':
            return stats.total_co2_saved >= threshold
        return False
    
    def _record_milestone_achievement(self, user, milestone_key):
        """Record that milestone was achieved"""
        # This would record in a milestone tracking table
        pass