import logging
from decimal import Decimal
from typing import Dict, Any, Optional, Tuple
from django.db.models import Q
from .models import EmissionFactor, UnitConversion, CarbonCalculation, CalculationLog

logger = logging.getLogger(__name__)


class CarbonCalculationEngine:
    """
    Carbon calculation engine with pluggable architecture for deterministic carbon footprint calculations.
    """
    
    def __init__(self):
        self.calculation_version = "1.0"
    
    def calculate(self, activity, user_region: str = 'global') -> Dict[str, Any]:
        """
        Calculate carbon footprint for a given activity.
        
        Args:
            activity: Activity instance
            user_region: User's region for localized emission factors
            
        Returns:
            Dict with calculation results including co2_kg, breakdown, and metadata
        """
        start_time = logger.time if hasattr(logger, 'time') else None
        
        try:
            # Step 1: Normalize input units
            normalized_value, normalized_unit = self._normalize_units(
                activity.value, 
                activity.unit, 
                activity.category.category_type
            )
            
            # Step 2: Find best emission factor
            emission_factor = self._find_emission_factor(
                category=activity.category.category_type,
                subcategory=activity.category.name,
                activity_type=activity.activity_type,
                unit=normalized_unit,
                region=user_region
            )
            
            if not emission_factor:
                # Fallback to global factors
                emission_factor = self._find_emission_factor(
                    category=activity.category.category_type,
                    subcategory=activity.category.name,
                    activity_type=activity.activity_type,
                    unit=normalized_unit,
                    region='global'
                )
            
            if not emission_factor:
                raise ValueError(f"No emission factor found for {activity.activity_type}")
            
            # Step 3: Perform calculation
            co2_kg = self._calculate_emissions(normalized_value, emission_factor)
            
            # Step 4: Calculate confidence score
            confidence_score = self._calculate_confidence(emission_factor, activity)
            
            # Step 5: Create breakdown
            breakdown = self._create_breakdown(co2_kg, emission_factor)
            
            # Step 6: Save calculation record
            calculation = CarbonCalculation.objects.create(
                activity=activity,
                emission_factor=emission_factor,
                input_value=activity.value,
                input_unit=activity.unit,
                normalized_value=normalized_value,
                normalized_unit=normalized_unit,
                co2_kg=co2_kg,
                calculation_method='direct_multiplication',
                confidence_score=confidence_score,
                metadata={
                    'version': self.calculation_version,
                    'region': user_region,
                    'fallback_used': user_region != emission_factor.region
                }
            )
            
            result = {
                'co2_kg': float(co2_kg),
                'breakdown': breakdown,
                'factor_used': {
                    'value': float(emission_factor.factor_value),
                    'unit': emission_factor.unit,
                    'source': emission_factor.source,
                    'version': emission_factor.version,
                    'region': emission_factor.region,
                    'confidence_level': emission_factor.confidence_level
                },
                'confidence': confidence_score,
                'calculation_id': str(calculation.id)
            }
            
            # Log successful calculation
            self._log_calculation(
                activity.id, 
                {
                    'input_value': float(activity.value),
                    'input_unit': activity.unit,
                    'category': activity.category.category_type,
                    'activity_type': activity.activity_type
                },
                result,
                'success',
                emission_factor=emission_factor,
                processing_time_ms=None  # Calculate if timing is available
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Carbon calculation failed for activity {activity.id}: {str(e)}")
            
            # Log failed calculation
            self._log_calculation(
                activity.id,
                {
                    'input_value': float(activity.value),
                    'input_unit': activity.unit,
                    'category': activity.category.category_type,
                    'activity_type': activity.activity_type
                },
                None,
                'error',
                error_message=str(e),
                processing_time_ms=None
            )
            
            raise
    
    def _normalize_units(self, value: Decimal, unit: str, category: str) -> Tuple[Decimal, str]:
        """
        Normalize units to standard units for calculations.
        """
        # Try to find unit conversion
        conversion = UnitConversion.objects.filter(
            from_unit=unit,
            category=category,
            is_active=True
        ).first()
        
        if conversion:
            normalized_value = value * conversion.conversion_factor
            return normalized_value, conversion.to_unit
        
        # No conversion needed, return as-is
        return value, unit
    
    def _find_emission_factor(self, category: str, subcategory: str, activity_type: str, 
                            unit: str, region: str) -> Optional[EmissionFactor]:
        """
        Find the best emission factor for given parameters.
        """
        # First, try exact match
        factor = EmissionFactor.objects.filter(
            category=category,
            subcategory=subcategory,
            activity_type=activity_type,
            unit=unit,
            region=region,
            is_active=True
        ).order_by('-year', '-confidence_level').first()
        
        if factor:
            return factor
        
        # Try broader match without activity_type
        factor = EmissionFactor.objects.filter(
            category=category,
            subcategory=subcategory,
            unit=unit,
            region=region,
            is_active=True
        ).order_by('-year', '-confidence_level').first()
        
        if factor:
            return factor
        
        # Try category-level match
        factor = EmissionFactor.objects.filter(
            category=category,
            unit=unit,
            region=region,
            is_active=True
        ).order_by('-year', '-confidence_level').first()
        
        return factor
    
    def _calculate_emissions(self, value: Decimal, emission_factor: EmissionFactor) -> Decimal:
        """
        Perform the actual emission calculation.
        """
        return value * emission_factor.factor_value
    
    def _calculate_confidence(self, emission_factor: EmissionFactor, activity) -> Decimal:
        """
        Calculate confidence score based on various factors.
        """
        base_confidence = {
            'high': Decimal('0.9'),
            'medium': Decimal('0.7'),
            'low': Decimal('0.5')
        }.get(emission_factor.confidence_level, Decimal('0.5'))
        
        # Adjust based on data recency
        current_year = 2025  # Should be dynamic
        age_penalty = max(0, (current_year - emission_factor.year) * 0.05)
        confidence = base_confidence - Decimal(str(age_penalty))
        
        # Ensure confidence is between 0 and 1
        return max(Decimal('0.1'), min(Decimal('1.0'), confidence))
    
    def _create_breakdown(self, total_co2_kg: Decimal, emission_factor: EmissionFactor) -> Dict[str, float]:
        """
        Create CO2 breakdown by scope.
        """
        breakdown = {
            'total': float(total_co2_kg),
            'scope_1': 0.0,
            'scope_2': 0.0,
            'scope_3': 0.0
        }
        
        # Assign to appropriate scope
        scope_key = emission_factor.scope.replace('scope_', 'scope_')
        if scope_key in breakdown:
            breakdown[scope_key] = float(total_co2_kg)
        
        return breakdown
    
    def _log_calculation(self, activity_id, input_data: Dict, output_data: Optional[Dict], 
                        status: str, emission_factor=None, error_message: str = '', 
                        processing_time_ms: Optional[int] = None):
        """
        Log calculation for debugging and audit purposes.
        """
        try:
            CalculationLog.objects.create(
                activity_id=activity_id,
                input_data=input_data,
                output_data=output_data,
                status=status,
                error_message=error_message,
                processing_time_ms=processing_time_ms,
                emission_factor_used=emission_factor,
                calculation_version=self.calculation_version
            )
        except Exception as e:
            logger.error(f"Failed to log calculation: {str(e)}")


class EstimationEngine:
    """
    Estimation engine for missing data and heuristic calculations.
    """
    
    def estimate_missing_activity_data(self, activity_type: str, 
                                     available_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate missing activity data using heuristics and ML models.
        """
        estimates = {}
        
        if activity_type == 'transportation':
            estimates.update(self._estimate_transportation_data(available_data))
        elif activity_type == 'energy':
            estimates.update(self._estimate_energy_data(available_data))
        elif activity_type == 'food':
            estimates.update(self._estimate_food_data(available_data))
        
        return estimates
    
    def _estimate_transportation_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate transportation-related missing data.
        """
        estimates = {}
        
        # Estimate distance from time if missing
        if 'duration_minutes' in data and 'distance_km' not in data:
            # Average speed estimates by mode
            speed_estimates = {
                'walking': 5,  # km/h
                'cycling': 15,
                'bus': 25,
                'train': 60,
                'car': 50
            }
            
            mode = data.get('mode', 'car').lower()
            speed = speed_estimates.get(mode, 50)
            estimates['distance_km'] = (data['duration_minutes'] / 60) * speed
        
        return estimates
    
    def _estimate_energy_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate energy-related missing data.
        """
        # Implementation for energy data estimation
        return {}
    
    def _estimate_food_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate food-related missing data.
        """
        # Implementation for food data estimation
        return {}


# Factory function to get calculation engine
def get_calculation_engine() -> CarbonCalculationEngine:
    """
    Factory function to get the appropriate calculation engine.
    """
    return CarbonCalculationEngine()


def get_estimation_engine() -> EstimationEngine:
    """
    Factory function to get the estimation engine.
    """
    return EstimationEngine()