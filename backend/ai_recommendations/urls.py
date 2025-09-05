"""
URLs for AI Recommendations API
"""

from django.urls import path
from . import views

app_name = 'ai_recommendations'

urlpatterns = [
    # AI Preferences
    path('preferences/', views.UserAIPreferencesView.as_view(), name='ai_preferences'),
    
    # Recommendations
    path('recommendations/', views.RecommendationListView.as_view(), name='recommendation_list'),
    path('recommendations/generate/', views.GenerateRecommendationView.as_view(), name='generate_recommendation'),
    path('recommendations/<uuid:recommendation_id>/', views.RecommendationDetailView.as_view(), name='recommendation_detail'),
    path('recommendations/<uuid:recommendation_id>/feedback/', views.RecommendationFeedbackView.as_view(), name='recommendation_feedback'),
    
    # Product Suggestions
    path('products/search/', views.ProductSearchView.as_view(), name='product_search'),
    path('products/', views.ProductSuggestionListView.as_view(), name='product_list'),
    path('products/<uuid:product_id>/interact/', views.ProductInteractionView.as_view(), name='product_interaction'),
    
    # Status and Stats
    path('status/', views.ai_status, name='ai_status'),
    path('stats/', views.recommendation_stats, name='recommendation_stats'),
]