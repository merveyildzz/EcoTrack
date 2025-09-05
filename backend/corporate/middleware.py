"""
Multi-tenant middleware for EcoTrack
Handles tenant context and scoped queries
"""
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Organization, OrganizationMember
from .utils import get_current_tenant, set_current_tenant

User = get_user_model()


class TenantMiddleware:
    """
    Middleware to handle multi-tenant context
    Sets the current organization based on subdomain or header
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Determine tenant from subdomain or header
        tenant = self.get_tenant_from_request(request)
        
        # Set tenant context
        set_current_tenant(tenant)
        request.tenant = tenant
        
        response = self.get_response(request)
        
        # Clean up tenant context
        set_current_tenant(None)
        
        return response
    
    def get_tenant_from_request(self, request):
        """Extract tenant information from request"""
        
        # Method 1: From subdomain (e.g., acme.ecotrack.com)
        host = request.get_host()
        if '.' in host:
            subdomain = host.split('.')[0]
            if subdomain and subdomain != 'www' and subdomain != 'api':
                try:
                    return Organization.objects.get(slug=subdomain, is_active=True)
                except Organization.DoesNotExist:
                    pass
        
        # Method 2: From X-Tenant-ID header (for API requests)
        tenant_id = request.META.get('HTTP_X_TENANT_ID')
        if tenant_id:
            try:
                return Organization.objects.get(id=tenant_id, is_active=True)
            except Organization.DoesNotExist:
                pass
        
        # Method 3: From user's primary organization (fallback)
        if hasattr(request, 'user') and request.user.is_authenticated:
            membership = OrganizationMember.objects.filter(
                user=request.user,
                status='active'
            ).select_related('organization').first()
            
            if membership:
                return membership.organization
        
        return None


class TenantAccessMiddleware:
    """
    Middleware to enforce tenant access permissions
    Ensures users can only access data from their organization
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip for non-authenticated requests and public endpoints
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return self.get_response(request)
        
        # Skip for superusers
        if request.user.is_superuser:
            return self.get_response(request)
        
        # Check if user has access to the current tenant
        if hasattr(request, 'tenant') and request.tenant:
            if not self.user_has_tenant_access(request.user, request.tenant):
                raise Http404("Organization not found")
        
        return self.get_response(request)
    
    def user_has_tenant_access(self, user, tenant):
        """Check if user has access to the tenant"""
        return OrganizationMember.objects.filter(
            user=user,
            organization=tenant,
            status='active'
        ).exists()


class APITenantMiddleware:
    """
    Simplified tenant middleware for API endpoints
    Uses X-Tenant-ID header for tenant identification
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only process API requests
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Get tenant from header
        tenant_id = request.META.get('HTTP_X_TENANT_ID')
        tenant = None
        
        if tenant_id:
            try:
                tenant = Organization.objects.get(id=tenant_id, is_active=True)
            except Organization.DoesNotExist:
                pass
        
        # Set tenant context
        request.tenant = tenant
        set_current_tenant(tenant)
        
        response = self.get_response(request)
        
        # Clean up
        set_current_tenant(None)
        
        return response