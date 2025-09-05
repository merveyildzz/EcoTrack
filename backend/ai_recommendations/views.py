"""
API Views for AI Recommendations
"""

import logging
from django.db import models
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from .models import UserAIPreferences, AIRecommendation, ProductSuggestion
from .serializers import (
    UserAIPreferencesSerializer,
    AIRecommendationSerializer, 
    ProductSuggestionSerializer,
    GenerateRecommendationSerializer,
    ProductSearchSerializer,
    RecommendationFeedbackSerializer,
    ProductInteractionSerializer
)
from .services import AIRecommendationService, get_user_recommendations, mark_recommendation_read, rate_recommendation

logger = logging.getLogger(__name__)


class UserAIPreferencesView(APIView):
    """Manage user AI preferences"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user AI preferences"""
        preferences, created = UserAIPreferences.objects.get_or_create(
            user=request.user,
            defaults={
                'ai_recommendations_enabled': False,
                'coaching_frequency': 'weekly',
                'tone_preference': 'encouraging'
            }
        )
        serializer = UserAIPreferencesSerializer(preferences)
        return Response(serializer.data)
    
    def put(self, request):
        """Update user AI preferences"""
        preferences, created = UserAIPreferences.objects.get_or_create(
            user=request.user
        )
        serializer = UserAIPreferencesSerializer(preferences, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecommendationListView(generics.ListAPIView):
    """List user's AI recommendations"""
    serializer_class = AIRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AIRecommendation.objects.filter(user=self.request.user)
        
        # Filter by type if specified
        recommendation_type = self.request.query_params.get('type')
        if recommendation_type:
            queryset = queryset.filter(recommendation_type=recommendation_type)
        
        # Filter out expired recommendations
        queryset = queryset.filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        )
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)
        
        return queryset.order_by('-created_at')


class GenerateRecommendationView(APIView):
    """Generate new AI recommendation"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Generate a new recommendation"""
        serializer = GenerateRecommendationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        recommendation_type = serializer.validated_data['recommendation_type']
        force_regenerate = serializer.validated_data['force_regenerate']
        
        try:
            ai_service = AIRecommendationService(request.user)
            
            # Check if user has AI recommendations enabled
            if not ai_service.preferences.ai_recommendations_enabled:
                return Response(
                    {'error': 'AI recommendations are disabled. Please enable them in your preferences.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check for existing recent recommendation
            if not force_regenerate:
                existing = AIRecommendation.objects.filter(
                    user=request.user,
                    recommendation_type=recommendation_type,
                    created_at__gte=timezone.now() - timedelta(hours=1)
                ).first()
                
                if existing:
                    serializer = AIRecommendationSerializer(existing)
                    return Response({
                        'message': 'Using recent recommendation',
                        'recommendation': serializer.data
                    })
            
            # Generate new recommendation
            if recommendation_type in ['daily_tip', 'coaching']:
                recommendation = ai_service.generate_daily_coaching()
            else:
                return Response(
                    {'error': f'Recommendation type "{recommendation_type}" not yet implemented'},
                    status=status.HTTP_501_NOT_IMPLEMENTED
                )
            
            if recommendation:
                serializer = AIRecommendationSerializer(recommendation)
                return Response({
                    'message': 'Recommendation generated successfully',
                    'recommendation': serializer.data
                })
            else:
                return Response(
                    {'error': 'Failed to generate recommendation'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RecommendationDetailView(APIView):
    """Manage individual recommendations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, recommendation_id):
        """Get recommendation details"""
        recommendation = get_object_or_404(
            AIRecommendation, 
            id=recommendation_id, 
            user=request.user
        )
        
        # Mark as read
        if not recommendation.is_read:
            recommendation.is_read = True
            recommendation.save()
        
        serializer = AIRecommendationSerializer(recommendation)
        return Response(serializer.data)
    
    def patch(self, request, recommendation_id):
        """Update recommendation (dismiss, etc.)"""
        recommendation = get_object_or_404(
            AIRecommendation,
            id=recommendation_id,
            user=request.user
        )
        
        serializer = AIRecommendationSerializer(
            recommendation, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecommendationFeedbackView(APIView):
    """Submit feedback for recommendations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, recommendation_id):
        """Submit rating and feedback"""
        recommendation = get_object_or_404(
            AIRecommendation,
            id=recommendation_id,
            user=request.user
        )
        
        serializer = RecommendationFeedbackSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        recommendation.user_rating = serializer.validated_data['rating']
        recommendation.user_feedback = serializer.validated_data.get('feedback', '')
        recommendation.save()
        
        return Response({'message': 'Feedback submitted successfully'})


class ProductSearchView(APIView):
    """Search for eco-friendly products"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Search for products based on query"""
        serializer = ProductSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        query = serializer.validated_data['query']
        category = serializer.validated_data.get('category')
        max_results = serializer.validated_data['max_results']
        
        try:
            ai_service = AIRecommendationService(request.user)
            
            # Check if user has product suggestions enabled
            if not ai_service.preferences.product_suggestions_enabled:
                return Response(
                    {'error': 'Product suggestions are disabled. Please enable them in your preferences.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            suggestions = ai_service.search_products(query, category)
            suggestions = suggestions[:max_results]
            
            serializer = ProductSuggestionSerializer(suggestions, many=True)
            return Response({
                'query': query,
                'category': category,
                'results': serializer.data,
                'count': len(suggestions)
            })
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductSuggestionListView(generics.ListAPIView):
    """List user's product suggestions"""
    serializer_class = ProductSuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ProductSuggestion.objects.filter(user=self.request.user)
        
        # Filter by category if specified
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by dismissed status
        include_dismissed = self.request.query_params.get('include_dismissed', 'false').lower() == 'true'
        if not include_dismissed:
            queryset = queryset.filter(is_dismissed=False)
        
        return queryset.order_by('-created_at')


class ProductInteractionView(APIView):
    """Track product interactions"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, product_id):
        """Track user interaction with product"""
        product = get_object_or_404(
            ProductSuggestion,
            id=product_id,
            user=request.user
        )
        
        serializer = ProductInteractionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        action = serializer.validated_data['action']
        interest_level = serializer.validated_data.get('interest_level')
        
        # Update product based on action
        if action == 'viewed':
            product.is_viewed = True
        elif action == 'clicked':
            product.is_clicked = True
        elif action == 'dismissed':
            product.is_dismissed = True
        
        if interest_level:
            product.user_interest_level = interest_level
        
        product.save()
        
        return Response({'message': f'Product {action} successfully'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_status(request):
    """Get AI service status"""
    from .ai_adapter import AIAdapterFactory
    
    try:
        adapter = AIAdapterFactory.create_adapter()
        available_providers = AIAdapterFactory.get_available_providers()
        
        return Response({
            'ai_enabled': getattr(settings, 'ENABLE_AI_RECOMMENDATIONS', True),
            'current_provider': adapter.provider_name,
            'available_providers': available_providers,
            'model': adapter.model
        })
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        return Response({
            'ai_enabled': False,
            'error': 'AI service unavailable'
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recommendation_stats(request):
    """Get user's recommendation statistics"""
    user_recommendations = AIRecommendation.objects.filter(user=request.user)
    user_products = ProductSuggestion.objects.filter(user=request.user)
    
    stats = {
        'total_recommendations': user_recommendations.count(),
        'read_recommendations': user_recommendations.filter(is_read=True).count(),
        'rated_recommendations': user_recommendations.filter(user_rating__isnull=False).count(),
        'average_rating': user_recommendations.filter(user_rating__isnull=False).aggregate(
            avg_rating=models.Avg('user_rating')
        )['avg_rating'] or 0,
        'total_product_suggestions': user_products.count(),
        'viewed_products': user_products.filter(is_viewed=True).count(),
        'clicked_products': user_products.filter(is_clicked=True).count(),
    }
    
    return Response(stats)
