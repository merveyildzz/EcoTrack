from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'organizations', views.OrganizationViewSet, basename='organization')
router.register(r'users', views.OrganizationMemberViewSet, basename='organizationmember')
router.register(r'teams', views.TeamViewSet, basename='team')
router.register(r'team-members', views.TeamMemberViewSet, basename='teammember')
router.register(r'challenges', views.ChallengeViewSet, basename='challenge')
router.register(r'challenge-participants', views.ChallengeParticipantViewSet, basename='challengeparticipant')

# Define URL patterns
urlpatterns = [
    # Dashboard endpoint
    path('dashboard/', views.dashboard_stats, name='corporate-dashboard'),
    
    # Include all the router URLs
    path('', include(router.urls)),
]