"""
Role-Based Access Control (RBAC) system for EcoTrack Enterprise
Handles permissions and access control for multi-tenant organizations
"""
from rest_framework import permissions
from django.core.exceptions import PermissionDenied
from .models import OrganizationMember, Team, TeamMember
from .utils import get_current_tenant


class TenantPermission(permissions.BasePermission):
    """
    Base permission class for tenant-aware permissions
    """
    
    def has_permission(self, request, view):
        """Check if user has basic tenant access"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers have access to everything
        if request.user.is_superuser:
            return True
        
        # Check if user is a member of the current tenant
        tenant = getattr(request, 'tenant', None) or get_current_tenant()
        if not tenant:
            return False
        
        return OrganizationMember.objects.filter(
            user=request.user,
            organization=tenant,
            status='active'
        ).exists()


class OrganizationAdminPermission(TenantPermission):
    """
    Permission for organization admins only
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        tenant = getattr(request, 'tenant', None) or get_current_tenant()
        if not tenant:
            return False
        
        # Check if user has admin role
        membership = OrganizationMember.objects.filter(
            user=request.user,
            organization=tenant,
            status='active'
        ).first()
        
        return membership and membership.role in ['admin', 'owner']


class OrganizationManagerPermission(TenantPermission):
    """
    Permission for organization managers and above
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        tenant = getattr(request, 'tenant', None) or get_current_tenant()
        if not tenant:
            return False
        
        membership = OrganizationMember.objects.filter(
            user=request.user,
            organization=tenant,
            status='active'
        ).first()
        
        return membership and membership.role in ['manager', 'admin', 'owner']


class TeamLeadPermission(TenantPermission):
    """
    Permission for team leads and above
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        # Organization managers and admins always have access
        tenant = getattr(request, 'tenant', None) or get_current_tenant()
        membership = OrganizationMember.objects.filter(
            user=request.user,
            organization=tenant,
            status='active'
        ).first()
        
        if membership and membership.role in ['manager', 'admin', 'owner']:
            return True
        
        # Check if user is a team lead
        return TeamMember.objects.filter(
            user=request.user,
            role='lead',
            team__organization=tenant,
            is_active=True
        ).exists()


class TeamMemberPermission(TenantPermission):
    """
    Permission for team members and above
    """
    
    def has_permission(self, request, view):
        # All authenticated tenant members have this permission
        return super().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions for team-related objects"""
        if not super().has_permission(request, view):
            return False
        
        tenant = getattr(request, 'tenant', None) or get_current_tenant()
        
        # Organization admins can access everything
        membership = OrganizationMember.objects.filter(
            user=request.user,
            organization=tenant,
            status='active'
        ).first()
        
        if membership and membership.role in ['admin', 'owner']:
            return True
        
        # Check team-specific permissions
        if hasattr(obj, 'team'):
            return TeamMember.objects.filter(
                user=request.user,
                team=obj.team,
                is_active=True
            ).exists()
        
        return True


class SelfOrAdminPermission(TenantPermission):
    """
    Permission that allows users to access their own data or admins to access any data
    """
    
    def has_object_permission(self, request, view, obj):
        if not super().has_permission(request, view):
            return False
        
        tenant = getattr(request, 'tenant', None) or get_current_tenant()
        
        # Organization admins can access everything
        membership = OrganizationMember.objects.filter(
            user=request.user,
            organization=tenant,
            status='active'
        ).first()
        
        if membership and membership.role in ['admin', 'owner']:
            return True
        
        # Users can access their own data
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class ReadOnlyOrAdminPermission(TenantPermission):
    """
    Permission that allows read access to all tenant members, write access to admins only
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        # Allow read access to all tenant members
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write access only for admins
        tenant = getattr(request, 'tenant', None) or get_current_tenant()
        membership = OrganizationMember.objects.filter(
            user=request.user,
            organization=tenant,
            status='active'
        ).first()
        
        return membership and membership.role in ['admin', 'owner']


# Utility functions for permission checking
def check_organization_permission(user, organization, required_role='member'):
    """
    Check if user has the required role in an organization
    
    Args:
        user: User object
        organization: Organization object
        required_role: Required role ('member', 'team_lead', 'manager', 'admin', 'owner')
    
    Returns:
        bool: True if user has required permission
    """
    if user.is_superuser:
        return True
    
    try:
        membership = OrganizationMember.objects.get(
            user=user,
            organization=organization,
            status='active'
        )
        
        role_hierarchy = {
            'member': 0,
            'team_lead': 1,
            'manager': 2,
            'admin': 3,
            'owner': 4
        }
        
        user_role_level = role_hierarchy.get(membership.role, -1)
        required_role_level = role_hierarchy.get(required_role, 0)
        
        return user_role_level >= required_role_level
        
    except OrganizationMember.DoesNotExist:
        return False


def check_team_permission(user, team, required_role='member'):
    """
    Check if user has the required role in a team
    
    Args:
        user: User object
        team: Team object
        required_role: Required role ('member', 'lead')
    
    Returns:
        bool: True if user has required permission
    """
    if user.is_superuser:
        return True
    
    # Organization admins have access to all teams
    if check_organization_permission(user, team.organization, 'admin'):
        return True
    
    try:
        team_membership = TeamMember.objects.get(
            user=user,
            team=team,
            is_active=True
        )
        
        if required_role == 'lead':
            return team_membership.role == 'lead'
        else:
            return True  # Any team member
            
    except TeamMember.DoesNotExist:
        return False


def require_organization_role(required_role='member'):
    """
    Decorator to require a specific organization role
    
    Usage:
        @require_organization_role('admin')
        def my_view(request):
            # Only organization admins can access this
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            tenant = getattr(request, 'tenant', None) or get_current_tenant()
            
            if not tenant:
                raise PermissionDenied("No organization context")
            
            if not check_organization_permission(request.user, tenant, required_role):
                raise PermissionDenied(f"Required role: {required_role}")
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_team_role(required_role='member'):
    """
    Decorator to require a specific team role
    
    Usage:
        @require_team_role('lead')
        def my_team_view(request, team_id):
            # Only team leads can access this
    """
    def decorator(func):
        def wrapper(request, team_id=None, *args, **kwargs):
            if not team_id:
                raise PermissionDenied("Team ID required")
            
            try:
                team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                raise PermissionDenied("Team not found")
            
            if not check_team_permission(request.user, team, required_role):
                raise PermissionDenied(f"Required team role: {required_role}")
            
            return func(request, team_id, *args, **kwargs)
        
        return wrapper
    return decorator


class PermissionChecker:
    """
    Utility class for checking various permissions
    """
    
    def __init__(self, user, organization=None):
        self.user = user
        self.organization = organization or get_current_tenant()
    
    def can_view_organization_data(self):
        """Check if user can view organization data"""
        return check_organization_permission(self.user, self.organization, 'member')
    
    def can_manage_teams(self):
        """Check if user can manage teams"""
        return check_organization_permission(self.user, self.organization, 'manager')
    
    def can_manage_users(self):
        """Check if user can manage organization users"""
        return check_organization_permission(self.user, self.organization, 'admin')
    
    def can_view_team_data(self, team):
        """Check if user can view specific team data"""
        return check_team_permission(self.user, team, 'member')
    
    def can_manage_team(self, team):
        """Check if user can manage a specific team"""
        return (
            check_organization_permission(self.user, self.organization, 'manager') or
            check_team_permission(self.user, team, 'lead')
        )
    
    def can_export_data(self):
        """Check if user can export organization data"""
        return check_organization_permission(self.user, self.organization, 'manager')
    
    def can_view_analytics(self):
        """Check if user can view advanced analytics"""
        return check_organization_permission(self.user, self.organization, 'manager')
    
    def get_accessible_teams(self):
        """Get teams the user can access"""
        if check_organization_permission(self.user, self.organization, 'manager'):
            # Managers can see all teams
            return Team.objects.filter(organization=self.organization, is_active=True)
        else:
            # Regular users can only see their teams
            user_teams = TeamMember.objects.filter(
                user=self.user,
                is_active=True,
                team__organization=self.organization
            ).values_list('team', flat=True)
            
            return Team.objects.filter(id__in=user_teams, is_active=True)