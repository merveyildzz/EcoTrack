from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from corporate.models import Organization, OrganizationMember, Team, TeamMember, Challenge
from datetime import datetime, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with sample corporate data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help='Clear existing corporate data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing corporate data...')
            Organization.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        # Create sample organizations
        self.stdout.write('Creating sample organizations...')
        
        organizations_data = [
            {
                'name': 'EcoTech Solutions',
                'domain': 'ecotech.com',
                'industry': 'Technology',
                'size': '100-500',
                'website': 'https://ecotech.com',
                'plan': 'professional'
            },
            {
                'name': 'Green Energy Corp',
                'domain': 'greenenergy.com',
                'industry': 'Energy',
                'size': '500-1000',
                'website': 'https://greenenergy.com',
                'plan': 'enterprise'
            },
            {
                'name': 'Sustainable Finance Ltd',
                'domain': 'sustainablefinance.com',
                'industry': 'Finance',
                'size': '50-100',
                'website': 'https://sustainablefinance.com',
                'plan': 'basic'
            }
        ]

        organizations = []
        for org_data in organizations_data:
            org, created = Organization.objects.get_or_create(
                domain=org_data['domain'],
                defaults=org_data
            )
            organizations.append(org)
            if created:
                self.stdout.write(f'Created organization: {org.name}')
            else:
                self.stdout.write(f'Organization already exists: {org.name}')

        # Get all users
        users = list(User.objects.all())
        
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return

        # Assign users to organizations
        self.stdout.write('Creating organization memberships...')
        
        roles = ['admin', 'manager', 'member']
        departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations']
        job_titles = [
            'Software Engineer', 'Product Manager', 'Marketing Manager', 
            'Sales Representative', 'HR Specialist', 'Financial Analyst',
            'Operations Manager', 'Team Lead', 'Senior Developer'
        ]

        for i, user in enumerate(users):
            # Assign each user to a different organization (cycle through orgs)
            org = organizations[i % len(organizations)]
            
            # First user in each org becomes admin, others get random roles
            role = 'admin' if i < len(organizations) else random.choice(roles)
            
            membership, created = OrganizationMember.objects.get_or_create(
                organization=org,
                user=user,
                defaults={
                    'role': role,
                    'status': 'active',
                    'department': random.choice(departments),
                    'job_title': random.choice(job_titles)
                }
            )
            
            if created:
                self.stdout.write(f'Added {user.email} to {org.name} as {role}')

        # Create teams for each organization
        self.stdout.write('Creating teams...')
        
        team_names = [
            'Engineering Team', 'Marketing Team', 'Sales Team', 
            'Product Team', 'Design Team', 'DevOps Team',
            'Research Team', 'Customer Success Team'
        ]

        teams = []
        for org in organizations:
            # Create 3-5 teams per organization
            org_members = OrganizationMember.objects.filter(organization=org, status='active')
            
            for i in range(random.randint(3, 5)):
                team_name = f"{org.name.split()[0]} {team_names[i % len(team_names)]}"
                
                # Select a random manager from org members
                manager = random.choice(org_members).user if org_members else None
                
                team, created = Team.objects.get_or_create(
                    organization=org,
                    name=team_name.replace(f"{org.name.split()[0]} ", ""),
                    defaults={
                        'description': f'A dedicated team for {team_name.lower()} at {org.name}',
                        'manager': manager,
                        'is_active': True
                    }
                )
                teams.append(team)
                
                if created:
                    self.stdout.write(f'Created team: {team_name}')

        # Add members to teams
        self.stdout.write('Adding members to teams...')
        
        for team in teams:
            org_members = OrganizationMember.objects.filter(
                organization=team.organization, 
                status='active'
            )
            
            # Add 2-6 members per team
            num_members = min(random.randint(2, 6), org_members.count())
            selected_members = random.sample(list(org_members), num_members)
            
            for member in selected_members:
                team_member, created = TeamMember.objects.get_or_create(
                    team=team,
                    user=member.user
                )
                if created:
                    self.stdout.write(f'Added {member.user.email} to team {team.name}')

        # Create sample challenges
        self.stdout.write('Creating sample challenges...')
        
        challenge_data = [
            {
                'title': 'Carbon Footprint Reduction Challenge',
                'description': 'Reduce your carbon footprint by 20% this quarter',
                'challenge_type': 'reduction',
                'target_value': 20.0,
                'target_unit': 'percentage',
                'reward_description': 'Team lunch and recognition'
            },
            {
                'title': 'Eco-Friendly Commute Week',
                'description': 'Use sustainable transportation for a week',
                'challenge_type': 'activity',
                'target_value': 7.0,
                'target_unit': 'days',
                'reward_description': 'Green transportation voucher'
            },
            {
                'title': 'Zero Waste Office Challenge',
                'description': 'Achieve zero waste in your department',
                'challenge_type': 'team',
                'target_value': 100.0,
                'target_unit': 'percentage',
                'reward_description': 'Sustainability award and team outing'
            }
        ]

        for org in organizations:
            admin_member = OrganizationMember.objects.filter(
                organization=org, 
                role='admin'
            ).first()
            
            if not admin_member:
                continue

            for i, challenge_info in enumerate(challenge_data):
                start_date = datetime.now() - timedelta(days=random.randint(1, 30))
                end_date = start_date + timedelta(days=random.randint(30, 90))
                
                challenge, created = Challenge.objects.get_or_create(
                    organization=org,
                    title=f"{org.name.split()[0]} {challenge_info['title']}",
                    defaults={
                        'description': challenge_info['description'],
                        'challenge_type': challenge_info['challenge_type'],
                        'target_value': challenge_info['target_value'],
                        'target_unit': challenge_info['target_unit'],
                        'start_date': start_date,
                        'end_date': end_date,
                        'status': random.choice(['active', 'completed']),
                        'is_public': random.choice([True, False]),
                        'reward_description': challenge_info['reward_description'],
                        'created_by': admin_member.user
                    }
                )
                
                if created:
                    self.stdout.write(f'Created challenge: {challenge.title}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated corporate data:\n'
                f'- Organizations: {Organization.objects.count()}\n'
                f'- Organization Members: {OrganizationMember.objects.count()}\n'
                f'- Teams: {Team.objects.count()}\n'
                f'- Team Members: {TeamMember.objects.count()}\n'
                f'- Challenges: {Challenge.objects.count()}'
            )
        )