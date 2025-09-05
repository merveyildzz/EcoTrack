"""
Serializers for AI Recommendations API
"""

from rest_framework import serializers
from .models import UserAIPreferences, AIRecommendation, ProductSuggestion


class UserAIPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for user AI preferences"""
    
    class Meta:
        model = UserAIPreferences
        fields = [
            'ai_recommendations_enabled',
            'product_suggestions_enabled', 
            'data_sharing_consent',
            'coaching_frequency',
            'focus_areas',
            'tone_preference',
            'updated_at'
        ]
        read_only_fields = ['updated_at']
    
    def validate_focus_areas(self, value):
        """Validate focus areas"""
        valid_areas = ['transportation', 'energy', 'food', 'consumption', 'waste']
        if value:
            invalid_areas = [area for area in value if area not in valid_areas]
            if invalid_areas:
                raise serializers.ValidationError(
                    f"Invalid focus areas: {invalid_areas}. Valid options: {valid_areas}"
                )
        return value


class AIRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for AI recommendations"""
    
    class Meta:
        model = AIRecommendation
        fields = [
            'id',
            'recommendation_type',
            'title',
            'content',
            'metadata',
            'ai_provider',
            'ai_model',
            'is_read',
            'is_dismissed',
            'user_rating',
            'user_feedback',
            'created_at',
            'expires_at'
        ]
        read_only_fields = [
            'id', 'ai_provider', 'ai_model', 'created_at'
        ]


class ProductSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for product suggestions"""
    
    class Meta:
        model = ProductSuggestion
        fields = [
            'id',
            'product_name',
            'description',
            'category',
            'estimated_co2_savings',
            'price_range',
            'product_url',
            'image_url',
            'vendor',
            'ai_confidence_score',
            'recommendation_reason',
            'is_viewed',
            'is_clicked',
            'is_dismissed',
            'user_interest_level',
            'created_at'
        ]
        read_only_fields = [
            'id', 'ai_confidence_score', 'recommendation_reason', 'created_at'
        ]


class GenerateRecommendationSerializer(serializers.Serializer):
    """Serializer for generating recommendations"""
    recommendation_type = serializers.ChoiceField(
        choices=['daily_tip', 'coaching', 'habit_improvement', 'goal_adjustment'],
        default='coaching'
    )
    force_regenerate = serializers.BooleanField(default=False)


class ProductSearchSerializer(serializers.Serializer):
    """Serializer for product search requests"""
    query = serializers.CharField(max_length=200)
    category = serializers.CharField(max_length=100, required=False, allow_blank=True)
    max_results = serializers.IntegerField(min_value=1, max_value=20, default=5)


class RecommendationFeedbackSerializer(serializers.Serializer):
    """Serializer for recommendation feedback"""
    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(max_length=500, required=False, allow_blank=True)


class ProductInteractionSerializer(serializers.Serializer):
    """Serializer for product interaction tracking"""
    action = serializers.ChoiceField(choices=['viewed', 'clicked', 'dismissed'])
    interest_level = serializers.ChoiceField(
        choices=['very_high', 'high', 'medium', 'low', 'not_interested'],
        required=False,
        allow_blank=True
    )