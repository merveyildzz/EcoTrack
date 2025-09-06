"""
Monitoring URLs
"""
from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('metrics/', views.metrics_endpoint, name='metrics'),
    path('health/', views.health_detailed, name='health-detailed'),
    path('dashboard/', views.dashboard_metrics, name='dashboard-metrics'),
    path('uptime/', views.uptime_check, name='uptime-check'),
    path('alert-test/', views.trigger_alert_test, name='alert-test'),
]