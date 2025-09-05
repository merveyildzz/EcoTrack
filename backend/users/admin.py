from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserSettings, UserMetrics

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_superuser', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('email', 'username')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('email_verified', 'timezone', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'location', 'created_at')
    search_fields = ('user__email', 'first_name', 'last_name')
    list_filter = ('created_at',)

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'units', 'privacy_level', 'ai_recommendations', 'email_notifications')
    list_filter = ('units', 'privacy_level', 'ai_recommendations', 'email_notifications')
    search_fields = ('user__email',)

@admin.register(UserMetrics)
class UserMetricsAdmin(admin.ModelAdmin):
    list_display = ('user', 'metric_date', 'co2_kg', 'activities_count', 'source')
    list_filter = ('metric_date', 'source')
    search_fields = ('user__email',)
    date_hierarchy = 'metric_date'
