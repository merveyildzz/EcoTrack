"""
A/B Testing and Feature Flag Models
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class FeatureFlag(models.Model):
    """Feature flags for gradual rollouts and A/B testing"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    # Flag configuration
    is_active = models.BooleanField(default=True)
    rollout_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Percentage of users who see this flag (0-100)"
    )
    
    # Targeting
    target_user_groups = models.JSONField(default=dict, blank=True)
    exclude_user_groups = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.rollout_percentage}%)"
    
    def is_enabled_for_user(self, user):
        """Check if flag is enabled for specific user"""
        if not self.is_active:
            return False
        
        # Check exclusions first
        if self._user_matches_criteria(user, self.exclude_user_groups):
            return False
        
        # Check targeting
        if self.target_user_groups and not self._user_matches_criteria(user, self.target_user_groups):
            return False
        
        # Check rollout percentage
        user_hash = hash(f"{self.id}:{user.id}") % 100
        return user_hash < self.rollout_percentage
    
    def _user_matches_criteria(self, user, criteria):
        """Check if user matches targeting criteria"""
        if not criteria:
            return False
        
        # Email domain targeting
        if 'email_domains' in criteria:
            email_domain = user.email.split('@')[1] if '@' in user.email else ''
            if email_domain in criteria['email_domains']:
                return True
        
        # User ID targeting
        if 'user_ids' in criteria:
            if str(user.id) in criteria['user_ids']:
                return True
        
        # Registration date targeting
        if 'registered_after' in criteria:
            try:
                after_date = timezone.datetime.fromisoformat(criteria['registered_after'])
                if user.date_joined >= after_date:
                    return True
            except:
                pass
        
        return False


class Experiment(models.Model):
    """A/B Testing experiments"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    hypothesis = models.TextField(help_text="What are you testing and why?")
    
    # Experiment configuration
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    traffic_allocation = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Percentage of traffic to include in experiment"
    )
    
    # Timeline
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Targeting
    target_criteria = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    @property
    def is_running(self):
        """Check if experiment is currently running"""
        if self.status != 'running':
            return False
        
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def get_variant_for_user(self, user):
        """Get experiment variant for user"""
        if not self.is_running:
            return None
        
        # Check if user is in experiment
        if not self._user_in_experiment(user):
            return None
        
        # Get user's variant assignment
        assignment, created = ExperimentAssignment.objects.get_or_create(
            experiment=self,
            user=user,
            defaults={'assigned_at': timezone.now()}
        )
        
        return assignment.variant
    
    def _user_in_experiment(self, user):
        """Check if user should be included in experiment"""
        # Check traffic allocation
        user_hash = hash(f"{self.id}:{user.id}") % 100
        if user_hash >= self.traffic_allocation:
            return False
        
        # Check targeting criteria
        return self._user_matches_criteria(user, self.target_criteria)
    
    def _user_matches_criteria(self, user, criteria):
        """Check if user matches targeting criteria"""
        if not criteria:
            return True
        
        # Reuse logic from FeatureFlag
        flag = FeatureFlag(target_user_groups=criteria)
        return flag._user_matches_criteria(user, criteria)


class ExperimentVariant(models.Model):
    """Variants within an experiment"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Allocation
    weight = models.FloatField(
        default=50.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Weight for random assignment (variants are normalized)"
    )
    
    # Configuration
    config = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['experiment', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.experiment.name} - {self.name}"


class ExperimentAssignment(models.Model):
    """User assignments to experiment variants"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    variant = models.ForeignKey(ExperimentVariant, on_delete=models.CASCADE)
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['experiment', 'user']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.user.email} → {self.variant.name}"


class ExperimentMetric(models.Model):
    """Metrics tracked for experiments"""
    
    METRIC_TYPES = [
        ('conversion', 'Conversion Rate'),
        ('engagement', 'Engagement'),
        ('retention', 'Retention'),
        ('revenue', 'Revenue'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='metrics')
    name = models.CharField(max_length=100)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    description = models.TextField(blank=True)
    
    # Configuration
    is_primary = models.BooleanField(default=False)
    goal_direction = models.CharField(
        max_length=10,
        choices=[('increase', 'Increase'), ('decrease', 'Decrease')],
        default='increase'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['experiment', 'name']
        ordering = ['-is_primary', 'name']
    
    def __str__(self):
        return f"{self.experiment.name} - {self.name}"


class ExperimentEvent(models.Model):
    """Events tracked for experiment analysis"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    variant = models.ForeignKey(ExperimentVariant, on_delete=models.CASCADE)
    metric = models.ForeignKey(ExperimentMetric, on_delete=models.CASCADE)
    
    # Event data
    event_name = models.CharField(max_length=100)
    event_value = models.FloatField(default=1.0)
    properties = models.JSONField(default=dict, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['experiment', 'variant', 'metric']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_name} - {self.variant.name} - {self.user.email[:20]}"


class PersonalizationProfile(models.Model):
    """User personalization profiles"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personalization')
    
    # User segments
    segments = models.JSONField(default=list, blank=True)
    
    # Behavioral data
    activity_frequency = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low (< 3/week)'),
            ('medium', 'Medium (3-7/week)'),
            ('high', 'High (> 7/week)'),
        ],
        default='low'
    )
    
    preferred_categories = models.JSONField(default=list, blank=True)
    time_of_day_pattern = models.JSONField(default=dict, blank=True)
    
    # Engagement metrics
    ai_engagement_score = models.FloatField(default=0.0)
    social_engagement_score = models.FloatField(default=0.0)
    challenge_completion_rate = models.FloatField(default=0.0)
    
    # Personalization settings
    preferred_recommendation_types = models.JSONField(default=list, blank=True)
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_updated']
    
    def __str__(self):
        return f"Profile for {self.user.email}"
    
    def update_segments(self):
        """Update user segments based on behavior"""
        new_segments = []
        
        # Activity-based segments
        if self.activity_frequency == 'high':
            new_segments.append('power_user')
        elif self.activity_frequency == 'low':
            new_segments.append('casual_user')
        
        # Engagement-based segments
        if self.ai_engagement_score > 0.7:
            new_segments.append('ai_engaged')
        if self.social_engagement_score > 0.7:
            new_segments.append('socially_active')
        if self.challenge_completion_rate > 0.8:
            new_segments.append('challenge_completer')
        
        self.segments = new_segments
        self.save()
        
        return new_segments