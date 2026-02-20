from rest_framework import serializers
from .models import TransportRequest


class TransportRequestSerializer(serializers.ModelSerializer):

    vehicle_title = serializers.CharField(source='vehicle.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TransportRequest
        fields = (
            'id',
            'vehicle', 'vehicle_title',
            'client_name', 'client_email', 'client_phone',
            'destination_city',
            'origin_country', 'origin_city',
            'estimated_cost', 'transport_note', 'customs_note',
            'advance_paid',
            'status', 'status_display',
            'created_at'
        )
        read_only_fields = (
            'id', 'estimated_cost', 'transport_note',
            'customs_note', 'advance_paid',
            'status', 'status_display', 'created_at',
            'vehicle_title'
        )

    def validate_vehicle(self, vehicle):
        if vehicle.origin != 'international':
            raise serializers.ValidationError(
                "Ce véhicule est local. La demande de transport ne s'applique qu'aux véhicules à l'étranger."
            )
        return vehicle