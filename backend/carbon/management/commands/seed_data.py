from django.core.management.base import BaseCommand
from django.db import transaction
from activities.models import ActivityCategory, ActivityTemplate
from carbon.models import EmissionFactor, UnitConversion


class Command(BaseCommand):
    help = 'Seed the database with initial data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with initial data...')
        
        with transaction.atomic():
            self.create_activity_categories()
            self.create_emission_factors()
            self.create_unit_conversions()
            self.create_activity_templates()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with initial data')
        )

    def create_activity_categories(self):
        categories = [
            {
                'name': 'Car Travel',
                'category_type': 'transportation',
                'description': 'Travel by car, including fuel consumption',
                'icon': 'car'
            },
            {
                'name': 'Public Transport',
                'category_type': 'transportation', 
                'description': 'Bus, train, subway, and other public transportation',
                'icon': 'bus'
            },
            {
                'name': 'Air Travel',
                'category_type': 'transportation',
                'description': 'Flights and air travel',
                'icon': 'plane'
            },
            {
                'name': 'Electricity',
                'category_type': 'energy',
                'description': 'Home and office electricity usage',
                'icon': 'electricity'
            },
            {
                'name': 'Natural Gas',
                'category_type': 'energy',
                'description': 'Home heating and cooking with natural gas',
                'icon': 'flame'
            },
            {
                'name': 'Food',
                'category_type': 'food',
                'description': 'Meals and food consumption',
                'icon': 'food'
            },
            {
                'name': 'Shopping',
                'category_type': 'consumption',
                'description': 'Consumer goods and purchases',
                'icon': 'shopping'
            }
        ]
        
        for cat_data in categories:
            category, created = ActivityCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

    def create_emission_factors(self):
        factors = [
            # Transportation
            {
                'category': 'transportation',
                'subcategory': 'Car Travel',
                'activity_type': 'gasoline_car',
                'unit': 'km',
                'factor_value': 0.21,  # kg CO2e per km
                'source': 'EPA 2024',
                'year': 2024,
                'confidence_level': 'high'
            },
            {
                'category': 'transportation',
                'subcategory': 'Car Travel',
                'activity_type': 'diesel_car',
                'unit': 'km',
                'factor_value': 0.18,
                'source': 'EPA 2024',
                'year': 2024,
                'confidence_level': 'high'
            },
            {
                'category': 'transportation',
                'subcategory': 'Public Transport',
                'activity_type': 'bus',
                'unit': 'km',
                'factor_value': 0.08,
                'source': 'Transit Authority 2024',
                'year': 2024,
                'confidence_level': 'medium'
            },
            {
                'category': 'transportation',
                'subcategory': 'Air Travel',
                'activity_type': 'domestic_flight',
                'unit': 'km',
                'factor_value': 0.25,
                'source': 'IATA 2024',
                'year': 2024,
                'confidence_level': 'high'
            },
            # Energy
            {
                'category': 'energy',
                'subcategory': 'Electricity',
                'activity_type': 'grid_electricity',
                'unit': 'kWh',
                'factor_value': 0.42,  # kg CO2e per kWh (US average)
                'source': 'EPA eGRID 2024',
                'year': 2024,
                'confidence_level': 'high'
            },
            {
                'category': 'energy',
                'subcategory': 'Natural Gas',
                'activity_type': 'natural_gas',
                'unit': 'kWh',
                'factor_value': 0.20,
                'source': 'EPA 2024',
                'year': 2024,
                'confidence_level': 'high'
            },
            # Food
            {
                'category': 'food',
                'subcategory': 'Food',
                'activity_type': 'beef',
                'unit': 'kg',
                'factor_value': 60.0,
                'source': 'FAO 2024',
                'year': 2024,
                'confidence_level': 'medium'
            },
            {
                'category': 'food',
                'subcategory': 'Food',
                'activity_type': 'chicken',
                'unit': 'kg',
                'factor_value': 6.9,
                'source': 'FAO 2024',
                'year': 2024,
                'confidence_level': 'medium'
            },
            {
                'category': 'food',
                'subcategory': 'Food',
                'activity_type': 'vegetables',
                'unit': 'kg',
                'factor_value': 2.0,
                'source': 'FAO 2024',
                'year': 2024,
                'confidence_level': 'medium'
            }
        ]
        
        for factor_data in factors:
            factor, created = EmissionFactor.objects.get_or_create(
                category=factor_data['category'],
                subcategory=factor_data['subcategory'],
                activity_type=factor_data['activity_type'],
                unit=factor_data['unit'],
                region='global',
                version='1.0',
                defaults=factor_data
            )
            if created:
                self.stdout.write(f'Created emission factor: {factor.activity_type}')

    def create_unit_conversions(self):
        conversions = [
            # Distance conversions
            {
                'from_unit': 'miles',
                'to_unit': 'km',
                'category': 'transportation',
                'conversion_factor': 1.60934
            },
            {
                'from_unit': 'm',
                'to_unit': 'km',
                'category': 'transportation',
                'conversion_factor': 0.001
            },
            # Energy conversions
            {
                'from_unit': 'MWh',
                'to_unit': 'kWh',
                'category': 'energy',
                'conversion_factor': 1000
            },
            {
                'from_unit': 'therms',
                'to_unit': 'kWh',
                'category': 'energy',
                'conversion_factor': 29.3071
            },
            # Weight conversions
            {
                'from_unit': 'lbs',
                'to_unit': 'kg',
                'category': 'food',
                'conversion_factor': 0.453592
            },
            {
                'from_unit': 'g',
                'to_unit': 'kg',
                'category': 'food',
                'conversion_factor': 0.001
            }
        ]
        
        for conv_data in conversions:
            conversion, created = UnitConversion.objects.get_or_create(
                from_unit=conv_data['from_unit'],
                to_unit=conv_data['to_unit'],
                category=conv_data['category'],
                defaults=conv_data
            )
            if created:
                self.stdout.write(f'Created unit conversion: {conversion.from_unit} -> {conversion.to_unit}')

    def create_activity_templates(self):
        templates = [
            # Transportation templates
            {
                'name': 'Daily Commute (Car)',
                'category_name': 'Car Travel',
                'activity_type': 'gasoline_car',
                'default_unit': 'km',
                'default_value': 20,
                'description': 'Round-trip daily commute by car'
            },
            {
                'name': 'Bus Trip',
                'category_name': 'Public Transport',
                'activity_type': 'bus',
                'default_unit': 'km',
                'default_value': 10,
                'description': 'Bus journey'
            },
            {
                'name': 'Domestic Flight',
                'category_name': 'Air Travel',
                'activity_type': 'domestic_flight',
                'default_unit': 'km',
                'default_value': 1000,
                'description': 'Domestic flight within country'
            },
            # Energy templates
            {
                'name': 'Monthly Electricity Bill',
                'category_name': 'Electricity',
                'activity_type': 'grid_electricity',
                'default_unit': 'kWh',
                'default_value': 500,
                'description': 'Average monthly household electricity usage'
            },
            {
                'name': 'Monthly Gas Bill',
                'category_name': 'Natural Gas',
                'activity_type': 'natural_gas',
                'default_unit': 'kWh',
                'default_value': 300,
                'description': 'Average monthly household natural gas usage'
            },
            # Food templates
            {
                'name': 'Beef Meal',
                'category_name': 'Food',
                'activity_type': 'beef',
                'default_unit': 'kg',
                'default_value': 0.2,
                'description': 'Typical beef portion in a meal'
            },
            {
                'name': 'Chicken Meal',
                'category_name': 'Food',
                'activity_type': 'chicken',
                'default_unit': 'kg',
                'default_value': 0.15,
                'description': 'Typical chicken portion in a meal'
            }
        ]
        
        for template_data in templates:
            category_name = template_data.pop('category_name')
            try:
                category = ActivityCategory.objects.get(name=category_name)
                template, created = ActivityTemplate.objects.get_or_create(
                    name=template_data['name'],
                    category=category,
                    defaults={**template_data, 'category': category}
                )
                if created:
                    self.stdout.write(f'Created activity template: {template.name}')
            except ActivityCategory.DoesNotExist:
                self.stdout.write(f'Category not found: {category_name}')
                continue