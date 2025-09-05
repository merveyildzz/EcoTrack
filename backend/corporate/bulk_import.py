"""
Bulk CSV import system for corporate activity data
Handles large-scale data imports with validation, error handling, and progress tracking
"""
import csv
import io
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal, InvalidOperation
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from celery import shared_task

from activities.models import Activity, ActivityCategory
from .models import Organization, OrganizationMember, Team, TeamMember
from .utils import with_tenant

User = get_user_model()
logger = logging.getLogger(__name__)


class BulkImportProcessor:
    """
    Main processor for bulk CSV imports
    Handles validation, processing, and error reporting
    """
    
    def __init__(self, organization: Organization, uploaded_by: User):
        self.organization = organization
        self.uploaded_by = uploaded_by
        self.errors = []
        self.warnings = []
        self.processed_count = 0
        self.skipped_count = 0
        self.created_count = 0
    
    def process_csv(self, csv_file, import_type='activities') -> Dict[str, Any]:
        """
        Process CSV file and import data
        
        Args:
            csv_file: File object containing CSV data
            import_type: Type of import ('activities', 'users', 'teams')
        
        Returns:
            Dict with import results and statistics
        """
        
        try:
            # Detect file encoding
            content = csv_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8-sig')  # Handle BOM
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(content))
            rows = list(csv_reader)
            
            if not rows:
                return {
                    'success': False,
                    'error': 'CSV file is empty or has no valid data rows'
                }
            
            # Process based on import type
            with with_tenant(self.organization):
                if import_type == 'activities':
                    return self._process_activities_csv(rows)
                elif import_type == 'users':
                    return self._process_users_csv(rows)
                elif import_type == 'teams':
                    return self._process_teams_csv(rows)
                else:
                    return {
                        'success': False,
                        'error': f'Unsupported import type: {import_type}'
                    }
        
        except Exception as e:
            logger.error(f"CSV import error for org {self.organization.id}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to process CSV: {str(e)}'
            }
    
    def _process_activities_csv(self, rows: List[Dict]) -> Dict[str, Any]:
        """Process activities CSV import"""
        
        # Validate CSV structure
        required_fields = ['user_email', 'category', 'activity_type', 'value', 'unit', 'date']
        optional_fields = ['co2_kg', 'location', 'notes', 'team_name']
        
        if not self._validate_csv_structure(rows[0], required_fields):
            return {
                'success': False,
                'error': f'Missing required fields. Required: {", ".join(required_fields)}'
            }
        
        # Process rows in batches
        batch_size = 100
        total_batches = len(rows) // batch_size + (1 if len(rows) % batch_size else 0)
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, len(rows))
            batch_rows = rows[start_idx:end_idx]
            
            self._process_activities_batch(batch_rows)
        
        return {
            'success': True,
            'processed_count': self.processed_count,
            'created_count': self.created_count,
            'skipped_count': self.skipped_count,
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def _process_activities_batch(self, rows: List[Dict]):
        """Process a batch of activity rows"""
        
        activities_to_create = []
        
        for row_num, row in enumerate(rows, 1):
            try:
                activity_data = self._parse_activity_row(row, row_num)
                if activity_data:
                    activities_to_create.append(activity_data)
                    
            except Exception as e:
                self.errors.append(f"Row {row_num}: {str(e)}")
                self.skipped_count += 1
        
        # Bulk create activities
        if activities_to_create:
            try:
                with transaction.atomic():
                    Activity.objects.bulk_create(activities_to_create)
                    self.created_count += len(activities_to_create)
                    self.processed_count += len(activities_to_create)
                    
            except Exception as e:
                logger.error(f"Batch creation failed: {str(e)}")
                # Fall back to individual creation
                self._create_activities_individually(activities_to_create)
    
    def _parse_activity_row(self, row: Dict, row_num: int) -> Optional[Activity]:
        """Parse a single activity row"""
        
        # Get user
        user_email = row.get('user_email', '').strip()
        if not user_email:
            raise ValueError(f"Missing user_email")
        
        user = self._get_or_validate_user(user_email)
        if not user:
            raise ValueError(f"User not found or not a member of organization: {user_email}")
        
        # Get category
        category_name = row.get('category', '').strip()
        category = self._get_or_create_category(category_name)
        
        # Parse activity data
        activity_type = row.get('activity_type', '').strip()
        if not activity_type:
            raise ValueError("Missing activity_type")
        
        # Parse value
        try:
            value = Decimal(str(row.get('value', 0)).strip())
            if value <= 0:
                raise ValueError("Value must be greater than 0")
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Invalid value: {row.get('value')}")
        
        unit = row.get('unit', '').strip()
        if not unit:
            raise ValueError("Missing unit")
        
        # Parse date
        date_str = row.get('date', '').strip()
        activity_date = self._parse_date(date_str)
        
        # Optional fields
        co2_kg = None
        co2_str = row.get('co2_kg', '').strip()
        if co2_str:
            try:
                co2_kg = Decimal(co2_str)
            except InvalidOperation:
                self.warnings.append(f"Row {row_num}: Invalid CO2 value '{co2_str}', will be calculated")
        
        location = row.get('location', '').strip()
        notes = row.get('notes', '').strip()
        
        # Create activity object
        activity = Activity(
            user=user,
            category=category,
            activity_type=activity_type,
            value=value,
            unit=unit,
            start_timestamp=activity_date,
            end_timestamp=activity_date,
            co2_kg=co2_kg,
            location_name=location,
            notes=notes,
            metadata={'imported': True, 'imported_by': str(self.uploaded_by.id)}
        )
        
        return activity
    
    def _get_or_validate_user(self, email: str) -> Optional[User]:
        """Get user and validate organization membership"""
        try:
            user = User.objects.get(email=email)
            
            # Check if user is a member of the organization
            if OrganizationMember.objects.filter(
                user=user,
                organization=self.organization,
                status='active'
            ).exists():
                return user
            
        except User.DoesNotExist:
            pass
        
        return None
    
    def _get_or_create_category(self, category_name: str) -> ActivityCategory:
        """Get or create activity category"""
        # Map common category names
        category_mapping = {
            'transport': 'transportation',
            'transportation': 'transportation',
            'energy': 'energy',
            'food': 'food',
            'consumption': 'consumption',
            'waste': 'waste',
        }
        
        category_type = category_mapping.get(category_name.lower(), 'consumption')
        
        category, created = ActivityCategory.objects.get_or_create(
            name=category_name,
            defaults={
                'category_type': category_type,
                'description': f'Imported category: {category_name}',
                'is_active': True
            }
        )
        
        return category
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string in various formats"""
        if not date_str:
            raise ValueError("Missing date")
        
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                # Make timezone aware
                if timezone.is_naive(parsed_date):
                    parsed_date = timezone.make_aware(parsed_date)
                return parsed_date
            except ValueError:
                continue
        
        raise ValueError(f"Invalid date format: {date_str}")
    
    def _create_activities_individually(self, activities: List[Activity]):
        """Create activities individually if bulk creation fails"""
        for activity in activities:
            try:
                activity.save()
                self.created_count += 1
                self.processed_count += 1
            except Exception as e:
                self.errors.append(f"Failed to create activity: {str(e)}")
                self.skipped_count += 1
    
    def _process_users_csv(self, rows: List[Dict]) -> Dict[str, Any]:
        """Process users CSV import"""
        required_fields = ['email', 'first_name', 'last_name', 'role']
        optional_fields = ['team_name', 'department', 'job_title']
        
        if not self._validate_csv_structure(rows[0], required_fields):
            return {
                'success': False,
                'error': f'Missing required fields. Required: {", ".join(required_fields)}'
            }
        
        # Process user rows
        for row_num, row in enumerate(rows, 1):
            try:
                self._process_user_row(row, row_num)
            except Exception as e:
                self.errors.append(f"Row {row_num}: {str(e)}")
                self.skipped_count += 1
        
        return {
            'success': True,
            'processed_count': self.processed_count,
            'created_count': self.created_count,
            'skipped_count': self.skipped_count,
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def _process_user_row(self, row: Dict, row_num: int):
        """Process a single user row"""
        email = row.get('email', '').strip().lower()
        first_name = row.get('first_name', '').strip()
        last_name = row.get('last_name', '').strip()
        role = row.get('role', 'member').strip().lower()
        
        if not email or not first_name or not last_name:
            raise ValueError("Missing required user fields")
        
        # Validate role
        valid_roles = ['member', 'team_lead', 'manager', 'admin']
        if role not in valid_roles:
            raise ValueError(f"Invalid role: {role}. Must be one of: {', '.join(valid_roles)}")
        
        # Get or create user
        user, user_created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True
            }
        )
        
        # Create organization membership
        membership, membership_created = OrganizationMember.objects.get_or_create(
            user=user,
            organization=self.organization,
            defaults={
                'role': role,
                'status': 'active',
                'department': row.get('department', '').strip(),
                'job_title': row.get('job_title', '').strip(),
                'invited_by': self.uploaded_by
            }
        )
        
        if not membership_created:
            # Update existing membership
            membership.role = role
            membership.department = row.get('department', '').strip()
            membership.job_title = row.get('job_title', '').strip()
            membership.save()
        
        # Add to team if specified
        team_name = row.get('team_name', '').strip()
        if team_name:
            try:
                team = Team.objects.get(name=team_name, organization=self.organization)
                TeamMember.objects.get_or_create(
                    user=user,
                    team=team,
                    defaults={'is_active': True}
                )
            except Team.DoesNotExist:
                self.warnings.append(f"Row {row_num}: Team '{team_name}' not found")
        
        if user_created:
            self.created_count += 1
        
        self.processed_count += 1
    
    def _process_teams_csv(self, rows: List[Dict]) -> Dict[str, Any]:
        """Process teams CSV import"""
        required_fields = ['name', 'description']
        optional_fields = ['manager_email', 'monthly_co2_target']
        
        if not self._validate_csv_structure(rows[0], required_fields):
            return {
                'success': False,
                'error': f'Missing required fields. Required: {", ".join(required_fields)}'
            }
        
        # Process team rows
        for row_num, row in enumerate(rows, 1):
            try:
                self._process_team_row(row, row_num)
            except Exception as e:
                self.errors.append(f"Row {row_num}: {str(e)}")
                self.skipped_count += 1
        
        return {
            'success': True,
            'processed_count': self.processed_count,
            'created_count': self.created_count,
            'skipped_count': self.skipped_count,
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def _process_team_row(self, row: Dict, row_num: int):
        """Process a single team row"""
        name = row.get('name', '').strip()
        description = row.get('description', '').strip()
        
        if not name:
            raise ValueError("Missing team name")
        
        # Get manager if specified
        manager = None
        manager_email = row.get('manager_email', '').strip()
        if manager_email:
            try:
                manager = User.objects.get(email=manager_email)
                # Verify manager is organization member
                if not OrganizationMember.objects.filter(
                    user=manager,
                    organization=self.organization,
                    status='active'
                ).exists():
                    raise ValueError(f"Manager {manager_email} is not a member of the organization")
            except User.DoesNotExist:
                raise ValueError(f"Manager not found: {manager_email}")
        
        # Parse CO2 target
        monthly_co2_target = None
        target_str = row.get('monthly_co2_target', '').strip()
        if target_str:
            try:
                monthly_co2_target = Decimal(target_str)
            except InvalidOperation:
                self.warnings.append(f"Row {row_num}: Invalid CO2 target '{target_str}'")
        
        # Create team
        team, created = Team.objects.get_or_create(
            name=name,
            organization=self.organization,
            defaults={
                'description': description,
                'manager': manager,
                'monthly_co2_target': monthly_co2_target,
                'is_active': True
            }
        )
        
        if created:
            self.created_count += 1
        
        self.processed_count += 1
    
    def _validate_csv_structure(self, first_row: Dict, required_fields: List[str]) -> bool:
        """Validate CSV has required fields"""
        if not first_row:
            return False
        
        missing_fields = set(required_fields) - set(first_row.keys())
        if missing_fields:
            self.errors.append(f"Missing required columns: {', '.join(missing_fields)}")
            return False
        
        return True


@shared_task(bind=True)
def process_bulk_import_task(self, organization_id: str, uploaded_by_id: str, 
                           csv_content: str, import_type: str = 'activities'):
    """
    Celery task for processing bulk imports asynchronously
    """
    try:
        organization = Organization.objects.get(id=organization_id)
        uploaded_by = User.objects.get(id=uploaded_by_id)
        
        processor = BulkImportProcessor(organization, uploaded_by)
        
        # Create file-like object from content
        csv_file = io.StringIO(csv_content)
        
        # Process the import
        result = processor.process_csv(csv_file, import_type)
        
        # Update task progress
        self.update_state(
            state='SUCCESS',
            meta=result
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Bulk import task failed: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise


def generate_csv_template(import_type: str = 'activities') -> str:
    """
    Generate CSV template for imports
    """
    templates = {
        'activities': [
            'user_email,category,activity_type,value,unit,date,co2_kg,location,notes,team_name',
            'john@company.com,transportation,car_trip,50,km,2024-01-15,12.5,"Office to Client","Business meeting",Sales Team',
            'jane@company.com,energy,electricity_usage,100,kWh,2024-01-15,45.0,"Main Office","Monthly usage",Operations Team'
        ],
        'users': [
            'email,first_name,last_name,role,team_name,department,job_title',
            'john@company.com,John,Doe,member,Sales Team,Sales,Account Manager',
            'jane@company.com,Jane,Smith,team_lead,Operations Team,Operations,Operations Lead'
        ],
        'teams': [
            'name,description,manager_email,monthly_co2_target',
            'Sales Team,Handles client relationships and sales,john@company.com,500.0',
            'Operations Team,Manages day-to-day operations,jane@company.com,800.0'
        ]
    }
    
    return '\n'.join(templates.get(import_type, templates['activities']))