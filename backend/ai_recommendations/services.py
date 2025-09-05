"""
AI Recommendation Services
Business logic for generating personalized recommendations and product suggestions
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

from .ai_adapter import AIAdapterFactory, AIResponse
from .models import UserAIPreferences, AIRecommendation, ProductSuggestion, AIInteractionLog
from activities.models import Activity, ActivityCategory
from carbon.models import CarbonCalculation

User = get_user_model()
logger = logging.getLogger(__name__)


class PromptTemplates:
    """Centralized prompt templates for AI interactions"""
    
    @staticmethod
    def daily_coaching_prompt(user_profile: Dict, activity_history: List[Dict], preferences: Dict) -> str:
        """Generate daily coaching prompt"""
        tone = preferences.get('tone_preference', 'encouraging')
        focus_areas = preferences.get('focus_areas', [])
        
        tone_instructions = {
            'encouraging': "Be positive, motivational, and celebrate progress",
            'educational': "Focus on providing facts and educational content",
            'direct': "Be clear, concise, and action-oriented",
            'casual': "Use a friendly, conversational tone"
        }
        
        prompt = f"""
You are an eco-friendly lifestyle coach. {tone_instructions.get(tone, '')}

User Profile:
- Name: {user_profile.get('name', 'User')}
- Focus areas: {', '.join(focus_areas) if focus_areas else 'All areas'}
- Recent CO₂ footprint: {user_profile.get('recent_co2', 0)} kg CO₂e

Recent Activities (last 7 days):
{chr(10).join(f"- {activity['type']}: {activity['co2']} kg CO₂e" for activity in activity_history[:5])}

Please provide:
1. A personalized daily tip (1-2 sentences)
2. One specific actionable recommendation based on their recent activities
3. Encouragement related to their progress

Keep the response under 150 words and make it actionable.
"""
        return prompt.strip()
    
    @staticmethod
    def product_suggestion_prompt(query: str, user_prefs: Dict, category: str = None) -> str:
        """Generate product suggestion prompt"""
        prompt = f"""
You are an eco-friendly product advisor. Help users find sustainable alternatives.

User Query: "{query}"
Category: {category or 'Any'}
User Preferences: {user_prefs}

Please suggest 3 eco-friendly products that match the query. For each product, provide:
1. Product name
2. Brief description (1-2 sentences)
3. Estimated CO₂ savings per year (if applicable)
4. Why this product is environmentally friendly
5. Approximate price range (if known)

Focus on products that are:
- Genuinely sustainable (not greenwashing)
- Practical and widely available
- Good value for money
- Have measurable environmental benefits

Format as JSON with products array.
"""
        return prompt.strip()
    
    @staticmethod
    def habit_improvement_prompt(user_data: Dict, weak_areas: List[str]) -> str:
        """Generate habit improvement suggestions"""
        prompt = f"""
You are a behavior change specialist focused on environmental habits.

User's current patterns:
{json.dumps(user_data, indent=2)}

Areas needing improvement: {', '.join(weak_areas)}

Please provide:
1. One specific habit change suggestion for their biggest opportunity area
2. A simple implementation strategy (how to start)
3. Expected impact if they adopt this change

Be specific, actionable, and focus on one change at a time.
Keep response under 100 words.
"""
        return prompt.strip()


class AIRecommendationService:
    """Service for generating AI-powered recommendations"""
    
    def __init__(self, user: User):
        self.user = user
        self.ai_adapter = AIAdapterFactory.create_adapter()
        self.preferences = self._get_or_create_preferences()
    
    def _get_or_create_preferences(self) -> UserAIPreferences:
        """Get or create user AI preferences"""
        preferences, created = UserAIPreferences.objects.get_or_create(
            user=self.user,
            defaults={
                'ai_recommendations_enabled': False,
                'coaching_frequency': 'weekly',
                'tone_preference': 'encouraging'
            }
        )
        return preferences
    
    def _log_interaction(self, interaction_type: str, prompt: str, response: AIResponse, context: Dict = None):
        """Log AI interaction for monitoring"""
        try:
            AIInteractionLog.objects.create(
                user=self.user,
                interaction_type=interaction_type,
                prompt_text=prompt,
                context_data=context or {},
                ai_provider=response.provider,
                ai_model=response.model,
                response_text=response.content,
                response_metadata=response.metadata,
                response_time_ms=response.response_time_ms,
                token_count=response.token_count,
                cost_estimate=response.cost_estimate,
                success=response.success,
                error_message=response.error_message,
                safety_flagged=response.safety_flagged
            )
        except Exception as e:
            logger.error(f"Failed to log AI interaction: {e}")
    
    def _get_user_profile(self) -> Dict[str, Any]:
        """Build user profile for AI context"""
        # Calculate recent CO₂ footprint
        recent_activities = Activity.objects.filter(
            user=self.user,
            start_timestamp__gte=timezone.now() - timedelta(days=7)
        )
        recent_co2 = sum(
            activity.co2_kg or 0 
            for activity in recent_activities
        )
        
        return {
            'name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.email,
            'recent_co2': round(recent_co2, 2),
            'total_activities': Activity.objects.filter(user=self.user).count(),
            'primary_categories': self._get_primary_categories(),
        }
    
    def _get_primary_categories(self) -> List[str]:
        """Get user's most used activity categories"""
        from django.db.models import Count
        
        categories = Activity.objects.filter(user=self.user).values(
            'category__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        return [cat['category__name'] for cat in categories]
    
    def _get_activity_history(self) -> List[Dict[str, Any]]:
        """Get recent activity history for AI context"""
        recent_activities = Activity.objects.filter(
            user=self.user,
            start_timestamp__gte=timezone.now() - timedelta(days=7)
        ).order_by('-start_timestamp')[:10]
        
        return [
            {
                'type': activity.activity_type,
                'category': activity.category.name,
                'co2': round(activity.co2_kg or 0, 2),
                'date': activity.start_timestamp.date().isoformat(),
                'value': activity.value,
                'unit': activity.unit
            }
            for activity in recent_activities
        ]
    
    def generate_daily_coaching(self) -> Optional[AIRecommendation]:
        """Generate personalized daily coaching recommendation"""
        if not self.preferences.ai_recommendations_enabled:
            logger.info(f"AI recommendations disabled for user {self.user.email}")
            return None
        
        # Build context
        user_profile = self._get_user_profile()
        activity_history = self._get_activity_history()
        preferences_dict = {
            'tone_preference': self.preferences.tone_preference,
            'focus_areas': self.preferences.focus_areas,
            'coaching_frequency': self.preferences.coaching_frequency
        }
        
        # Generate prompt
        prompt = PromptTemplates.daily_coaching_prompt(
            user_profile, activity_history, preferences_dict
        )
        
        # Call AI
        context = {
            'user_profile': user_profile,
            'activity_history': activity_history,
            'preferences': preferences_dict
        }
        
        response = self.ai_adapter.generate_text(prompt, context)
        self._log_interaction('daily_coaching', prompt, response, context)
        
        if not response.success:
            logger.error(f"AI daily coaching failed: {response.error_message}")
            return self._generate_fallback_coaching()
        
        # Create recommendation record
        recommendation = AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='coaching',
            title='Your Daily Eco Tip',
            content=response.content,
            metadata={
                'ai_response': response.metadata,
                'user_context': context
            },
            ai_provider=response.provider,
            ai_model=response.model,
            expires_at=timezone.now() + timedelta(days=1)
        )
        
        return recommendation
    
    def _generate_fallback_coaching(self) -> AIRecommendation:
        """Generate rule-based coaching when AI fails"""
        fallback_tips = [
            {
                'title': 'Transportation Tip',
                'content': 'Consider walking, biking, or using public transport for trips under 3 miles. This can reduce your transportation footprint by up to 50%!'
            },
            {
                'title': 'Energy Saving Tip',  
                'content': 'Unplug electronics when not in use. Even in standby mode, devices consume energy. This simple habit can reduce your home energy use by 5-10%.'
            },
            {
                'title': 'Food Choice Tip',
                'content': 'Try incorporating one plant-based meal into your day. Plant-based foods generally have a lower carbon footprint than meat-based meals.'
            }
        ]
        
        import random
        tip = random.choice(fallback_tips)
        
        return AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='coaching',
            title=tip['title'],
            content=tip['content'],
            metadata={'fallback': True},
            ai_provider='rule_based',
            ai_model='fallback_v1.0',
            expires_at=timezone.now() + timedelta(days=1)
        )
    
    def search_products(self, query: str, category: str = None) -> List[ProductSuggestion]:
        """Search for eco-friendly product suggestions"""
        if not self.preferences.product_suggestions_enabled:
            return []
        
        user_prefs = {
            'focus_areas': self.preferences.focus_areas,
            'tone_preference': self.preferences.tone_preference
        }
        
        prompt = PromptTemplates.product_suggestion_prompt(query, user_prefs, category)
        response = self.ai_adapter.generate_text(prompt)
        
        self._log_interaction('product_search', prompt, response, {'query': query, 'category': category})
        
        if not response.success:
            return self._generate_fallback_products(query, category)
        
        # Parse AI response and create product suggestions
        products = self._parse_product_response(response.content)
        
        suggestions = []
        for product_data in products:
            suggestion = ProductSuggestion.objects.create(
                user=self.user,
                product_name=product_data.get('name', 'Unknown Product'),
                description=product_data.get('description', ''),
                category=category or 'general',
                estimated_co2_savings=product_data.get('co2_savings'),
                price_range=product_data.get('price_range', ''),
                product_url=product_data.get('url', ''),
                ai_confidence_score=product_data.get('confidence', 0.7),
                recommendation_reason=product_data.get('reason', '')
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _parse_product_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse AI product response into structured data"""
        import json
        import re
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get('products', [])
        except json.JSONDecodeError:
            pass
        
        # Fallback: parse as structured text
        products = []
        # Simple text parsing logic here
        return products
    
    def _generate_fallback_products(self, query: str, category: str) -> List[ProductSuggestion]:
        """Generate rule-based product suggestions when AI fails"""
        fallback_products = {
            'energy': [
                {
                    'name': 'LED Light Bulbs',
                    'description': 'Energy-efficient LED bulbs that last 25x longer than incandescent bulbs',
                    'co2_savings': 50.0,
                    'reason': 'LEDs use 75% less energy than traditional bulbs'
                }
            ],
            'transport': [
                {
                    'name': 'Bicycle',
                    'description': 'Zero-emission transportation for short to medium distances',
                    'co2_savings': 1500.0,
                    'reason': 'Replaces car trips with zero emissions'
                }
            ]
        }
        
        products_data = fallback_products.get(category, [
            {
                'name': 'Reusable Water Bottle',
                'description': 'Reduces single-use plastic consumption',
                'co2_savings': 25.0,
                'reason': 'Eliminates disposable plastic bottles'
            }
        ])
        
        suggestions = []
        for product_data in products_data:
            suggestion = ProductSuggestion.objects.create(
                user=self.user,
                product_name=product_data['name'],
                description=product_data['description'],
                category=category or 'general',
                estimated_co2_savings=product_data.get('co2_savings'),
                ai_confidence_score=0.5,  # Lower confidence for fallback
                recommendation_reason=product_data['reason']
            )
            suggestions.append(suggestion)
        
        return suggestions


def get_user_recommendations(user: User, recommendation_type: str = None) -> List[AIRecommendation]:
    """Get existing recommendations for a user"""
    queryset = AIRecommendation.objects.filter(user=user)
    
    if recommendation_type:
        queryset = queryset.filter(recommendation_type=recommendation_type)
    
    # Filter out expired recommendations
    queryset = queryset.filter(
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
    )
    
    return queryset.order_by('-created_at')


def mark_recommendation_read(recommendation_id: str, user: User) -> bool:
    """Mark a recommendation as read"""
    try:
        recommendation = AIRecommendation.objects.get(id=recommendation_id, user=user)
        recommendation.is_read = True
        recommendation.save()
        return True
    except AIRecommendation.DoesNotExist:
        return False


def rate_recommendation(recommendation_id: str, user: User, rating: int, feedback: str = "") -> bool:
    """Rate a recommendation"""
    try:
        recommendation = AIRecommendation.objects.get(id=recommendation_id, user=user)
        recommendation.user_rating = rating
        recommendation.user_feedback = feedback
        recommendation.save()
        return True
    except AIRecommendation.DoesNotExist:
        return False