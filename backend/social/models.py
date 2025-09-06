"""
Social Features Models
Leaderboards, challenges, badges, and social interactions
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Badge(models.Model):
    """Achievement badges users can earn"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)  # Font Awesome icon class
    
    # Badge criteria
    criteria_type = models.CharField(
        max_length=30,
        choices=[
            ('activity_count', 'Activity Count'),
            ('co2_reduction', 'CO2 Reduction'),
            ('streak_days', 'Daily Streak'),
            ('challenge_completion', 'Challenge Completion'),
            ('social_engagement', 'Social Engagement'),
        ]
    )
    criteria_value = models.FloatField()  # Threshold value to earn badge
    criteria_period = models.CharField(
        max_length=20,
        choices=[
            ('all_time', 'All Time'),
            ('monthly', 'Monthly'),
            ('weekly', 'Weekly'),
            ('daily', 'Daily'),
        ],
        default='all_time'
    )
    
    # Badge properties
    rarity = models.CharField(
        max_length=20,
        choices=[
            ('common', 'Common'),
            ('uncommon', 'Uncommon'),
            ('rare', 'Rare'),
            ('epic', 'Epic'),
            ('legendary', 'Legendary'),
        ],
        default='common'
    )
    points = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['rarity', 'name']
        
    def __str__(self):
        return f"{self.name} ({self.rarity})"


class UserBadge(models.Model):
    """Badges earned by users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    
    earned_at = models.DateTimeField(auto_now_add=True)
    progress_value = models.FloatField(default=0.0)  # Value that triggered the badge
    
    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']
        
    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"


class Challenge(models.Model):
    """Community challenges users can participate in"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Challenge details
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    
    # Challenge mechanics
    challenge_type = models.CharField(
        max_length=30,
        choices=[
            ('individual', 'Individual'),
            ('team', 'Team'),
            ('community', 'Community'),
        ],
        default='individual'
    )
    
    goal_type = models.CharField(
        max_length=30,
        choices=[
            ('activity_count', 'Activity Count'),
            ('co2_reduction', 'CO2 Reduction'),
            ('streak_days', 'Daily Streak'),
            ('category_focus', 'Category Focus'),
        ]
    )
    goal_value = models.FloatField()
    goal_unit = models.CharField(max_length=20, default='count')
    
    # Challenge timing
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Rewards
    reward_points = models.IntegerField(default=0)
    reward_badge = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Challenge properties
    max_participants = models.IntegerField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_challenges_created')
    
    class Meta:
        ordering = ['-is_featured', '-start_date']
        
    @property
    def is_current(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    @property
    def participant_count(self):
        return self.participants.filter(is_active=True).count()
        
    def __str__(self):
        return f"{self.title} ({self.challenge_type})"


class ChallengeParticipation(models.Model):
    """User participation in challenges"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_challenge_participations')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    
    # Participation tracking
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Progress tracking
    current_progress = models.FloatField(default=0.0)
    progress_percentage = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ['user', 'challenge']
        ordering = ['-joined_at']
        
    def update_progress(self, new_progress):
        """Update challenge progress"""
        self.current_progress = new_progress
        self.progress_percentage = min((new_progress / self.challenge.goal_value) * 100, 100)
        
        if self.progress_percentage >= 100 and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            
        self.save()
        
    def __str__(self):
        return f"{self.user.email} - {self.challenge.title}"


class Leaderboard(models.Model):
    """Leaderboard configurations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Leaderboard type
    leaderboard_type = models.CharField(
        max_length=30,
        choices=[
            ('global', 'Global'),
            ('friends', 'Friends'),
            ('challenge', 'Challenge-based'),
            ('category', 'Category-based'),
        ]
    )
    
    # Scoring criteria
    metric_type = models.CharField(
        max_length=30,
        choices=[
            ('total_co2_saved', 'Total CO2 Saved'),
            ('activity_count', 'Activity Count'),
            ('streak_days', 'Streak Days'),
            ('badge_points', 'Badge Points'),
            ('challenge_completions', 'Challenge Completions'),
        ]
    )
    
    # Time period
    time_period = models.CharField(
        max_length=20,
        choices=[
            ('all_time', 'All Time'),
            ('yearly', 'Yearly'),
            ('monthly', 'Monthly'),
            ('weekly', 'Weekly'),
        ],
        default='monthly'
    )
    
    # Leaderboard properties
    max_entries = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', 'name']
        
    def __str__(self):
        return f"{self.name} ({self.metric_type})"


class LeaderboardEntry(models.Model):
    """Individual leaderboard entries"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, related_name='entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Ranking data
    rank = models.IntegerField()
    score = models.FloatField()
    previous_rank = models.IntegerField(null=True, blank=True)
    
    # Meta data
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['leaderboard', 'user', 'period_start']
        ordering = ['leaderboard', 'rank']
        
    @property
    def rank_change(self):
        if self.previous_rank is None:
            return 0
        return self.previous_rank - self.rank
        
    def __str__(self):
        return f"{self.leaderboard.name} - {self.user.email} (#{self.rank})"


class SocialFeed(models.Model):
    """Social activity feed"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_entries')
    
    # Feed content
    activity_type = models.CharField(
        max_length=30,
        choices=[
            ('badge_earned', 'Badge Earned'),
            ('challenge_completed', 'Challenge Completed'),
            ('leaderboard_rank', 'Leaderboard Achievement'),
            ('milestone_reached', 'Milestone Reached'),
            ('streak_achievement', 'Streak Achievement'),
        ]
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    
    # Visibility
    is_public = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.email} - {self.activity_type}"


class UserStats(models.Model):
    """Aggregated user statistics for leaderboards"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='social_stats')
    
    # Activity statistics
    total_activities = models.IntegerField(default=0)
    total_co2_saved = models.FloatField(default=0.0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    
    # Social statistics
    total_badge_points = models.IntegerField(default=0)
    challenges_completed = models.IntegerField(default=0)
    badges_earned = models.IntegerField(default=0)
    
    # Time-based statistics
    weekly_co2_saved = models.FloatField(default=0.0)
    monthly_co2_saved = models.FloatField(default=0.0)
    yearly_co2_saved = models.FloatField(default=0.0)
    
    last_activity_date = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def update_streak(self):
        """Update user's activity streak"""
        from activities.models import Activity
        
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Check if user has activity today or yesterday
        recent_activity = Activity.objects.filter(
            user=self.user,
            created_at__date__in=[today, yesterday]
        ).exists()
        
        if recent_activity:
            if self.last_activity_date and (today - self.last_activity_date.date()).days == 1:
                self.current_streak += 1
            elif self.last_activity_date is None or (today - self.last_activity_date.date()).days > 1:
                self.current_streak = 1
            
            self.longest_streak = max(self.longest_streak, self.current_streak)
            self.last_activity_date = timezone.now()
        else:
            # Reset streak if no recent activity
            if self.last_activity_date and (today - self.last_activity_date.date()).days > 1:
                self.current_streak = 0
        
        self.save()
    
    def __str__(self):
        return f"{self.user.email} - Stats"
