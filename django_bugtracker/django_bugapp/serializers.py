from rest_framework import serializers
from django.contrib.auth.models import User,Group
from .models import Bug,Sprint
from django.core.exceptions import ValidationError

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

class DeveloperBugStatsSerializer(serializers.Serializer):
    developer = UserProfileSerializer()
    bugs_completed = serializers.IntegerField()
    bugs_created = serializers.IntegerField()

class BugSerializer(serializers.ModelSerializer):
    time_spent_seconds = serializers.SerializerMethodField()

    class Meta:
        model = Bug
        fields = ('id', 'title', 'status', 'created_at', 'updated_at', 'time_spent_seconds')

    def get_time_spent_seconds(self, obj):
        duration = obj.updated_at - obj.created_at
        # Defensive: return integer seconds, not float
        return int(duration.total_seconds())

class SprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = '__all__'

    def validate(self, data):
        lead = data.get('lead_developer')
        devs = data.get('developers', [])
        if lead and lead in devs:
            raise serializers.ValidationError("Lead developer cannot be a developer in the same sprint.")

        developer_group = Group.objects.get(name="developer")
        for dev in devs:
            if not developer_group in dev.groups.all():
                raise serializers.ValidationError(f"User {dev} is not in the developer group.")
        return data