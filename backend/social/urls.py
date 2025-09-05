"""
Social Features URL Configuration
"""
from django.urls import path, include
from . import views

app_name = 'social'

urlpatterns = [
    # Badges
    path('badges/', views.BadgeListView.as_view(), name='badge-list'),
    path('badges/user/', views.UserBadgesView.as_view(), name='user-badges'),
    
    # Challenges
    path('challenges/', views.ChallengeListView.as_view(), name='challenge-list'),
    path('challenges/<uuid:pk>/', views.ChallengeDetailView.as_view(), name='challenge-detail'),
    path('challenges/<uuid:challenge_id>/join/', views.join_challenge, name='challenge-join'),
    path('challenges/<uuid:challenge_id>/leave/', views.leave_challenge, name='challenge-leave'),
    path('challenges/user/', views.UserChallengesView.as_view(), name='user-challenges'),
    
    # Leaderboards
    path('leaderboards/', views.LeaderboardListView.as_view(), name='leaderboard-list'),
    path('leaderboards/<uuid:pk>/', views.LeaderboardDetailView.as_view(), name='leaderboard-detail'),
    path('leaderboards/<uuid:leaderboard_id>/position/', views.user_leaderboard_position, name='user-leaderboard-position'),
    
    # Social Feed
    path('feed/', views.SocialFeedView.as_view(), name='social-feed'),
    
    # User Stats & Dashboard
    path('stats/', views.UserStatsView.as_view(), name='user-stats'),
    path('dashboard/', views.user_dashboard, name='user-dashboard'),
    path('refresh/', views.refresh_user_data, name='refresh-user-data'),
]