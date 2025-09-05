"""
Advanced analytics and insights engine for EcoTrack
Provides trend analysis, predictions, and personalized insights
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Sum, Count, Q
from typing import Dict, List, Any, Optional
import logging

from activities.models import Activity, ActivityCategory
from social.models import UserStats, Challenge, ChallengeParticipation
from .models import UserInsight, TrendAnalysis

logger = logging.getLogger(__name__)


class InsightsEngine:
    """Main engine for generating user insights and recommendations"""
    
    def __init__(self, user):
        self.user = user
        self.now = timezone.now()
        
    def generate_weekly_insights(self) -> Dict[str, Any]:
        """Generate comprehensive weekly insights for user"""
        week_start = self.now - timedelta(days=7)
        
        activities = Activity.objects.filter(
            user=self.user,
            created_at__gte=week_start
        ).select_related('category')
        
        if not activities.exists():
            return self._empty_insights("No activities this week")
            
        # Convert to DataFrame for analysis
        df = self._activities_to_dataframe(activities)
        
        insights = {
            'period': 'weekly',
            'start_date': week_start.isoformat(),
            'end_date': self.now.isoformat(),
            'summary': self._generate_weekly_summary(df),
            'trends': self._analyze_trends(df),
            'achievements': self._identify_achievements(df),
            'recommendations': self._generate_recommendations(df),
            'comparisons': self._generate_comparisons(df),
            'predictions': self._generate_predictions(df),
        }
        
        return insights
    
    def generate_monthly_insights(self) -> Dict[str, Any]:
        """Generate monthly insights with deeper analysis"""
        month_start = self.now.replace(day=1)
        
        activities = Activity.objects.filter(
            user=self.user,
            created_at__gte=month_start
        ).select_related('category')
        
        if not activities.exists():
            return self._empty_insights("No activities this month")
            
        df = self._activities_to_dataframe(activities)
        
        insights = {
            'period': 'monthly',
            'start_date': month_start.isoformat(),
            'end_date': self.now.isoformat(),
            'summary': self._generate_monthly_summary(df),
            'category_analysis': self._analyze_by_category(df),
            'patterns': self._identify_patterns(df),
            'goals_progress': self._analyze_goals_progress(df),
            'social_comparison': self._generate_social_comparison(),
            'environmental_impact': self._calculate_environmental_impact(df),
        }
        
        return insights
    
    def _activities_to_dataframe(self, activities) -> pd.DataFrame:
        """Convert activities queryset to pandas DataFrame"""
        data = []
        for activity in activities:
            data.append({
                'date': activity.created_at.date(),
                'datetime': activity.created_at,
                'category': activity.category.category_type,
                'activity_type': activity.activity_type,
                'co2_kg': float(activity.co2_kg or 0),
                'value': float(activity.value),
                'unit': activity.unit,
                'day_of_week': activity.created_at.weekday(),
                'hour': activity.created_at.hour,
            })
        
        return pd.DataFrame(data)
    
    def _generate_weekly_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate weekly summary statistics"""
        total_co2 = df['co2_kg'].sum()
        avg_daily_co2 = df.groupby('date')['co2_kg'].sum().mean()
        activity_count = len(df)
        active_days = df['date'].nunique()
        
        # Find best and worst days
        daily_co2 = df.groupby('date')['co2_kg'].sum()
        best_day = daily_co2.idxmin() if len(daily_co2) > 0 else None
        worst_day = daily_co2.idxmax() if len(daily_co2) > 0 else None
        
        return {
            'total_co2_kg': round(total_co2, 2),
            'avg_daily_co2': round(avg_daily_co2, 2),
            'activity_count': activity_count,
            'active_days': active_days,
            'consistency_rate': round((active_days / 7) * 100, 1),
            'best_day': {
                'date': best_day.isoformat() if best_day else None,
                'co2_kg': round(daily_co2.min(), 2) if len(daily_co2) > 0 else 0
            },
            'worst_day': {
                'date': worst_day.isoformat() if worst_day else None,
                'co2_kg': round(daily_co2.max(), 2) if len(daily_co2) > 0 else 0
            }
        }
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends in user behavior"""
        if len(df) < 3:
            return {'message': 'Not enough data for trend analysis'}
            
        daily_co2 = df.groupby('date')['co2_kg'].sum().sort_index()
        
        # Calculate trend direction
        x = np.arange(len(daily_co2))
        y = daily_co2.values
        trend_slope = np.polyfit(x, y, 1)[0] if len(x) > 1 else 0
        
        trend_direction = 'improving' if trend_slope < 0 else 'worsening' if trend_slope > 0 else 'stable'
        
        return {
            'direction': trend_direction,
            'slope': round(trend_slope, 4),
            'improvement_rate': round(abs(trend_slope) * 7, 2),  # Weekly change
            'volatility': round(daily_co2.std(), 2),
            'most_active_day': df.groupby('day_of_week')['co2_kg'].sum().idxmax(),
            'most_active_hour': df.groupby('hour')['co2_kg'].sum().idxmax(),
        }
    
    def _identify_achievements(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify achievements and milestones"""
        achievements = []
        
        # Daily streak
        active_days = df['date'].nunique()
        if active_days >= 7:
            achievements.append({
                'type': 'consistency',
                'title': 'Full Week Warrior',
                'description': 'Logged activities every day this week!',
                'icon': '🔥'
            })
        
        # Low carbon days
        daily_co2 = df.groupby('date')['co2_kg'].sum()
        low_carbon_days = (daily_co2 < daily_co2.mean() * 0.8).sum()
        
        if low_carbon_days >= 3:
            achievements.append({
                'type': 'impact',
                'title': 'Eco Champion',
                'description': f'{low_carbon_days} low-carbon days this week!',
                'icon': '🌱'
            })
        
        # Category diversity
        categories = df['category'].nunique()
        if categories >= 4:
            achievements.append({
                'type': 'diversity',
                'title': 'Well-Rounded Eco Warrior',
                'description': f'Tracked {categories} different activity categories',
                'icon': '🌈'
            })
        
        return achievements
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Category-specific recommendations
        category_co2 = df.groupby('category')['co2_kg'].sum().sort_values(ascending=False)
        
        if len(category_co2) > 0:
            highest_category = category_co2.index[0]
            highest_value = category_co2.iloc[0]
            
            category_tips = {
                'transportation': 'Try carpooling, public transit, or cycling for short trips',
                'energy': 'Consider LED bulbs, unplugging devices, or adjusting thermostat',
                'food': 'Try plant-based meals or locally sourced ingredients',
                'consumption': 'Focus on buying only what you need and choosing sustainable brands',
                'waste': 'Increase recycling and composting efforts'
            }
            
            recommendations.append({
                'type': 'focus_area',
                'category': highest_category,
                'title': f'Focus on {highest_category.title()}',
                'description': category_tips.get(highest_category, 'Consider sustainable alternatives'),
                'potential_impact': round(highest_value * 0.2, 2),  # 20% potential reduction
                'priority': 'high'
            })
        
        # Time-based recommendations
        hour_activity = df.groupby('hour')['co2_kg'].sum()
        if len(hour_activity) > 0:
            peak_hour = hour_activity.idxmax()
            
            if 7 <= peak_hour <= 9:
                recommendations.append({
                    'type': 'timing',
                    'title': 'Morning Commute Optimization',
                    'description': 'Your highest impact is during morning hours. Consider sustainable commuting options.',
                    'priority': 'medium'
                })
        
        return recommendations
    
    def _generate_comparisons(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compare user performance with averages"""
        total_co2 = df['co2_kg'].sum()
        
        # Get platform averages (mock data for now)
        platform_avg = self._get_platform_averages()
        
        return {
            'vs_platform_average': {
                'your_co2': round(total_co2, 2),
                'platform_avg': platform_avg['weekly_co2'],
                'performance': 'above_average' if total_co2 < platform_avg['weekly_co2'] else 'below_average',
                'percentile': self._calculate_percentile(total_co2)
            },
            'vs_last_week': self._compare_with_last_week(total_co2)
        }
    
    def _generate_predictions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictions for next week"""
        if len(df) < 5:
            return {'message': 'Not enough data for predictions'}
            
        daily_co2 = df.groupby('date')['co2_kg'].sum()
        
        # Simple trend-based prediction
        trend = np.polyfit(range(len(daily_co2)), daily_co2.values, 1)[0]
        current_avg = daily_co2.mean()
        predicted_next_week = current_avg + (trend * 7)
        
        return {
            'next_week_co2': round(max(0, predicted_next_week), 2),
            'confidence': 'medium',
            'trend_direction': 'improving' if trend < 0 else 'worsening',
            'recommendation': 'Keep up the good work!' if trend < 0 else 'Consider focusing on high-impact areas'
        }
    
    def _empty_insights(self, message: str) -> Dict[str, Any]:
        """Return empty insights structure"""
        return {
            'message': message,
            'recommendations': [{
                'type': 'getting_started',
                'title': 'Start Tracking',
                'description': 'Log your first activity to begin getting personalized insights!',
                'priority': 'high'
            }]
        }
    
    def _get_platform_averages(self) -> Dict[str, float]:
        """Get platform-wide averages (cached)"""
        # This would typically be cached and updated periodically
        return {
            'weekly_co2': 25.0,
            'daily_activities': 2.5,
            'categories_used': 3.2
        }
    
    def _calculate_percentile(self, user_co2: float) -> int:
        """Calculate user's percentile ranking"""
        # Mock implementation - would use actual user data
        if user_co2 < 15:
            return 90
        elif user_co2 < 25:
            return 70
        elif user_co2 < 35:
            return 50
        else:
            return 30
    
    def _compare_with_last_week(self, current_co2: float) -> Dict[str, Any]:
        """Compare with last week's performance"""
        last_week_start = self.now - timedelta(days=14)
        last_week_end = self.now - timedelta(days=7)
        
        last_week_co2 = Activity.objects.filter(
            user=self.user,
            created_at__range=[last_week_start, last_week_end]
        ).aggregate(total=Sum('co2_kg'))['total'] or 0
        
        change = current_co2 - float(last_week_co2)
        change_percent = (change / float(last_week_co2)) * 100 if last_week_co2 > 0 else 0
        
        return {
            'last_week_co2': round(float(last_week_co2), 2),
            'change_kg': round(change, 2),
            'change_percent': round(change_percent, 1),
            'trend': 'improved' if change < 0 else 'worsened' if change > 0 else 'stable'
        }
    
    def _generate_monthly_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate monthly summary with additional metrics"""
        summary = self._generate_weekly_summary(df)
        
        # Add monthly-specific metrics
        summary.update({
            'weeks_active': df['date'].dt.isocalendar().week.nunique(),
            'avg_weekend_co2': df[df['day_of_week'].isin([5, 6])]['co2_kg'].mean(),
            'avg_weekday_co2': df[~df['day_of_week'].isin([5, 6])]['co2_kg'].mean(),
        })
        
        return summary
    
    def _analyze_by_category(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detailed category analysis"""
        category_stats = df.groupby('category').agg({
            'co2_kg': ['sum', 'mean', 'count'],
            'date': 'nunique'
        }).round(2)
        
        return category_stats.to_dict('index')
    
    def _identify_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify behavioral patterns"""
        patterns = {}
        
        # Weekend vs weekday patterns
        weekday_avg = df[~df['day_of_week'].isin([5, 6])]['co2_kg'].mean()
        weekend_avg = df[df['day_of_week'].isin([5, 6])]['co2_kg'].mean()
        
        patterns['weekend_vs_weekday'] = {
            'weekday_avg': round(weekday_avg, 2),
            'weekend_avg': round(weekend_avg, 2),
            'pattern': 'higher_weekend' if weekend_avg > weekday_avg else 'higher_weekday'
        }
        
        return patterns
    
    def _analyze_goals_progress(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze progress towards goals"""
        # This would integrate with user-defined goals
        total_co2 = df['co2_kg'].sum()
        
        # Mock monthly goal of 100kg CO2
        monthly_goal = 100.0
        progress = (monthly_goal - total_co2) / monthly_goal * 100
        
        return {
            'monthly_co2_goal': monthly_goal,
            'current_co2': round(total_co2, 2),
            'remaining': round(monthly_goal - total_co2, 2),
            'progress_percent': round(max(0, progress), 1),
            'on_track': progress > 0
        }
    
    def _generate_social_comparison(self) -> Dict[str, Any]:
        """Compare with social network performance"""
        # Mock social comparison data
        return {
            'friends_avg': 28.5,
            'your_rank': 3,
            'total_friends': 12,
            'better_than_percent': 75
        }