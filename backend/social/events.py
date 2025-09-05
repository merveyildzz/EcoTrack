"""
Real-time Events System for Social Features
"""
import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


class EventDispatcher:
    """Centralized event dispatcher for real-time updates"""
    
    @staticmethod
    def send_notification(user_id: str, notification_type: str, title: str, message: str, data: Dict[str, Any] = None):
        """Send real-time notification to a user"""
        try:
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"user_{user_id}_notifications",
                    {
                        'type': 'notification_message',
                        'notification_type': notification_type,
                        'title': title,
                        'message': message,
                        'data': data or {},
                        'timestamp': timezone.now().isoformat()
                    }
                )
                logger.info(f"Notification sent to user {user_id}: {notification_type}")
            else:
                logger.warning("Channel layer not configured - notification not sent")
        except Exception as e:
            logger.error(f"Failed to send notification to user {user_id}: {e}")
    
    @staticmethod
    def send_leaderboard_update(leaderboard_type: str, update_type: str, data: Dict[str, Any]):
        """Send leaderboard update to all connected users"""
        try:
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"leaderboard_{leaderboard_type}",
                    {
                        'type': 'leaderboard_update',
                        'update_type': update_type,
                        'leaderboard_type': leaderboard_type,
                        'data': data,
                        'timestamp': timezone.now().isoformat()
                    }
                )
                logger.info(f"Leaderboard update sent: {leaderboard_type} - {update_type}")
            else:
                logger.warning("Channel layer not configured - leaderboard update not sent")
        except Exception as e:
            logger.error(f"Failed to send leaderboard update: {e}")
    
    @staticmethod
    def send_challenge_update(challenge_id: str, update_type: str, data: Dict[str, Any]):
        """Send challenge update to all participants"""
        try:
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"challenge_{challenge_id}",
                    {
                        'type': 'challenge_update',
                        'update_type': update_type,
                        'data': data,
                        'timestamp': timezone.now().isoformat()
                    }
                )
                logger.info(f"Challenge update sent: {challenge_id} - {update_type}")
            else:
                logger.warning("Channel layer not configured - challenge update not sent")
        except Exception as e:
            logger.error(f"Failed to send challenge update: {e}")


class SocialEventHandler:
    """Handle social events and trigger real-time updates"""
    
    @staticmethod
    def handle_activity_logged(user, activity, carbon_saved):
        """Handle when user logs an activity"""
        from .services import BadgeService, ChallengeService, LeaderboardService
        
        # Update user stats
        stats = user.social_stats if hasattr(user, 'social_stats') else None
        if stats:
            stats.total_activities += 1
            stats.total_co2_saved += carbon_saved
            stats.update_streak()
            stats.save()
        
        # Check for badge achievements
        new_badges = BadgeService.check_user_badges(user)
        for badge in new_badges:
            SocialEventHandler.handle_badge_earned(user, badge)
        
        # Update challenge progress
        ChallengeService.update_user_challenges(user, activity, carbon_saved)
        
        # Update leaderboards
        LeaderboardService.update_user_rankings(user)
        
        # Send activity logged notification
        EventDispatcher.send_notification(
            str(user.id),
            'activity_logged',
            'Activity Logged',
            f'Great! You saved {carbon_saved:.2f} kg CO₂e with your recent activity.',
            {
                'activity_type': activity.activity_type,
                'carbon_saved': carbon_saved,
                'total_saved': stats.total_co2_saved if stats else carbon_saved
            }
        )
    
    @staticmethod
    def handle_badge_earned(user, badge):
        """Handle when user earns a badge"""
        from .models import SocialFeed
        
        # Create social feed entry
        SocialFeed.objects.create(
            user=user,
            activity_type='badge_earned',
            title=f'Badge Earned: {badge.name}',
            description=badge.description,
            metadata={
                'badge_id': str(badge.id),
                'badge_name': badge.name,
                'badge_rarity': badge.rarity,
                'badge_points': badge.points
            }
        )
        
        # Send badge earned notification
        EventDispatcher.send_notification(
            str(user.id),
            'badge_earned',
            'Badge Earned!',
            f'Congratulations! You earned the "{badge.name}" badge.',
            {
                'badge_id': str(badge.id),
                'badge_name': badge.name,
                'badge_rarity': badge.rarity,
                'badge_points': badge.points,
                'badge_description': badge.description
            }
        )
    
    @staticmethod
    def handle_challenge_completed(user, challenge):
        """Handle when user completes a challenge"""
        from .models import SocialFeed
        
        # Create social feed entry
        SocialFeed.objects.create(
            user=user,
            activity_type='challenge_completed',
            title=f'Challenge Completed: {challenge.title}',
            description=f'Successfully completed the {challenge.title} challenge!',
            metadata={
                'challenge_id': str(challenge.id),
                'challenge_title': challenge.title,
                'reward_points': challenge.reward_points
            }
        )
        
        # Send challenge completion notification
        EventDispatcher.send_notification(
            str(user.id),
            'challenge_completed',
            'Challenge Completed!',
            f'Amazing! You completed the "{challenge.title}" challenge.',
            {
                'challenge_id': str(challenge.id),
                'challenge_title': challenge.title,
                'reward_points': challenge.reward_points
            }
        )
        
        # Send challenge update to all participants
        EventDispatcher.send_challenge_update(
            str(challenge.id),
            'participant_completed',
            {
                'user_id': str(user.id),
                'username': user.username,
                'challenge_title': challenge.title
            }
        )
    
    @staticmethod
    def handle_leaderboard_rank_change(user, leaderboard_type, new_rank, old_rank):
        """Handle when user's leaderboard ranking changes"""
        from .models import SocialFeed
        
        if new_rank < old_rank:  # User moved up
            rank_change = 'improved'
            message = f'You moved up to #{new_rank} in the {leaderboard_type} leaderboard!'
        else:
            rank_change = 'changed'
            message = f'Your ranking changed to #{new_rank} in the {leaderboard_type} leaderboard.'
        
        # Create social feed entry for significant rank changes (top 10)
        if new_rank <= 10:
            SocialFeed.objects.create(
                user=user,
                activity_type='leaderboard_rank',
                title=f'Leaderboard Achievement: #{new_rank}',
                description=f'Achieved #{new_rank} position in the {leaderboard_type} leaderboard!',
                metadata={
                    'leaderboard_type': leaderboard_type,
                    'new_rank': new_rank,
                    'old_rank': old_rank,
                    'rank_change': rank_change
                }
            )
        
        # Send leaderboard notification
        EventDispatcher.send_notification(
            str(user.id),
            'leaderboard_rank',
            'Leaderboard Update',
            message,
            {
                'leaderboard_type': leaderboard_type,
                'new_rank': new_rank,
                'old_rank': old_rank,
                'rank_change': rank_change
            }
        )
        
        # Send leaderboard update to all connected users
        EventDispatcher.send_leaderboard_update(
            leaderboard_type,
            'rank_change',
            {
                'user_id': str(user.id),
                'username': user.username,
                'new_rank': new_rank,
                'old_rank': old_rank
            }
        )
    
    @staticmethod
    def handle_weekly_summary_ready(user, summary_data):
        """Handle when weekly summary is ready"""
        EventDispatcher.send_notification(
            str(user.id),
            'weekly_summary',
            'Weekly Summary Ready',
            f'Your weekly eco-summary is ready! You saved {summary_data.get("co2_saved", 0):.2f} kg CO₂e.',
            summary_data
        )
    
    @staticmethod
    def handle_streak_milestone(user, streak_days):
        """Handle when user reaches a streak milestone"""
        from .models import SocialFeed
        
        # Create social feed entry for significant streaks
        if streak_days % 7 == 0:  # Weekly milestones
            SocialFeed.objects.create(
                user=user,
                activity_type='streak_achievement',
                title=f'{streak_days}-Day Streak Achievement',
                description=f'Maintained a {streak_days}-day activity streak!',
                metadata={
                    'streak_days': streak_days,
                    'milestone_type': 'weekly' if streak_days % 7 == 0 else 'milestone'
                }
            )
        
        # Send streak notification
        EventDispatcher.send_notification(
            str(user.id),
            'streak_milestone',
            'Streak Milestone!',
            f'Incredible! You\'ve maintained a {streak_days}-day activity streak.',
            {
                'streak_days': streak_days,
                'milestone_type': 'weekly' if streak_days % 7 == 0 else 'milestone'
            }
        )