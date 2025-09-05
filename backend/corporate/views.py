from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Organization, OrganizationMember, Team, TeamMember, Challenge, ChallengeParticipant
from .serializers import (
    OrganizationSerializer, OrganizationMemberSerializer, TeamSerializer, 
    TeamMemberSerializer, ChallengeSerializer, ChallengeParticipantSerializer,
    DashboardStatsSerializer
)
# Simple permission classes for now - we'll enhance these later
class IsCorporateAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # For now, allow all authenticated users - can be enhanced later
        return True

class IsCorporateManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # For now, allow all authenticated users - can be enhanced later
        return True


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get corporate dashboard statistics"""
    try:
        # Get user's organization
        membership = OrganizationMember.objects.filter(
            user=request.user, 
            status='active'
        ).first()
        
        if not membership:
            # Return default stats for users not in any organization
            stats = {
                'total_organizations': 0,
                'total_users': 0,
                'total_teams': 0,
                'total_co2_saved': 0,
                'active_challenges': 0,
                'recent_activities_count': 0,
            }
            serializer = DashboardStatsSerializer(stats)
            return Response(serializer.data)
        
        org = membership.organization
        
        # Calculate stats
        stats = {
            'total_organizations': 1,  # Current user's org only
            'total_users': OrganizationMember.objects.filter(
                organization=org, 
                status='active'
            ).count(),
            'total_teams': Team.objects.filter(
                organization=org, 
                is_active=True
            ).count(),
            'total_co2_saved': 0,  # Would be calculated from activities
            'active_challenges': Challenge.objects.filter(
                organization=org,
                status='active'
            ).count(),
            'recent_activities_count': 0,  # Would be calculated from activities
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own organization
        user_orgs = OrganizationMember.objects.filter(
            user=self.request.user, 
            status='active'
        ).values_list('organization', flat=True)
        
        return Organization.objects.filter(id__in=user_orgs)
    
    def get_permissions(self):
        """Only admins can create/update/delete organizations"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsCorporateAdmin]
        return super().get_permissions()


class OrganizationMemberViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see members from their organization
        user_orgs = OrganizationMember.objects.filter(
            user=self.request.user, 
            status='active'
        ).values_list('organization', flat=True)
        
        return OrganizationMember.objects.filter(
            organization__in=user_orgs
        ).select_related('user', 'organization', 'invited_by')
    
    def get_permissions(self):
        """Only admins/managers can manage members"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsCorporateManager]
        return super().get_permissions()


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see teams from their organization
        user_orgs = OrganizationMember.objects.filter(
            user=self.request.user, 
            status='active'
        ).values_list('organization', flat=True)
        
        return Team.objects.filter(
            organization__in=user_orgs,
            is_active=True
        ).select_related('manager', 'organization')
    
    def perform_create(self, serializer):
        # Set organization based on user's membership
        membership = OrganizationMember.objects.filter(
            user=self.request.user, 
            status='active'
        ).first()
        
        if membership:
            serializer.save(organization=membership.organization)
    
    def get_permissions(self):
        """Only managers/admins can create/update/delete teams"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsCorporateManager]
        return super().get_permissions()


class TeamMemberViewSet(viewsets.ModelViewSet):
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see team members from their organization's teams
        user_orgs = OrganizationMember.objects.filter(
            user=self.request.user, 
            status='active'
        ).values_list('organization', flat=True)
        
        return TeamMember.objects.filter(
            team__organization__in=user_orgs
        ).select_related('user', 'team')


class ChallengeViewSet(viewsets.ModelViewSet):
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can see challenges from their organization and public challenges
        user_orgs = OrganizationMember.objects.filter(
            user=self.request.user, 
            status='active'
        ).values_list('organization', flat=True)
        
        return Challenge.objects.filter(
            Q(organization__in=user_orgs) | Q(is_public=True)
        ).select_related('organization', 'created_by')
    
    def perform_create(self, serializer):
        # Set organization and creator
        membership = OrganizationMember.objects.filter(
            user=self.request.user, 
            status='active'
        ).first()
        
        if membership:
            serializer.save(
                organization=membership.organization,
                created_by=self.request.user
            )


class ChallengeParticipantViewSet(viewsets.ModelViewSet):
    serializer_class = ChallengeParticipantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can see participants in challenges they have access to
        user_orgs = OrganizationMember.objects.filter(
            user=self.request.user, 
            status='active'
        ).values_list('organization', flat=True)
        
        return ChallengeParticipant.objects.filter(
            Q(challenge__organization__in=user_orgs) | Q(challenge__is_public=True)
        ).select_related('challenge', 'user', 'team')
