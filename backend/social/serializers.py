"""
Social Features Serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Badge, UserBadge, Challenge, ChallengeParticipation,
    Leaderboard, LeaderboardEntry, SocialFeed, UserStats
)

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for social features"""
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class BadgeSerializer(serializers.ModelSerializer):
    """Badge serializer"""
    class Meta:
        model = Badge
        fields = [
            'id', 'name', 'description', 'icon', 'criteria_type', 
            'criteria_value', 'criteria_period', 'rarity', 'points', 
            'is_active', 'created_at'
        ]


class UserBadgeSerializer(serializers.ModelSerializer):
    """User badge serializer"""
    badge = BadgeSerializer(read_only=True)
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = UserBadge
        fields = ['id', 'user', 'badge', 'earned_at', 'progress_value']


class ChallengeSerializer(serializers.ModelSerializer):
    """Challenge serializer"""
    created_by = UserBasicSerializer(read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    is_current = serializers.BooleanField(read_only=True)
    reward_badge = BadgeSerializer(read_only=True)
    
    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'icon', 'challenge_type',
            'goal_type', 'goal_value', 'goal_unit', 'start_date', 'end_date',
            'reward_points', 'reward_badge', 'max_participants', 'is_featured',
            'is_active', 'created_at', 'created_by', 'participant_count', 'is_current'
        ]


class ChallengeParticipationSerializer(serializers.ModelSerializer):
    """Challenge participation serializer"""
    user = UserBasicSerializer(read_only=True)
    challenge = ChallengeSerializer(read_only=True)
    
    class Meta:
        model = ChallengeParticipation
        fields = [
            'id', 'user', 'challenge', 'joined_at', 'is_active', 
            'is_completed', 'completed_at', 'current_progress', 'progress_percentage'
        ]


class ChallengeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating challenges"""
    class Meta:
        model = Challenge
        fields = [
            'title', 'description', 'icon', 'challenge_type',
            'goal_type', 'goal_value', 'goal_unit', 'start_date', 'end_date',
            'reward_points', 'reward_badge', 'max_participants', 'is_featured'
        ]


class LeaderboardSerializer(serializers.ModelSerializer):
    """Leaderboard serializer"""
    class Meta:
        model = Leaderboard
        fields = [
            'id', 'name', 'description', 'leaderboard_type', 'metric_type',
            'time_period', 'max_entries', 'is_active', 'is_featured', 'created_at'
        ]


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    """Leaderboard entry serializer"""
    user = UserBasicSerializer(read_only=True)
    leaderboard = LeaderboardSerializer(read_only=True)
    rank_change = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = LeaderboardEntry
        fields = [
            'id', 'leaderboard', 'user', 'rank', 'score', 'previous_rank',
            'period_start', 'period_end', 'last_updated', 'rank_change'
        ]


class SocialFeedSerializer(serializers.ModelSerializer):
    """Social feed serializer"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = SocialFeed
        fields = [
            'id', 'user', 'activity_type', 'title', 'description', 'metadata',
            'is_public', 'is_featured', 'created_at'
        ]


class UserStatsSerializer(serializers.ModelSerializer):
    """User statistics serializer"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = UserStats
        fields = [
            'id', 'user', 'total_activities', 'total_co2_saved', 'current_streak',
            'longest_streak', 'total_badge_points', 'challenges_completed',
            'badges_earned', 'weekly_co2_saved', 'monthly_co2_saved',
            'yearly_co2_saved', 'last_activity_date', 'last_updated'
        ]


class LeaderboardWithEntriesSerializer(serializers.ModelSerializer):
    """Leaderboard with entries"""
    entries = LeaderboardEntrySerializer(many=True, read_only=True)
    
    class Meta:
        model = Leaderboard
        fields = [
            'id', 'name', 'description', 'leaderboard_type', 'metric_type',
            'time_period', 'max_entries', 'is_active', 'is_featured', 
            'created_at', 'entries'
        ]