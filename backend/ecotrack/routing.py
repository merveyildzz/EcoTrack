"""
WebSocket URL routing for EcoTrack real-time features
"""
from django.urls import path
from social.consumers import NotificationConsumer, LeaderboardConsumer, ChallengeConsumer

websocket_urlpatterns = [
    # Real-time notifications for users
    path('ws/notifications/', NotificationConsumer.as_asgi()),
    
    # Real-time leaderboard updates  
    path('ws/leaderboard/<str:type>/', LeaderboardConsumer.as_asgi()),
    
    # Challenge updates
    path('ws/challenges/<uuid:challenge_id>/', ChallengeConsumer.as_asgi()),
]