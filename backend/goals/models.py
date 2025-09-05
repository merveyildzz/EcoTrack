"""
Goal setting and tracking models for EcoTrack
Allows users to set and track environmental goals
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta

User = get_user_model()


class GoalCategory(models.Model):
    """Categories for different types of goals"""
    CATEGORY_CHOICES = [
        ('co2_reduction', 'CO₂ Reduction'),
        ('activity_frequency', 'Activity Frequency'),
        ('category_focus', 'Category Focus'),
        ('streak_building', 'Streak Building'),
        ('social_engagement', 'Social Engagement'),
        ('custom', 'Custom Goal'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Goal Categories'
        
    def __str__(self):
        return self.name


class Goal(models.Model):
    """User goals for environmental impact"""
    
    TIMEFRAME_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom Range'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('expert', 'Expert'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    category = models.ForeignKey(GoalCategory, on_delete=models.CASCADE, related_name='goals')
    
    # Goal definition
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_value = models.FloatField(validators=[MinValueValidator(0)])
    current_value = models.FloatField(default=0, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20)
    
    # Time settings
    timeframe = models.CharField(max_length=20, choices=TIMEFRAME_CHOICES)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    
    # Goal properties
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    is_public = models.BooleanField(default=False)
    auto_track = models.BooleanField(default=True)  # Auto-update from activities
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    completion_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    @property
    def days_remaining(self):
        """Calculate days remaining until goal deadline"""
        if self.status == 'completed':
            return 0
        remaining = (self.end_date.date() - timezone.now().date()).days
        return max(0, remaining)
    
    @property
    def is_overdue(self):
        """Check if goal is overdue"""
        return timezone.now() > self.end_date and self.status == 'active'
    
    @property
    def progress_rate(self):
        """Calculate daily progress rate needed to complete goal"""
        if self.days_remaining <= 0:
            return 0
        remaining_value = self.target_value - self.current_value
        return remaining_value / self.days_remaining if remaining_value > 0 else 0
    
    def update_progress(self, new_value=None):
        """Update goal progress and check for completion"""
        if new_value is not None:
            self.current_value = new_value
        
        # Calculate completion percentage
        if self.target_value > 0:
            self.completion_percentage = min((self.current_value / self.target_value) * 100, 100)
        
        # Check for completion
        if self.completion_percentage >= 100 and self.status == 'active':
            self.status = 'completed'
            self.completed_at = timezone.now()
        
        # Check for failure (overdue and not completed)
        elif self.is_overdue and self.status == 'active':
            self.status = 'failed'
        
        self.save()
        
        # Trigger notifications if needed
        if self.status == 'completed':
            from notifications.services import NotificationService
            NotificationService().send_notification(
                user=self.user,
                notification_type='goal_completed',
                title='🎯 Goal Achieved!',
                message=f'Congratulations! You completed "{self.title}"!',
                data={'goal_id': str(self.id), 'goal_title': self.title}
            )
    
    def __str__(self):
        return f"{self.title} ({self.user.email})"


class GoalMilestone(models.Model):
    """Milestones within a goal for tracking progress"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='milestones')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_value = models.FloatField(validators=[MinValueValidator(0)])
    target_date = models.DateTimeField()
    
    is_achieved = models.BooleanField(default=False)
    achieved_at = models.DateTimeField(null=True, blank=True)
    achieved_value = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['target_date']
        
    def check_achievement(self, current_value):
        """Check if milestone is achieved"""
        if not self.is_achieved and current_value >= self.target_value:
            self.is_achieved = True
            self.achieved_at = timezone.now()
            self.achieved_value = current_value
            self.save()
            
            # Send milestone notification
            from notifications.services import NotificationService
            NotificationService().send_notification(
                user=self.goal.user,
                notification_type='milestone_reached',
                title='🏁 Milestone Reached!',
                message=f'You reached the milestone: "{self.title}"!',
                data={
                    'milestone_id': str(self.id),
                    'goal_id': str(self.goal.id),
                    'milestone_title': self.title
                }
            )
            return True
        return False
    
    def __str__(self):
        return f"{self.title} ({self.goal.title})"


class GoalTemplate(models.Model):
    """Pre-defined goal templates users can choose from"""
    
    TEMPLATE_CATEGORIES = [
        ('beginner', 'Beginner Friendly'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('seasonal', 'Seasonal'),
        ('challenge', 'Challenge'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(GoalCategory, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    template_category = models.CharField(max_length=20, choices=TEMPLATE_CATEGORIES)
    
    # Default values for goals created from this template
    suggested_target_value = models.FloatField()
    suggested_timeframe = models.CharField(max_length=20, choices=Goal.TIMEFRAME_CHOICES)
    suggested_difficulty = models.CharField(max_length=10, choices=Goal.DIFFICULTY_CHOICES)
    
    # Template metadata
    icon = models.CharField(max_length=50, blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', '-usage_count', 'name']
        
    def create_goal_for_user(self, user, custom_values=None):
        """Create a goal for user based on this template"""
        custom_values = custom_values or {}
        
        # Calculate end date based on timeframe
        start_date = timezone.now()
        timeframe = custom_values.get('timeframe', self.suggested_timeframe)
        
        if timeframe == 'daily':
            end_date = start_date + timedelta(days=1)
        elif timeframe == 'weekly':
            end_date = start_date + timedelta(weeks=1)
        elif timeframe == 'monthly':
            end_date = start_date + timedelta(days=30)
        elif timeframe == 'quarterly':
            end_date = start_date + timedelta(days=90)
        elif timeframe == 'yearly':
            end_date = start_date + timedelta(days=365)
        else:
            end_date = start_date + timedelta(days=30)  # Default to 30 days
        
        goal = Goal.objects.create(
            user=user,
            category=self.category,
            title=custom_values.get('title', self.name),
            description=custom_values.get('description', self.description),
            target_value=custom_values.get('target_value', self.suggested_target_value),
            unit=self.category.unit,
            timeframe=timeframe,
            start_date=start_date,
            end_date=custom_values.get('end_date', end_date),
            difficulty=custom_values.get('difficulty', self.suggested_difficulty),
            is_public=custom_values.get('is_public', False)
        )
        
        # Increment usage count
        self.usage_count += 1
        self.save()
        
        return goal
    
    def __str__(self):
        return f"{self.name} ({self.template_category})"


class GoalProgress(models.Model):
    """Daily progress tracking for goals"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='progress_entries')
    
    date = models.DateField()
    value_added = models.FloatField(default=0)
    cumulative_value = models.FloatField()
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['goal', 'date']
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.goal.title} - {self.date}"


class GoalSharing(models.Model):
    """Handle goal sharing and collaboration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal = models.OneToOneField(Goal, on_delete=models.CASCADE, related_name='sharing')
    
    is_public = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    share_progress = models.BooleanField(default=True)
    share_with_friends = models.BooleanField(default=False)
    
    # Social features
    supporters_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Sharing for {self.goal.title}"