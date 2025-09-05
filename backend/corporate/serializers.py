from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organization, OrganizationMember, Team, TeamMember, Challenge, ChallengeParticipant

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'username']


class OrganizationSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    total_co2_saved = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'domain', 'industry', 'size', 'logo', 'website', 
                 'plan', 'is_active', 'created_at', 'updated_at', 'member_count', 'total_co2_saved']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.filter(status='active').count()
    
    def get_total_co2_saved(self, obj):
        # This would be calculated from activities data
        # For now, return 0 - can be enhanced later
        return 0


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)
    invited_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = ['id', 'organization', 'user', 'role', 'status', 'department', 
                 'job_title', 'joined_at', 'invited_by']
        read_only_fields = ['joined_at']


class TeamSerializer(serializers.ModelSerializer):
    manager = UserBasicSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    total_co2_saved = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'manager', 'is_active', 
                 'created_at', 'updated_at', 'member_count', 'total_co2_saved']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_total_co2_saved(self, obj):
        # This would be calculated from activities data
        # For now, return 0 - can be enhanced later
        return 0


class TeamMemberSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    
    class Meta:
        model = TeamMember
        fields = ['team', 'user', 'joined_at']
        read_only_fields = ['joined_at']


class ChallengeSerializer(serializers.ModelSerializer):
    created_by = UserBasicSerializer(read_only=True)
    participant_count = serializers.SerializerMethodField()
    organization = OrganizationSerializer(read_only=True)
    
    class Meta:
        model = Challenge
        fields = ['id', 'organization', 'title', 'description', 'challenge_type', 
                 'target_value', 'target_unit', 'start_date', 'end_date', 'status',
                 'is_public', 'reward_description', 'created_by', 'created_at', 
                 'updated_at', 'participant_count']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_participant_count(self, obj):
        return obj.participants.filter(status='joined').count()


class ChallengeParticipantSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    challenge = ChallengeSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = ChallengeParticipant
        fields = ['challenge', 'user', 'team', 'status', 'current_progress', 
                 'progress_percentage', 'joined_at', 'completed_at']
        read_only_fields = ['joined_at']


# Dashboard specific serializers
class DashboardStatsSerializer(serializers.Serializer):
    total_organizations = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_teams = serializers.IntegerField()
    total_co2_saved = serializers.DecimalField(max_digits=15, decimal_places=3)
    active_challenges = serializers.IntegerField()
    recent_activities_count = serializers.IntegerField()