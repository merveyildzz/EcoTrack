from django.contrib import admin
from .models import Activity, ActivityCategory, ActivityTemplate

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'co2_kg', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__email', 'activity_type', 'notes')
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(ActivityTemplate)
class ActivityTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'activity_type', 'default_unit', 'default_value', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'activity_type', 'description')
