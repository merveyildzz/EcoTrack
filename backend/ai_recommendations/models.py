import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAIPreferences(models.Model):
    """User preferences for AI recommendations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_preferences')
    
    # Privacy settings
    ai_recommendations_enabled = models.BooleanField(default=False)
    product_suggestions_enabled = models.BooleanField(default=False)
    data_sharing_consent = models.BooleanField(default=False)
    
    # Personalization preferences
    coaching_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('disabled', 'Disabled'),
        ],
        default='weekly'
    )
    
    focus_areas = models.JSONField(default=list, blank=True)  # ['transport', 'energy', 'food']
    tone_preference = models.CharField(
        max_length=20,
        choices=[
            ('encouraging', 'Encouraging'),
            ('educational', 'Educational'),
            ('direct', 'Direct'),
            ('casual', 'Casual'),
        ],
        default='encouraging'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User AI Preferences"
        verbose_name_plural = "User AI Preferences"

    def __str__(self):
        return f"{self.user.email} - AI Preferences"


class AIRecommendation(models.Model):
    """Store AI-generated recommendations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_recommendations')
    
    recommendation_type = models.CharField(
        max_length=30,
        choices=[
            ('daily_tip', 'Daily Tip'),
            ('coaching', 'Coaching'),
            ('product_suggestion', 'Product Suggestion'),
            ('habit_improvement', 'Habit Improvement'),
            ('goal_adjustment', 'Goal Adjustment'),
        ]
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)  # Store additional data
    
    # AI response tracking
    ai_provider = models.CharField(max_length=50, default='gemini')
    ai_model = models.CharField(max_length=100, default='gemini-1.5-flash')
    prompt_version = models.CharField(max_length=20, default='v1.0')
    
    # User interaction
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    user_rating = models.IntegerField(
        null=True, 
        blank=True,
        choices=[(i, i) for i in range(1, 6)]  # 1-5 stars
    )
    user_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'recommendation_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"


class ProductSuggestion(models.Model):
    """AI-suggested eco-friendly products"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_suggestions')
    
    # Product details
    product_name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    estimated_co2_savings = models.FloatField(null=True, blank=True)
    price_range = models.CharField(max_length=50, blank=True)
    
    # External data
    product_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    vendor = models.CharField(max_length=100, blank=True)
    
    # AI metadata
    ai_confidence_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    recommendation_reason = models.TextField()
    
    # User interaction
    is_viewed = models.BooleanField(default=False)
    is_clicked = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    user_interest_level = models.CharField(
        max_length=20,
        choices=[
            ('very_high', 'Very High'),
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low'),
            ('not_interested', 'Not Interested'),
        ],
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'category']),
            models.Index(fields=['ai_confidence_score']),
        ]

    def __str__(self):
        return f"{self.product_name} - {self.user.email}"


class AIInteractionLog(models.Model):
    """Log all AI interactions for monitoring and improvement"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_interactions')
    
    # Request details
    interaction_type = models.CharField(max_length=50)  # 'recommendation', 'product_search', etc.
    prompt_text = models.TextField()
    context_data = models.JSONField(default=dict)
    
    # Response details
    ai_provider = models.CharField(max_length=50)
    ai_model = models.CharField(max_length=100)
    response_text = models.TextField()
    response_metadata = models.JSONField(default=dict)
    
    # Performance metrics
    response_time_ms = models.IntegerField()
    token_count = models.IntegerField(null=True, blank=True)
    cost_estimate = models.FloatField(null=True, blank=True)
    
    # Quality tracking
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    safety_flagged = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'interaction_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['success']),
        ]

    def __str__(self):
        return f"{self.interaction_type} - {self.user.email} - {self.created_at}"
