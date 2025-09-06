"""
Experimentation and Personalization Services
"""
import logging
import random
from typing import Dict, Any, Optional, List
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Avg
from .models import (
    FeatureFlag, Experiment, ExperimentVariant, ExperimentAssignment,
    ExperimentMetric, ExperimentEvent, PersonalizationProfile
)

User = get_user_model()
logger = logging.getLogger('ecotrack.experimentation')


class FeatureFlagService:
    """Service for managing feature flags"""
    
    @staticmethod
    def is_enabled(flag_name: str, user) -> bool:
        """Check if feature flag is enabled for user"""
        try:
            flag = FeatureFlag.objects.get(name=flag_name, is_active=True)
            return flag.is_enabled_for_user(user)
        except FeatureFlag.DoesNotExist:
            return False
    
    @staticmethod
    def get_enabled_flags(user) -> List[str]:
        """Get all enabled flags for user"""
        flags = FeatureFlag.objects.filter(is_active=True)
        enabled_flags = []
        
        for flag in flags:
            if flag.is_enabled_for_user(user):
                enabled_flags.append(flag.name)
        
        return enabled_flags
    
    @staticmethod
    def create_flag(name: str, description: str, rollout_percentage: float = 0.0, created_by=None) -> FeatureFlag:
        """Create a new feature flag"""
        flag = FeatureFlag.objects.create(
            name=name,
            description=description,
            rollout_percentage=rollout_percentage,
            created_by=created_by
        )
        
        logger.info(f"Created feature flag: {name} with {rollout_percentage}% rollout")
        return flag


class ExperimentService:
    """Service for managing A/B testing experiments"""
    
    @staticmethod
    def get_user_variant(experiment_name: str, user) -> Optional[ExperimentVariant]:
        """Get user's variant assignment for experiment"""
        try:
            experiment = Experiment.objects.get(name=experiment_name, status='running')
            return experiment.get_variant_for_user(user)
        except Experiment.DoesNotExist:
            return None
    
    @staticmethod
    def assign_user_to_variant(experiment: Experiment, user) -> Optional[ExperimentVariant]:
        """Assign user to experiment variant"""
        if not experiment.is_running:
            return None
        
        variants = list(experiment.variants.all())
        if not variants:
            return None
        
        # Weighted random selection
        total_weight = sum(v.weight for v in variants)
        if total_weight == 0:
            return random.choice(variants)
        
        # Normalize weights
        weights = [v.weight / total_weight for v in variants]
        
        # Use user ID for consistent assignment
        user_hash = hash(f"{experiment.id}:{user.id}")
        random.seed(user_hash)
        
        selected_variant = random.choices(variants, weights=weights)[0]
        
        # Create assignment
        ExperimentAssignment.objects.get_or_create(
            experiment=experiment,
            user=user,
            defaults={'variant': selected_variant}
        )
        
        return selected_variant
    
    @staticmethod
    def track_event(experiment_name: str, user, event_name: str, 
                   event_value: float = 1.0, properties: Dict[str, Any] = None):
        """Track an event for experiment analysis"""
        try:
            experiment = Experiment.objects.get(name=experiment_name)
            assignment = ExperimentAssignment.objects.get(experiment=experiment, user=user)
            
            # Find matching metric
            try:
                metric = ExperimentMetric.objects.get(experiment=experiment, name=event_name)
            except ExperimentMetric.DoesNotExist:
                # Create metric if it doesn't exist
                metric = ExperimentMetric.objects.create(
                    experiment=experiment,
                    name=event_name,
                    metric_type='custom'
                )
            
            # Track event
            ExperimentEvent.objects.create(
                experiment=experiment,
                user=user,
                variant=assignment.variant,
                metric=metric,
                event_name=event_name,
                event_value=event_value,
                properties=properties or {}
            )
            
            logger.debug(f"Tracked event {event_name} for user {user.id} in experiment {experiment_name}")
            
        except (Experiment.DoesNotExist, ExperimentAssignment.DoesNotExist):
            # User not in experiment, ignore
            pass
    
    @staticmethod
    def get_experiment_results(experiment: Experiment) -> Dict[str, Any]:
        """Get experiment results and statistics"""
        variants = list(experiment.variants.all())
        metrics = list(experiment.metrics.all())
        
        results = {
            'experiment': experiment.name,
            'status': experiment.status,
            'variants': [],
            'total_users': ExperimentAssignment.objects.filter(experiment=experiment).count()
        }
        
        for variant in variants:
            variant_data = {
                'name': variant.name,
                'users': ExperimentAssignment.objects.filter(
                    experiment=experiment, variant=variant
                ).count(),
                'metrics': {}
            }
            
            for metric in metrics:
                events = ExperimentEvent.objects.filter(
                    experiment=experiment,
                    variant=variant,
                    metric=metric
                )
                
                if events.exists():
                    variant_data['metrics'][metric.name] = {
                        'total_events': events.count(),
                        'unique_users': events.values('user').distinct().count(),
                        'avg_value': events.aggregate(avg=Avg('event_value'))['avg'] or 0,
                        'conversion_rate': (
                            events.values('user').distinct().count() / variant_data['users'] * 100
                            if variant_data['users'] > 0 else 0
                        )
                    }
                else:
                    variant_data['metrics'][metric.name] = {
                        'total_events': 0,
                        'unique_users': 0,
                        'avg_value': 0,
                        'conversion_rate': 0
                    }
            
            results['variants'].append(variant_data)
        
        return results


class PersonalizationService:
    """Service for user personalization"""
    
    @staticmethod
    def get_or_create_profile(user) -> PersonalizationProfile:
        """Get or create user personalization profile"""
        profile, created = PersonalizationProfile.objects.get_or_create(user=user)
        
        if created:
            PersonalizationService.update_profile(profile)
        
        return profile
    
    @staticmethod
    def update_profile(profile: PersonalizationProfile):
        """Update user profile based on behavior"""
        user = profile.user
        
        # Update activity frequency
        from activities.models import Activity
        from datetime import timedelta
        
        week_ago = timezone.now() - timedelta(days=7)
        weekly_activities = Activity.objects.filter(
            user=user,
            created_at__gte=week_ago
        ).count()
        
        if weekly_activities < 3:
            profile.activity_frequency = 'low'
        elif weekly_activities <= 7:
            profile.activity_frequency = 'medium'
        else:
            profile.activity_frequency = 'high'
        
        # Update preferred categories
        top_categories = Activity.objects.filter(user=user).values(
            'category__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        profile.preferred_categories = [
            cat['category__name'] for cat in top_categories
        ]
        
        # Update engagement scores
        profile.ai_engagement_score = PersonalizationService._calculate_ai_engagement(user)
        profile.social_engagement_score = PersonalizationService._calculate_social_engagement(user)
        profile.challenge_completion_rate = PersonalizationService._calculate_challenge_completion(user)
        
        # Update segments
        profile.update_segments()
        
        profile.save()
        logger.info(f"Updated personalization profile for user {user.id}")
    
    @staticmethod
    def _calculate_ai_engagement(user) -> float:
        """Calculate AI engagement score (0-1)"""
        try:
            from ai_recommendations.models import UserRecommendation
            
            total_recommendations = UserRecommendation.objects.filter(user=user).count()
            if total_recommendations == 0:
                return 0.0
            
            clicked_recommendations = UserRecommendation.objects.filter(
                user=user,
                clicked_at__isnull=False
            ).count()
            
            return clicked_recommendations / total_recommendations
        except:
            return 0.0
    
    @staticmethod
    def _calculate_social_engagement(user) -> float:
        """Calculate social engagement score (0-1)"""
        try:
            from social.models import ChallengeParticipation, UserBadge
            
            # Combine multiple social metrics
            participations = ChallengeParticipation.objects.filter(user=user).count()
            badges = UserBadge.objects.filter(user=user).count()
            
            # Normalize to 0-1 scale (arbitrary thresholds)
            participation_score = min(participations / 10.0, 1.0)
            badge_score = min(badges / 5.0, 1.0)
            
            return (participation_score + badge_score) / 2.0
        except:
            return 0.0
    
    @staticmethod
    def _calculate_challenge_completion(user) -> float:
        """Calculate challenge completion rate (0-1)"""
        try:
            from social.models import ChallengeParticipation
            
            total_challenges = ChallengeParticipation.objects.filter(user=user).count()
            if total_challenges == 0:
                return 0.0
            
            completed_challenges = ChallengeParticipation.objects.filter(
                user=user,
                is_completed=True
            ).count()
            
            return completed_challenges / total_challenges
        except:
            return 0.0
    
    @staticmethod
    def get_personalized_recommendations(user, count: int = 5) -> List[Dict[str, Any]]:
        """Get personalized recommendations for user"""
        profile = PersonalizationService.get_or_create_profile(user)
        
        recommendations = []
        
        # Recommendation based on segments
        if 'power_user' in profile.segments:
            recommendations.extend([
                {
                    'type': 'challenge',
                    'title': 'Join Advanced Carbon Challenge',
                    'description': 'Ready for a bigger impact? Try our advanced challenges.',
                    'priority': 'high'
                },
                {
                    'type': 'feature',
                    'title': 'Track Corporate Activities',
                    'description': 'Expand your tracking to include workplace activities.',
                    'priority': 'medium'
                }
            ])
        
        if 'casual_user' in profile.segments:
            recommendations.extend([
                {
                    'type': 'motivation',
                    'title': 'Small Steps, Big Impact',
                    'description': 'Even small changes make a difference. Log one activity today!',
                    'priority': 'high'
                }
            ])
        
        if 'ai_engaged' in profile.segments:
            recommendations.extend([
                {
                    'type': 'ai_insight',
                    'title': 'Your Personalized CO₂ Insights',
                    'description': 'Get AI-powered analysis of your carbon footprint patterns.',
                    'priority': 'medium'
                }
            ])
        
        # Category-based recommendations
        if profile.preferred_categories:
            for category in profile.preferred_categories[:2]:
                recommendations.append({
                    'type': 'category_tip',
                    'title': f'Optimize Your {category} Impact',
                    'description': f'Discover new ways to reduce emissions in {category}.',
                    'priority': 'low',
                    'category': category
                })
        
        # Sort by priority and return top recommendations
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return recommendations[:count]


class ABTestingDecorator:
    """Decorator for A/B testing different implementations"""
    
    def __init__(self, experiment_name: str, variants: Dict[str, callable]):
        self.experiment_name = experiment_name
        self.variants = variants
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # Get user from request or args
            user = None
            if args and hasattr(args[0], 'user'):
                user = args[0].user
            elif 'user' in kwargs:
                user = kwargs['user']
            
            if not user:
                return func(*args, **kwargs)
            
            # Get variant
            variant = ExperimentService.get_user_variant(self.experiment_name, user)
            
            if variant and variant.name in self.variants:
                # Track exposure
                ExperimentService.track_event(
                    self.experiment_name, 
                    user, 
                    'exposure',
                    properties={'function': func.__name__}
                )
                
                # Call variant implementation
                return self.variants[variant.name](*args, **kwargs)
            
            # Default implementation
            return func(*args, **kwargs)
        
        return wrapper