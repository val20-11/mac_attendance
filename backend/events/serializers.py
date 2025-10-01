from rest_framework import serializers
from .models import Event, ExternalUser

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type', 'modality',
            'speaker', 'date', 'start_time', 'end_time', 'location',
            'max_capacity', 'is_active', 'meeting_link'
        ]

class ExternalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalUser
        fields = [
            'id', 'full_name', 'email', 'phone', 'institution',
            'position', 'reason', 'temporary_id', 'status',
            'created_at', 'processed_at'
        ]