"""
Multi-tenant utilities for EcoTrack
Provides tenant context management and scoped queries
"""
import threading
from typing import Optional
from django.db import models
from django.contrib.auth import get_user_model
from .models import Organization

User = get_user_model()

# Thread-local storage for tenant context
_tenant_context = threading.local()


def get_current_tenant() -> Optional[Organization]:
    """Get the current tenant from thread-local storage"""
    return getattr(_tenant_context, 'tenant', None)


def set_current_tenant(tenant: Optional[Organization]):
    """Set the current tenant in thread-local storage"""
    _tenant_context.tenant = tenant


def get_current_tenant_id() -> Optional[str]:
    """Get the current tenant ID"""
    tenant = get_current_tenant()
    return str(tenant.id) if tenant else None


class TenantManager(models.Manager):
    """
    Custom manager that automatically filters by tenant
    """
    
    def get_queryset(self):
        """Override to filter by current tenant"""
        queryset = super().get_queryset()
        tenant = get_current_tenant()
        
        # If we have a tenant and the model has organization field
        if tenant and hasattr(self.model, 'organization'):
            queryset = queryset.filter(organization=tenant)
        
        return queryset
    
    def all_tenants(self):
        """Get queryset without tenant filtering"""
        return super().get_queryset()


class UserTenantManager(models.Manager):
    """
    Manager for models that are scoped by user and tenant
    """
    
    def get_queryset(self):
        """Filter by current tenant through user's organization membership"""
        from .models import OrganizationMember
        
        queryset = super().get_queryset()
        tenant = get_current_tenant()
        
        if tenant and hasattr(self.model, 'user'):
            # Filter to users who are members of the current tenant
            tenant_users = OrganizationMember.objects.filter(
                organization=tenant,
                status='active'
            ).values_list('user_id', flat=True)
            
            queryset = queryset.filter(user_id__in=tenant_users)
        
        return queryset


def require_tenant(func):
    """
    Decorator to ensure a tenant is set before executing the function
    """
    def wrapper(*args, **kwargs):
        if not get_current_tenant():
            raise ValueError("No tenant context available")
        return func(*args, **kwargs)
    return wrapper


def with_tenant(tenant):
    """
    Context manager to temporarily set a tenant
    
    Usage:
        with with_tenant(organization):
            # Code here runs with organization as current tenant
            activities = Activity.objects.all()
    """
    class TenantContext:
        def __init__(self, tenant):
            self.tenant = tenant
            self.previous_tenant = None
        
        def __enter__(self):
            self.previous_tenant = get_current_tenant()
            set_current_tenant(self.tenant)
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            set_current_tenant(self.previous_tenant)
    
    return TenantContext(tenant)


def get_user_organizations(user) -> models.QuerySet:
    """Get all organizations a user belongs to"""
    from .models import OrganizationMember
    
    return Organization.objects.filter(
        members__user=user,
        members__status='active',
        is_active=True
    ).distinct()


def get_user_primary_organization(user) -> Optional[Organization]:
    """Get user's primary organization (first active membership)"""
    from .models import OrganizationMember
    
    membership = OrganizationMember.objects.filter(
        user=user,
        status='active'
    ).select_related('organization').first()
    
    return membership.organization if membership else None


def switch_user_tenant(user, organization_id: str) -> bool:
    """
    Switch user's active tenant context
    Returns True if successful, False if user doesn't have access
    """
    from .models import OrganizationMember
    
    try:
        organization = Organization.objects.get(id=organization_id, is_active=True)
        
        # Check if user has access
        if OrganizationMember.objects.filter(
            user=user,
            organization=organization,
            status='active'
        ).exists():
            set_current_tenant(organization)
            return True
        
    except Organization.DoesNotExist:
        pass
    
    return False


def get_tenant_stats(tenant: Organization) -> dict:
    """Get statistics for a tenant"""
    from .models import OrganizationMember, Team
    from activities.models import Activity
    
    with with_tenant(tenant):
        stats = {
            'total_members': OrganizationMember.objects.filter(
                organization=tenant,
                status='active'
            ).count(),
            'total_teams': Team.objects.filter(
                organization=tenant,
                is_active=True
            ).count(),
            'total_activities': Activity.objects.count(),
            'total_co2_saved': 0,  # Would be calculated from activities
        }
    
    return stats


def create_organization_with_admin(name: str, admin_user: User, **kwargs) -> Organization:
    """
    Create a new organization with an admin user
    """
    from .models import OrganizationMember, OrganizationSettings
    
    # Create organization
    organization = Organization.objects.create(
        name=name,
        created_by=admin_user,
        **kwargs
    )
    
    # Create admin membership
    OrganizationMember.objects.create(
        user=admin_user,
        organization=organization,
        role='admin',
        status='active'
    )
    
    # Create default settings
    OrganizationSettings.objects.create(
        organization=organization
    )
    
    return organization


class TenantAwareModel(models.Model):
    """
    Abstract base model for tenant-aware models
    """
    objects = TenantManager()
    all_objects = models.Manager()  # Manager without tenant filtering
    
    class Meta:
        abstract = True


class UserTenantAwareModel(models.Model):
    """
    Abstract base model for user-scoped tenant-aware models
    """
    objects = UserTenantManager()
    all_objects = models.Manager()  # Manager without filtering
    
    class Meta:
        abstract = True