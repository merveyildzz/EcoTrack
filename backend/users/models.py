import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    email_verified = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, default='UTC')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.email


class UserSettings(models.Model):
    UNITS_CHOICES = [
        ('metric', 'Metric'),
        ('imperial', 'Imperial'),
    ]
    
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('friends', 'Friends Only'),
        ('private', 'Private'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    units = models.CharField(max_length=20, choices=UNITS_CHOICES, default='metric')
    privacy_level = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
    ai_recommendations = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    weekly_reports = models.BooleanField(default=True)
    social_challenges = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_settings'

    def __str__(self):
        return f"{self.user.email} settings"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"{self.user.email} profile"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class UserMetrics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metrics')
    metric_date = models.DateField()
    co2_kg = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    calories_est = models.IntegerField(null=True, blank=True)
    activities_count = models.IntegerField(default=0)
    source = models.CharField(max_length=50, default='calculated')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_metrics'
        unique_together = ['user', 'metric_date']
        indexes = [
            models.Index(fields=['user', 'metric_date']),
            models.Index(fields=['metric_date']),
        ]
        
    def __str__(self):
        return f"{self.user.email} - {self.metric_date}: {self.co2_kg}kg CO2"