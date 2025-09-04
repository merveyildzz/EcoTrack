import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class ActivityCategory(models.Model):
    CATEGORY_TYPES = [
        ('transportation', 'Transportation'),
        ('energy', 'Energy'),
        ('food', 'Food'),
        ('consumption', 'Consumption'),
        ('waste', 'Waste'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activity_categories'
        verbose_name_plural = 'Activity Categories'
        
    def __str__(self):
        return self.name


class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    category = models.ForeignKey(ActivityCategory, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_name = models.CharField(max_length=200, blank=True)
    co2_kg = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    co2_calculated = models.BooleanField(default=False)
    device_id = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'activities'
        indexes = [
            models.Index(fields=['user', 'start_timestamp']),
            models.Index(fields=['category', 'start_timestamp']),
            models.Index(fields=['start_timestamp']),
            models.Index(fields=['co2_calculated']),
        ]
        ordering = ['-start_timestamp']
        
    def __str__(self):
        return f"{self.user.email} - {self.activity_type}: {self.value} {self.unit}"
    
    @property
    def duration_minutes(self):
        if self.end_timestamp:
            return int((self.end_timestamp - self.start_timestamp).total_seconds() / 60)
        return None


class ActivityTemplate(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ActivityCategory, on_delete=models.CASCADE, related_name='templates')
    activity_type = models.CharField(max_length=100)
    default_unit = models.CharField(max_length=20)
    default_value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activity_templates'
        unique_together = ['name', 'category']
        
    def __str__(self):
        return f"{self.category.name} - {self.name}"


class ActivityImport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='imports')
    file = models.FileField(upload_to='imports/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_records = models.IntegerField(null=True, blank=True)
    processed_records = models.IntegerField(default=0)
    successful_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    error_log = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activity_imports'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.email} - Import {self.id[:8]} ({self.status})"
    
    @property
    def progress_percentage(self):
        if self.total_records and self.total_records > 0:
            return int((self.processed_records / self.total_records) * 100)
        return 0