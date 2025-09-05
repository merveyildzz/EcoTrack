"""
Social Features Services
Badge engine, challenge management, and leaderboard services
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    Badge, UserBadge, Challenge, ChallengeParticipation, 
    Leaderboard, LeaderboardEntry, UserStats
)

User = get_user_model()
logger = logging.getLogger(__name__)


class BadgeService:
    """Service for managing badges and achievements"""
    
    @staticmethod
    def check_user_badges(user) -> List[Badge]:
        """Check if user has earned any new badges"""
        new_badges = []
        
        try:
            # Get user stats
            stats, created = UserStats.objects.get_or_create(user=user)
            
            # Get all active badges user hasn't earned
            earned_badge_ids = user.badges.values_list('badge_id', flat=True)
            available_badges = Badge.objects.filter(
                is_active=True
            ).exclude(id__in=earned_badge_ids)
            
            for badge in available_badges:
                if BadgeService._check_badge_criteria(user, stats, badge):
                    # Award the badge
                    user_badge = UserBadge.objects.create(
                        user=user,
                        badge=badge,
                        progress_value=BadgeService._get_current_value(user, stats, badge)
                    )
                    
                    # Update user's badge points
                    stats.total_badge_points += badge.points
                    stats.badges_earned += 1
                    stats.save()
                    
                    new_badges.append(badge)
                    logger.info(f"Badge '{badge.name}' awarded to user {user.email}")
            
        except Exception as e:
            logger.error(f"Error checking badges for user {user.email}: {e}")
        
        return new_badges
    
    @staticmethod
    def _check_badge_criteria(user, stats: UserStats, badge: Badge) -> bool:
        """Check if user meets badge criteria"""
        current_value = BadgeService._get_current_value(user, stats, badge)
        return current_value >= badge.criteria_value
    
    @staticmethod
    def _get_current_value(user, stats: UserStats, badge: Badge) -> float:
        """Get current value for badge criteria"""
        criteria_type = badge.criteria_type
        
        if criteria_type == 'activity_count':
            return stats.total_activities
        elif criteria_type == 'co2_reduction':
            if badge.criteria_period == 'all_time':
                return stats.total_co2_saved
            elif badge.criteria_period == 'monthly':
                return stats.monthly_co2_saved
            elif badge.criteria_period == 'weekly':
                return stats.weekly_co2_saved
        elif criteria_type == 'streak_days':
            return stats.current_streak
        elif criteria_type == 'challenge_completion':
            return stats.challenges_completed
        elif criteria_type == 'social_engagement':
            return stats.badges_earned  # Could be more sophisticated
        
        return 0.0
    
    @staticmethod
    def create_default_badges():
        """Create default achievement badges"""
        default_badges = [
            {
                'name': 'First Steps',
                'description': 'Log your first eco-friendly activity',
                'criteria_type': 'activity_count',
                'criteria_value': 1,
                'rarity': 'common',
                'points': 10,
                'icon': 'fa-seedling'
            },
            {
                'name': 'Eco Warrior',
                'description': 'Log 10 eco-friendly activities',
                'criteria_type': 'activity_count',
                'criteria_value': 10,
                'rarity': 'uncommon',
                'points': 50,
                'icon': 'fa-leaf'
            },
            {
                'name': 'Carbon Saver',
                'description': 'Save 10 kg of CO₂e',
                'criteria_type': 'co2_reduction',
                'criteria_value': 10.0,
                'rarity': 'uncommon',
                'points': 100,
                'icon': 'fa-cloud'
            },
            {
                'name': 'Streak Master',
                'description': 'Maintain a 7-day activity streak',
                'criteria_type': 'streak_days',
                'criteria_value': 7,
                'rarity': 'rare',
                'points': 150,
                'icon': 'fa-fire'
            },
            {
                'name': 'Challenge Champion',
                'description': 'Complete 3 challenges',
                'criteria_type': 'challenge_completion',
                'criteria_value': 3,
                'rarity': 'rare',
                'points': 200,
                'icon': 'fa-trophy'
            },
            {
                'name': 'Planet Protector',
                'description': 'Save 100 kg of CO₂e',
                'criteria_type': 'co2_reduction',
                'criteria_value': 100.0,
                'rarity': 'epic',
                'points': 500,
                'icon': 'fa-globe'
            },
            {
                'name': 'Eco Legend',
                'description': 'Save 1000 kg of CO₂e',
                'criteria_type': 'co2_reduction',
                'criteria_value': 1000.0,
                'rarity': 'legendary',
                'points': 2000,
                'icon': 'fa-crown'
            }
        ]
        
        for badge_data in default_badges:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                logger.info(f"Created default badge: {badge.name}")


class ChallengeService:
    """Service for managing challenges"""
    
    @staticmethod
    def update_user_challenges(user, activity, carbon_saved):
        """Update user's progress in all active challenges"""
        try:
            # Get user's active challenge participations
            participations = ChallengeParticipation.objects.filter(
                user=user,
                is_active=True,
                challenge__is_active=True,
                challenge__start_date__lte=timezone.now(),
                challenge__end_date__gte=timezone.now()
            ).select_related('challenge')
            
            for participation in participations:
                challenge = participation.challenge
                new_progress = ChallengeService._calculate_progress(
                    user, challenge, activity, carbon_saved
                )
                
                if new_progress > participation.current_progress:
                    old_progress = participation.current_progress
                    participation.update_progress(new_progress)
                    
                    # Check if challenge was just completed
                    if participation.is_completed and old_progress < challenge.goal_value:
                        from .events import SocialEventHandler
                        SocialEventHandler.handle_challenge_completed(user, challenge)
                        
                        # Update user stats
                        stats, _ = UserStats.objects.get_or_create(user=user)
                        stats.challenges_completed += 1
                        stats.save()
            
        except Exception as e:
            logger.error(f"Error updating challenges for user {user.email}: {e}")
    
    @staticmethod
    def _calculate_progress(user, challenge: Challenge, activity, carbon_saved) -> float:
        """Calculate user's progress for a specific challenge"""
        goal_type = challenge.goal_type
        
        if goal_type == 'activity_count':
            # Count activities in challenge period
            return user.activities.filter(
                created_at__gte=challenge.start_date,
                created_at__lte=challenge.end_date
            ).count()
            
        elif goal_type == 'co2_reduction':
            # Sum CO2 savings in challenge period
            from carbon.models import CarbonCalculation
            total_saved = CarbonCalculation.objects.filter(
                activity__user=user,
                activity__created_at__gte=challenge.start_date,
                activity__created_at__lte=challenge.end_date
            ).aggregate(
                total=models.Sum('co2_equivalent_kg')
            )['total'] or 0
            return total_saved
            
        elif goal_type == 'streak_days':
            # Calculate streak during challenge period
            stats, _ = UserStats.objects.get_or_create(user=user)
            return stats.current_streak
            
        elif goal_type == 'category_focus':
            # Count activities in specific category
            target_category = challenge.metadata.get('target_category', 'transportation')
            return user.activities.filter(
                created_at__gte=challenge.start_date,
                created_at__lte=challenge.end_date,
                category__category_type=target_category
            ).count()
        
        return 0.0
    
    @staticmethod
    def join_challenge(user, challenge: Challenge) -> ChallengeParticipation:
        """Join a user to a challenge"""
        participation, created = ChallengeParticipation.objects.get_or_create(
            user=user,
            challenge=challenge,
            defaults={'is_active': True}
        )
        
        if not created and not participation.is_active:
            participation.is_active = True
            participation.save()
        
        return participation
    
    @staticmethod
    def leave_challenge(user, challenge: Challenge):
        """Remove a user from a challenge"""
        ChallengeParticipation.objects.filter(
            user=user,
            challenge=challenge
        ).update(is_active=False)
    
    @staticmethod
    def create_weekly_challenges():
        """Create recurring weekly challenges"""
        from django.contrib.auth import get_user_model
        
        # Get a staff user to create challenges (or create system user)
        User = get_user_model()
        system_user = User.objects.filter(is_staff=True).first()
        if not system_user:
            return
        
        start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)
        
        weekly_challenges = [
            {
                'title': 'Weekly CO₂ Saver',
                'description': 'Save 5 kg of CO₂e this week through eco-friendly activities',
                'goal_type': 'co2_reduction',
                'goal_value': 5.0,
                'goal_unit': 'kg CO₂e',
                'reward_points': 100,
                'challenge_type': 'individual'
            },
            {
                'title': 'Activity Streak',
                'description': 'Log at least one activity every day this week',
                'goal_type': 'streak_days',
                'goal_value': 7,
                'goal_unit': 'days',
                'reward_points': 150,
                'challenge_type': 'individual'
            },
            {
                'title': 'Transport Challenge',
                'description': 'Use sustainable transportation 5 times this week',
                'goal_type': 'category_focus',
                'goal_value': 5,
                'goal_unit': 'activities',
                'reward_points': 80,
                'challenge_type': 'individual',
                'metadata': {'target_category': 'transportation'}
            }
        ]
        
        for challenge_data in weekly_challenges:
            Challenge.objects.get_or_create(
                title=challenge_data['title'],
                start_date=start_date,
                end_date=end_date,
                defaults={
                    **challenge_data,
                    'created_by': system_user,
                    'is_active': True,
                    'is_featured': True
                }
            )


class LeaderboardService:
    """Service for managing leaderboards"""
    
    @staticmethod
    def update_user_rankings(user):
        """Update user's rankings across all leaderboards"""
        try:
            active_leaderboards = Leaderboard.objects.filter(is_active=True)
            
            for leaderboard in active_leaderboards:
                LeaderboardService._update_leaderboard_entry(user, leaderboard)
                
        except Exception as e:
            logger.error(f"Error updating leaderboards for user {user.email}: {e}")
    
    @staticmethod
    def _update_leaderboard_entry(user, leaderboard: Leaderboard):
        """Update a specific leaderboard entry for a user"""
        period_start, period_end = LeaderboardService._get_period_dates(leaderboard.time_period)
        
        # Calculate user's score
        score = LeaderboardService._calculate_score(user, leaderboard)
        
        # Get existing entry or create new one
        entry, created = LeaderboardEntry.objects.get_or_create(
            leaderboard=leaderboard,
            user=user,
            period_start=period_start,
            defaults={
                'score': score,
                'period_end': period_end,
                'rank': 999999  # Temporary rank
            }
        )
        
        if not created:
            entry.previous_rank = entry.rank
            entry.score = score
            entry.save()
        
        # Recalculate rankings for this leaderboard
        LeaderboardService._recalculate_rankings(leaderboard, period_start)
    
    @staticmethod
    def _calculate_score(user, leaderboard: Leaderboard) -> float:
        """Calculate user's score for a leaderboard"""
        metric_type = leaderboard.metric_type
        stats, _ = UserStats.objects.get_or_create(user=user)
        
        if metric_type == 'total_co2_saved':
            return stats.total_co2_saved
        elif metric_type == 'activity_count':
            return stats.total_activities
        elif metric_type == 'streak_days':
            return stats.current_streak
        elif metric_type == 'badge_points':
            return stats.total_badge_points
        elif metric_type == 'challenge_completions':
            return stats.challenges_completed
        
        return 0.0
    
    @staticmethod
    def _get_period_dates(time_period: str) -> tuple:
        """Get start and end dates for a time period"""
        now = timezone.now()
        
        if time_period == 'weekly':
            start = now - timedelta(days=now.weekday())
            end = start + timedelta(days=7)
        elif time_period == 'monthly':
            start = now.replace(day=1)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        elif time_period == 'yearly':
            start = now.replace(month=1, day=1)
            end = start.replace(year=start.year + 1)
        else:  # all_time
            start = datetime(2020, 1, 1, tzinfo=timezone.utc)
            end = datetime(2030, 1, 1, tzinfo=timezone.utc)
        
        return start, end
    
    @staticmethod
    def _recalculate_rankings(leaderboard: Leaderboard, period_start: datetime):
        """Recalculate rankings for a leaderboard"""
        entries = LeaderboardEntry.objects.filter(
            leaderboard=leaderboard,
            period_start=period_start
        ).order_by('-score')
        
        rank_changes = []
        for rank, entry in enumerate(entries, 1):
            old_rank = entry.rank
            entry.rank = rank
            entry.save()
            
            if old_rank != rank:
                rank_changes.append({
                    'user': entry.user,
                    'new_rank': rank,
                    'old_rank': old_rank
                })
        
        # Send real-time updates for significant rank changes
        from .events import SocialEventHandler
        for change in rank_changes:
            if change['new_rank'] <= 10:  # Only notify for top 10
                SocialEventHandler.handle_leaderboard_rank_change(
                    change['user'],
                    leaderboard.leaderboard_type,
                    change['new_rank'],
                    change['old_rank']
                )
    
    @staticmethod
    def create_default_leaderboards():
        """Create default leaderboards"""
        default_leaderboards = [
            {
                'name': 'Global CO₂ Savers',
                'description': 'Top users by total CO₂ saved',
                'leaderboard_type': 'global',
                'metric_type': 'total_co2_saved',
                'time_period': 'all_time',
                'is_featured': True
            },
            {
                'name': 'Monthly Champions',
                'description': 'Top users this month by CO₂ saved',
                'leaderboard_type': 'global',
                'metric_type': 'total_co2_saved',
                'time_period': 'monthly',
                'is_featured': True
            },
            {
                'name': 'Activity Leaders',
                'description': 'Most active users by activity count',
                'leaderboard_type': 'global',
                'metric_type': 'activity_count',
                'time_period': 'all_time',
                'is_featured': False
            },
            {
                'name': 'Streak Masters',
                'description': 'Longest current activity streaks',
                'leaderboard_type': 'global',
                'metric_type': 'streak_days',
                'time_period': 'all_time',
                'is_featured': True
            }
        ]
        
        for lb_data in default_leaderboards:
            leaderboard, created = Leaderboard.objects.get_or_create(
                name=lb_data['name'],
                defaults=lb_data
            )
            if created:
                logger.info(f"Created default leaderboard: {leaderboard.name}")


class SocialService:
    """General social features service"""
    
    @staticmethod
    def update_user_stats(user) -> UserStats:
        """Update user's social statistics"""
        from activities.models import Activity
        
        try:
            stats, created = UserStats.objects.get_or_create(user=user)
            
            # Calculate activity statistics
            activities = Activity.objects.filter(user=user)
            total_activities = activities.count()
            total_co2_saved = float(activities.aggregate(
                total=models.Sum('co2_saved')
            )['total'] or 0)
            
            # Calculate time-based statistics
            now = timezone.now()
            week_start = now - timedelta(days=7)
            month_start = now.replace(day=1)
            year_start = now.replace(month=1, day=1)
            
            weekly_co2 = float(activities.filter(
                created_at__gte=week_start
            ).aggregate(total=models.Sum('co2_saved'))['total'] or 0)
            
            monthly_co2 = float(activities.filter(
                created_at__gte=month_start
            ).aggregate(total=models.Sum('co2_saved'))['total'] or 0)
            
            yearly_co2 = float(activities.filter(
                created_at__gte=year_start
            ).aggregate(total=models.Sum('co2_saved'))['total'] or 0)
            
            # Update stats
            stats.total_activities = total_activities
            stats.total_co2_saved = total_co2_saved
            stats.weekly_co2_saved = weekly_co2
            stats.monthly_co2_saved = monthly_co2
            stats.yearly_co2_saved = yearly_co2
            
            # Update badges and challenges counts
            stats.badges_earned = UserBadge.objects.filter(user=user).count()
            stats.challenges_completed = ChallengeParticipation.objects.filter(
                user=user, is_completed=True
            ).count()
            
            # Calculate badge points
            stats.total_badge_points = UserBadge.objects.filter(user=user).aggregate(
                total=models.Sum('badge__points')
            )['total'] or 0
            
            # Update streak
            stats.update_streak()
            
            stats.save()
            logger.info(f"Updated stats for user {user.email}")
            return stats
            
        except Exception as e:
            logger.error(f"Error updating user stats for {user.email}: {str(e)}")
            raise