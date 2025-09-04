import uuid
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class EmissionFactor(models.Model):
    CATEGORY_CHOICES = [
        ('transportation', 'Transportation'),
        ('energy', 'Energy'), 
        ('food', 'Food'),
        ('consumption', 'Consumption'),
        ('waste', 'Waste'),
    ]
    
    SCOPE_CHOICES = [
        ('scope_1', 'Scope 1 - Direct'),
        ('scope_2', 'Scope 2 - Indirect Energy'),
        ('scope_3', 'Scope 3 - Other Indirect'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=100)
    activity_type = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)
    factor_value = models.DecimalField(max_digits=15, decimal_places=6, validators=[MinValueValidator(0)])
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES, default='scope_3')
    source = models.CharField(max_length=200)
    source_url = models.URLField(blank=True)
    region = models.CharField(max_length=50, default='global')
    year = models.IntegerField()
    version = models.CharField(max_length=20, default='1.0')
    is_active = models.BooleanField(default=True)
    confidence_level = models.CharField(max_length=10, default='medium',
                                      choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'emission_factors'
        unique_together = ['category', 'subcategory', 'activity_type', 'unit', 'region', 'version']
        indexes = [
            models.Index(fields=['category', 'subcategory', 'activity_type']),
            models.Index(fields=['is_active', 'year']),
            models.Index(fields=['region']),
        ]
        ordering = ['-year', '-updated_at']
        
    def __str__(self):
        return f"{self.category} - {self.subcategory}: {self.factor_value} kg CO2e/{self.unit}"


class CarbonCalculation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.OneToOneField('activities.Activity', on_delete=models.CASCADE, related_name='calculation')
    emission_factor = models.ForeignKey(EmissionFactor, on_delete=models.CASCADE, related_name='calculations')
    input_value = models.DecimalField(max_digits=10, decimal_places=3)
    input_unit = models.CharField(max_length=20)
    normalized_value = models.DecimalField(max_digits=10, decimal_places=3)
    normalized_unit = models.CharField(max_length=20)
    co2_kg = models.DecimalField(max_digits=10, decimal_places=3)
    calculation_method = models.CharField(max_length=50, default='direct_multiplication')
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.5'))
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'carbon_calculations'
        indexes = [
            models.Index(fields=['activity']),
            models.Index(fields=['emission_factor']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return f"Calculation for {self.activity}: {self.co2_kg}kg CO2"


class CalculationLog(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('fallback', 'Fallback Used'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity_id = models.UUIDField()
    input_data = models.JSONField()
    output_data = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True)
    processing_time_ms = models.IntegerField(null=True, blank=True)
    emission_factor_used = models.ForeignKey(EmissionFactor, on_delete=models.SET_NULL, null=True, blank=True)
    calculation_version = models.CharField(max_length=20, default='1.0')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'calculation_logs'
        indexes = [
            models.Index(fields=['activity_id']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Log {self.activity_id[:8]} - {self.status}"


class UnitConversion(models.Model):
    from_unit = models.CharField(max_length=20)
    to_unit = models.CharField(max_length=20)
    category = models.CharField(max_length=20)
    conversion_factor = models.DecimalField(max_digits=15, decimal_places=6)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'unit_conversions'
        unique_together = ['from_unit', 'to_unit', 'category']
        indexes = [
            models.Index(fields=['from_unit', 'category']),
            models.Index(fields=['is_active']),
        ]
        
    def __str__(self):
        return f"{self.from_unit} → {self.to_unit} ({self.category}): {self.conversion_factor}"


class CarbonBudget(models.Model):
    BUDGET_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='carbon_budgets')
    budget_type = models.CharField(max_length=10, choices=BUDGET_TYPE_CHOICES)
    target_co2_kg = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0)])
    current_co2_kg = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carbon_budgets'
        unique_together = ['user', 'budget_type', 'start_date']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]
        
    def __str__(self):
        return f"{self.user.email} - {self.budget_type} budget: {self.target_co2_kg}kg CO2"
    
    @property
    def progress_percentage(self):
        if self.target_co2_kg > 0:
            return min(100, int((self.current_co2_kg / self.target_co2_kg) * 100))
        return 0
    
    @property
    def remaining_co2_kg(self):
        return max(0, self.target_co2_kg - self.current_co2_kg)