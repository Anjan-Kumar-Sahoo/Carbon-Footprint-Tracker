from rest_framework import serializers
from .models import CommuteRecord

class CommuteRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommuteRecord
        fields = [
            'id', 'user', 'mode_of_transport', 'distance', 'fuel_efficiency', 'date', 'predicted_emission',
            'weather', 'traffic_intensity', 'road_type'
        ]
        read_only_fields = ['id', 'user', 'date', 'predicted_emission']
