from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import ActivityCategory, Activity, ActivityTemplate
from .serializers import (
    ActivityCategorySerializer, ActivitySerializer, 
    ActivityTemplateSerializer, ActivityCreateSerializer
)
from carbon.engine import get_calculation_engine


class ActivityCategoryListView(generics.ListAPIView):
    queryset = ActivityCategory.objects.filter(is_active=True)
    serializer_class = ActivityCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ActivityTemplateListView(generics.ListAPIView):
    serializer_class = ActivityTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'category__category_type']
    
    def get_queryset(self):
        return ActivityTemplate.objects.filter(is_active=True)


class ActivityListCreateView(generics.ListCreateAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'category__category_type', 'co2_calculated']
    ordering = ['-start_timestamp']
    
    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ActivityCreateSerializer
        return ActivitySerializer
    
    def perform_create(self, serializer):
        activity = serializer.save(user=self.request.user)
        
        # Trigger carbon calculation in background
        # For now, do it synchronously
        try:
            calculation_engine = get_calculation_engine()
            result = calculation_engine.calculate(activity)
            
            activity.co2_kg = result['co2_kg']
            activity.co2_calculated = True
            activity.save(update_fields=['co2_kg', 'co2_calculated'])
            
        except Exception as e:
            # Log error but don't fail the activity creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to calculate carbon footprint for activity {activity.id}: {str(e)}")


class ActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_view(request):
    """
    Get dashboard data for the current user.
    """
    user = request.user
    today = timezone.now().date()
    
    # Get recent activities
    recent_activities = Activity.objects.filter(
        user=user,
        start_timestamp__date=today
    )[:5]
    
    # Calculate today's CO2
    today_co2 = sum(
        float(activity.co2_kg or 0) 
        for activity in recent_activities
    )
    
    # Get this week's activities for trend
    week_start = today - timezone.timedelta(days=today.weekday())
    week_activities = Activity.objects.filter(
        user=user,
        start_timestamp__date__gte=week_start,
        co2_calculated=True
    )
    
    weekly_co2 = sum(
        float(activity.co2_kg or 0) 
        for activity in week_activities
    )
    
    # Category breakdown
    categories = {}
    for activity in week_activities:
        category = activity.category.name
        categories[category] = categories.get(category, 0) + float(activity.co2_kg or 0)
    
    return Response({
        'today_co2_kg': round(today_co2, 3),
        'weekly_co2_kg': round(weekly_co2, 3),
        'activities_today': len(recent_activities),
        'category_breakdown': categories,
        'recent_activities': ActivitySerializer(recent_activities, many=True).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def recalculate_activity_co2(request, activity_id):
    """
    Recalculate CO2 for a specific activity.
    """
    try:
        activity = Activity.objects.get(id=activity_id, user=request.user)
    except Activity.DoesNotExist:
        return Response(
            {'error': 'Activity not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        calculation_engine = get_calculation_engine()
        result = calculation_engine.calculate(activity)
        
        activity.co2_kg = result['co2_kg']
        activity.co2_calculated = True
        activity.save(update_fields=['co2_kg', 'co2_calculated'])
        
        return Response({
            'success': True,
            'activity': ActivitySerializer(activity).data,
            'calculation_result': result
        })
        
    except Exception as e:
        return Response(
            {'error': f'Calculation failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )