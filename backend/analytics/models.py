import uuid
from django.db import models
from django.conf import settings


class DashboardMetrics(models.Model):
    METRIC_TYPE_CHOICES = [
        ('daily_co2', 'Daily CO2'),
        ('weekly_co2', 'Weekly CO2'),
        ('monthly_co2', 'Monthly CO2'),
        ('category_breakdown', 'Category Breakdown'),
        ('trend_analysis', 'Trend Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                            related_name='dashboard_metrics', null=True, blank=True)
    organization = models.ForeignKey('corporate.Organization', on_delete=models.CASCADE,
                                   related_name='dashboard_metrics', null=True, blank=True)
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPE_CHOICES)
    metric_date = models.DateField()
    value = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dashboard_metrics'
        unique_together = ['user', 'organization', 'metric_type', 'metric_date']
        indexes = [
            models.Index(fields=['user', 'metric_type', 'metric_date']),
            models.Index(fields=['organization', 'metric_type', 'metric_date']),
            models.Index(fields=['metric_date']),
        ]
        
    def __str__(self):
        entity = self.user.email if self.user else self.organization.name
        return f"{entity} - {self.metric_type}: {self.metric_date}"


class Report(models.Model):
    STATUS_CHOICES = [
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('excel', 'Excel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            related_name='reports', null=True, blank=True)
    organization = models.ForeignKey('corporate.Organization', on_delete=models.CASCADE,
                                   related_name='reports', null=True, blank=True)
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating')
    parameters = models.JSONField(default=dict)
    file_url = models.URLField(blank=True)
    error_message = models.TextField(blank=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='requested_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'reports'
        indexes = [
            models.Index(fields=['user', 'status', 'created_at']),
            models.Index(fields=['organization', 'status', 'created_at']),
            models.Index(fields=['requested_by', 'created_at']),
        ]
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} ({self.status})"


class UserEngagement(models.Model):
    EVENT_TYPES = [
        ('login', 'Login'),
        ('activity_logged', 'Activity Logged'),
        ('dashboard_viewed', 'Dashboard Viewed'),
        ('challenge_joined', 'Challenge Joined'),
        ('recommendation_clicked', 'Recommendation Clicked'),
        ('report_generated', 'Report Generated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            related_name='engagement_events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_data = models.JSONField(default=dict, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_engagement'
        indexes = [
            models.Index(fields=['user', 'event_type', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
        
    def __str__(self):
        return f"{self.user.email} - {self.event_type}: {self.timestamp}"


class Leaderboard(models.Model):
    SCOPE_CHOICES = [
        ('global', 'Global'),
        ('organization', 'Organization'),
        ('team', 'Team'),
        ('friends', 'Friends'),
    ]
    
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('all_time', 'All Time'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    organization = models.ForeignKey('corporate.Organization', on_delete=models.CASCADE,
                                   null=True, blank=True, related_name='leaderboards')
    team = models.ForeignKey('corporate.Team', on_delete=models.CASCADE,
                           null=True, blank=True, related_name='leaderboards')
    date_from = models.DateField()
    date_to = models.DateField()
    rankings = models.JSONField()
    total_participants = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leaderboards'
        unique_together = ['scope', 'period', 'organization', 'team', 'date_from', 'date_to']
        indexes = [
            models.Index(fields=['scope', 'period', 'date_from', 'date_to']),
            models.Index(fields=['organization', 'period']),
            models.Index(fields=['updated_at']),
        ]
        
    def __str__(self):
        scope_name = f"{self.organization.name}" if self.organization else f"{self.team.name}" if self.team else "Global"
        return f"{scope_name} - {self.period} leaderboard: {self.date_from} to {self.date_to}"


class Insight(models.Model):
    INSIGHT_TYPES = [
        ('tip', 'Tip'),
        ('achievement', 'Achievement'),
        ('warning', 'Warning'),
        ('trend', 'Trend Analysis'),
        ('comparison', 'Comparison'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            related_name='insights')
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    is_actionable = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'insights'
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
            models.Index(fields=['insight_type', 'priority']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.email} - {self.insight_type}: {self.title}"