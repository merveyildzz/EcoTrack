import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class Organization(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=100, unique=True)
    industry = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(upload_to='org_logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations'
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['is_active']),
        ]
        
    def __str__(self):
        return self.name


class OrganizationMember(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('member', 'Member'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('invited', 'Invited'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    department = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='invitations_sent')
    
    class Meta:
        db_table = 'organization_members'
        unique_together = ['organization', 'user']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['user', 'status']),
        ]
        
    def __str__(self):
        return f"{self.user.email} @ {self.organization.name} ({self.role})"


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name='managed_teams')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teams'
        unique_together = ['organization', 'name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
        ]
        
    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teams')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'team_members'
        unique_together = ['team', 'user']
        
    def __str__(self):
        return f"{self.user.email} in {self.team.name}"


class Challenge(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    TYPE_CHOICES = [
        ('reduction', 'Carbon Reduction'),
        ('activity', 'Activity Challenge'),
        ('team', 'Team Challenge'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, 
                                   related_name='challenges', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='reduction')
    target_value = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0)])
    target_unit = models.CharField(max_length=20)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_public = models.BooleanField(default=False)
    reward_description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                  related_name='created_challenges')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'challenges'
        indexes = [
            models.Index(fields=['status', 'start_date', 'end_date']),
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['is_public', 'status']),
        ]
        ordering = ['-start_date']
        
    def __str__(self):
        return f"{self.title} ({self.status})"


class ChallengeParticipant(models.Model):
    STATUS_CHOICES = [
        ('joined', 'Joined'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped Out'),
    ]
    
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                            related_name='challenge_participations')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, 
                            related_name='challenge_participations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='joined')
    current_progress = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'challenge_participants'
        unique_together = ['challenge', 'user']
        indexes = [
            models.Index(fields=['challenge', 'status']),
            models.Index(fields=['user', 'status']),
        ]
        
    def __str__(self):
        return f"{self.user.email} in {self.challenge.title} ({self.status})"
    
    @property
    def progress_percentage(self):
        if self.challenge.target_value > 0:
            return min(100, int((self.current_progress / self.challenge.target_value) * 100))
        return 0


class OrganizationSettings(models.Model):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='settings')
    carbon_budget_kg_monthly = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    enable_team_leaderboards = models.BooleanField(default=True)
    enable_public_challenges = models.BooleanField(default=False)
    require_activity_approval = models.BooleanField(default=False)
    data_retention_months = models.IntegerField(default=24)
    timezone = models.CharField(max_length=50, default='UTC')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organization_settings'
        
    def __str__(self):
        return f"{self.organization.name} settings"