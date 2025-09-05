"""
Social Features API Views
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    Badge, UserBadge, Challenge, ChallengeParticipation,
    Leaderboard, LeaderboardEntry, SocialFeed, UserStats
)
from .serializers import (
    BadgeSerializer, UserBadgeSerializer, ChallengeSerializer,
    ChallengeParticipationSerializer, ChallengeCreateSerializer,
    LeaderboardSerializer, LeaderboardEntrySerializer, LeaderboardWithEntriesSerializer,
    SocialFeedSerializer, UserStatsSerializer
)
from .services import (
    SocialService, BadgeService, ChallengeService, LeaderboardService
)


class BadgeListView(generics.ListAPIView):
    """List all available badges"""
    queryset = Badge.objects.filter(is_active=True)
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserBadgesView(generics.ListAPIView):
    """List user's earned badges"""
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user).select_related('badge', 'user')


class ChallengeListView(generics.ListCreateAPIView):
    """List and create challenges"""
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChallengeCreateSerializer
        return ChallengeSerializer
    
    def get_queryset(self):
        queryset = Challenge.objects.filter(is_active=True).select_related('created_by', 'reward_badge')
        
        # Filter by challenge type
        challenge_type = self.request.query_params.get('type', None)
        if challenge_type:
            queryset = queryset.filter(challenge_type=challenge_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        now = timezone.now()
        
        if status_filter == 'current':
            queryset = queryset.filter(start_date__lte=now, end_date__gte=now)
        elif status_filter == 'upcoming':
            queryset = queryset.filter(start_date__gt=now)
        elif status_filter == 'ended':
            queryset = queryset.filter(end_date__lt=now)
        
        # Filter featured
        featured = self.request.query_params.get('featured', None)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset.order_by('-is_featured', '-start_date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ChallengeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Challenge detail, update, delete"""
    queryset = Challenge.objects.filter(is_active=True)
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ChallengeCreateSerializer
        return ChallengeSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_challenge(request, challenge_id):
    """Join a challenge"""
    challenge = get_object_or_404(Challenge, id=challenge_id, is_active=True)
    
    # Check if user already participating
    existing = ChallengeParticipation.objects.filter(
        user=request.user, 
        challenge=challenge,
        is_active=True
    ).first()
    
    if existing:
        return Response(
            {'error': 'Already participating in this challenge'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if challenge is full
    if challenge.max_participants:
        current_participants = challenge.participants.filter(is_active=True).count()
        if current_participants >= challenge.max_participants:
            return Response(
                {'error': 'Challenge is full'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Check if challenge is current
    now = timezone.now()
    if now > challenge.end_date:
        return Response(
            {'error': 'Challenge has ended'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create participation
    participation = ChallengeParticipation.objects.create(
        user=request.user,
        challenge=challenge
    )
    
    # Update user's challenge progress using service
    ChallengeService.update_user_progress(request.user)
    
    serializer = ChallengeParticipationSerializer(participation)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def leave_challenge(request, challenge_id):
    """Leave a challenge"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    participation = get_object_or_404(
        ChallengeParticipation,
        user=request.user,
        challenge=challenge,
        is_active=True
    )
    
    participation.is_active = False
    participation.save()
    
    return Response({'message': 'Left challenge successfully'})


class UserChallengesView(generics.ListAPIView):
    """List user's challenge participations"""
    serializer_class = ChallengeParticipationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ChallengeParticipation.objects.filter(
            user=self.request.user
        ).select_related('challenge', 'user')
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'completed':
            queryset = queryset.filter(is_completed=True)
        
        return queryset.order_by('-joined_at')


class LeaderboardListView(generics.ListAPIView):
    """List all leaderboards"""
    queryset = Leaderboard.objects.filter(is_active=True)
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by type
        leaderboard_type = self.request.query_params.get('type', None)
        if leaderboard_type:
            queryset = queryset.filter(leaderboard_type=leaderboard_type)
        
        # Filter featured
        featured = self.request.query_params.get('featured', None)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset.order_by('-is_featured', 'name')


class LeaderboardDetailView(generics.RetrieveAPIView):
    """Leaderboard with entries"""
    queryset = Leaderboard.objects.filter(is_active=True)
    serializer_class = LeaderboardWithEntriesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        leaderboard = super().get_object()
        # Update leaderboard entries
        LeaderboardService.update_leaderboard(leaderboard)
        return leaderboard


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_leaderboard_position(request, leaderboard_id):
    """Get user's position in a specific leaderboard"""
    leaderboard = get_object_or_404(Leaderboard, id=leaderboard_id, is_active=True)
    
    # Get user's entry
    entry = LeaderboardEntry.objects.filter(
        leaderboard=leaderboard,
        user=request.user
    ).first()
    
    if not entry:
        return Response({'message': 'User not found in leaderboard'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = LeaderboardEntrySerializer(entry)
    return Response(serializer.data)


class SocialFeedView(generics.ListAPIView):
    """Social activity feed"""
    serializer_class = SocialFeedSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = SocialFeed.objects.filter(is_public=True).select_related('user')
        
        # Filter by activity type
        activity_type = self.request.query_params.get('type', None)
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Filter by user (for personal feed)
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter featured
        featured = self.request.query_params.get('featured', None)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset.order_by('-created_at')[:50]  # Limit to recent 50 items


class UserStatsView(generics.RetrieveAPIView):
    """Get user statistics"""
    serializer_class = UserStatsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        stats, created = UserStats.objects.get_or_create(user=self.request.user)
        if created or (timezone.now() - stats.last_updated).total_seconds() > 3600:  # Update hourly
            SocialService.update_user_stats(self.request.user)
            stats.refresh_from_db()
        return stats


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard(request):
    """User social dashboard with summary data"""
    user = request.user
    
    # Get or create user stats
    stats, created = UserStats.objects.get_or_create(user=user)
    if created:
        SocialService.update_user_stats(user)
        stats.refresh_from_db()
    
    # Get recent badges (last 5)
    recent_badges = UserBadge.objects.filter(user=user).select_related('badge')[:5]
    
    # Get active challenges
    active_challenges = ChallengeParticipation.objects.filter(
        user=user,
        is_active=True,
        challenge__is_active=True
    ).select_related('challenge')[:3]
    
    # Get recent feed items
    recent_feed = SocialFeed.objects.filter(
        Q(user=user) | Q(is_featured=True)
    ).select_related('user')[:10]
    
    # Get user's best leaderboard positions (top 3)
    best_positions = LeaderboardEntry.objects.filter(
        user=user,
        rank__lte=10  # Top 10 positions only
    ).select_related('leaderboard').order_by('rank')[:3]
    
    dashboard_data = {
        'stats': UserStatsSerializer(stats).data,
        'recent_badges': UserBadgeSerializer(recent_badges, many=True).data,
        'active_challenges': ChallengeParticipationSerializer(active_challenges, many=True).data,
        'recent_feed': SocialFeedSerializer(recent_feed, many=True).data,
        'best_positions': LeaderboardEntrySerializer(best_positions, many=True).data,
    }
    
    return Response(dashboard_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def refresh_user_data(request):
    """Manually refresh user's social data"""
    user = request.user
    
    # Update user stats
    SocialService.update_user_stats(user)
    
    # Check for new badges
    BadgeService.check_user_badges(user)
    
    # Update challenge progress
    ChallengeService.update_user_progress(user)
    
    return Response({'message': 'User data refreshed successfully'})