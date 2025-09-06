"""
Django management command for deployment
"""
from django.core.management.base import BaseCommand
from ecotrack.deployment import HealthChecker, DeploymentManager, BackupManager


class Command(BaseCommand):
    help = 'Run deployment and launch readiness tasks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--task',
            type=str,
            choices=['health-check', 'deploy', 'backup', 'all'],
            default='all',
            help='Specific deployment task to run'
        )
        parser.add_argument(
            '--create-backup',
            action='store_true',
            help='Create backup before deployment'
        )
        parser.add_argument(
            '--backup-name',
            type=str,
            help='Name for the backup'
        )
    
    def handle(self, *args, **options):
        task = options['task']
        create_backup = options['create_backup']
        backup_name = options['backup_name']
        
        self.stdout.write(self.style.SUCCESS('🚀 EcoTrack Deployment Manager\n'))
        
        if create_backup or task in ['backup', 'all']:
            self.stdout.write('📦 Creating backup...')
            backup_result = BackupManager.create_backup(backup_name)
            if backup_result['success']:
                self.stdout.write(self.style.SUCCESS(f'✓ {backup_result["message"]}'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ {backup_result["message"]}'))
        
        if task in ['health-check', 'all']:
            self.stdout.write('\n🏥 Running health checks...')
            health_results = HealthChecker.run_all_checks()
            
            for check in health_results['checks']:
                status_icon = '✓' if check['status'] == 'PASS' else '✗'
                status_style = self.style.SUCCESS if check['status'] == 'PASS' else self.style.ERROR
                self.stdout.write(status_style(f'{status_icon} {check["name"]}: {check["message"]}'))
            
            overall_style = self.style.SUCCESS if health_results['overall_status'] == 'PASS' else self.style.ERROR
            self.stdout.write(overall_style(f'\nOverall Health: {health_results["overall_status"]}'))
            
            if health_results['overall_status'] == 'FAIL':
                self.stdout.write(self.style.WARNING('⚠️  Fix health check issues before deployment'))
                if task != 'all':
                    return
        
        if task in ['deploy', 'all']:
            self.stdout.write('\n⚙️  Running deployment tasks...')
            deployment_results = DeploymentManager.run_deployment_tasks()
            
            for result in deployment_results:
                status_icon = '✓' if result['status'] == 'SUCCESS' else '✗'
                status_style = self.style.SUCCESS if result['status'] == 'SUCCESS' else self.style.ERROR
                self.stdout.write(status_style(f'{status_icon} {result["task"]}: {result["message"]}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Deployment tasks completed!'))