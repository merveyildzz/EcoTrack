from rest_framework import serializers
from .models import ActivityCategory, Activity, ActivityTemplate


class ActivityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityCategory
        fields = '__all__'


class ActivityTemplateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = ActivityTemplate
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.category_type', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = Activity
        fields = '__all__'
        read_only_fields = ('user', 'co2_kg', 'co2_calculated', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        if attrs.get('end_timestamp') and attrs.get('start_timestamp'):
            if attrs['end_timestamp'] <= attrs['start_timestamp']:
                raise serializers.ValidationError("End time must be after start time")
        return attrs


class ActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('category', 'activity_type', 'value', 'unit', 'start_timestamp', 
                 'end_timestamp', 'latitude', 'longitude', 'location_name', 'notes')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)