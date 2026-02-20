from rest_framework import serializers
from .models import TransportZone, Transporter, TransportRequest, TransportStep


class TransportZoneSerializer(serializers.ModelSerializer):
    countries_list = serializers.SerializerMethodField()
    delay_display = serializers.SerializerMethodField()

    class Meta:
        model = TransportZone
        fields = (
            'id', 'name', 'countries_list',
            'base_price', 'price_per_kg',
            'delay_days_min', 'delay_days_max', 'delay_display',
            'notes'
        )

    def get_countries_list(self, obj):
        return obj.get_countries_list()

    def get_delay_display(self, obj):
        return f"{obj.delay_days_min}–{obj.delay_days_max} jours"


class TransporterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transporter
        fields = ('id', 'name', 'zones')


class TransportStepSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TransportStep
        fields = ('id', 'status', 'status_display', 'title', 'description', 'location', 'reached_at')


class TransportRequestCreateSerializer(serializers.ModelSerializer):
    """
    Soumission d'une demande de transport par un client.
    Détecte automatiquement la zone et calcule l'estimation.
    """

    class Meta:
        model = TransportRequest
        fields = (
            'vehicle',
            'client_name', 'client_email', 'client_phone',
            'destination_city',
            'origin_country', 'origin_city',
            'vehicle_weight_kg',
        )

    def validate_vehicle(self, vehicle):
        if vehicle.origin != 'international':
            raise serializers.ValidationError(
                "Ce véhicule est local. Le transport international ne s'applique qu'aux véhicules situés à l'étranger."
            )
        if vehicle.status != 'available':
            raise serializers.ValidationError(
                "Ce véhicule n'est plus disponible."
            )
        return vehicle

    def create(self, validated_data):
        origin_country = validated_data.get('origin_country', '')

        # Détection automatique de la zone tarifaire
        zone = self._detect_zone(origin_country)

        instance = TransportRequest(**validated_data)
        instance.zone = zone

        # Calcul automatique de l'estimation
        if zone:
            instance.estimated_cost = instance.calculate_estimate()
            instance.advance_required = instance.estimated_cost * 30 / 100  # 30% d'avance

        instance.save()

        # Créer la première étape de suivi
        TransportStep.objects.create(
            request=instance,
            status='quote_requested',
            title='Demande de devis reçue',
            description=f"Demande soumise pour {instance.vehicle.title} depuis {origin_country}.",
        )

        return instance

    def _detect_zone(self, country_name):
        """Cherche la zone tarifaire correspondant au pays d'origine."""
        for zone in TransportZone.objects.filter(is_active=True):
            if zone.country_belongs(country_name):
                return zone
        return None


class TransportRequestDetailSerializer(serializers.ModelSerializer):
    """
    Détail complet d'une demande de transport avec étapes de suivi.
    """
    steps = TransportStepSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    transporter_name = serializers.CharField(source='transporter.name', read_only=True)
    vehicle_title = serializers.CharField(source='vehicle.title', read_only=True)
    delay_display = serializers.SerializerMethodField()

    class Meta:
        model = TransportRequest
        fields = (
            'id',
            'vehicle', 'vehicle_title',
            'client_name', 'client_email', 'client_phone',
            'destination_city',
            'origin_country', 'origin_city',
            'zone_name',
            'vehicle_weight_kg',
            'estimated_cost', 'final_cost',
            'advance_required', 'advance_paid',
            'transporter_name',
            'status', 'status_display',
            'customs_note', 'client_note',
            'delay_display',
            'steps',
            'created_at', 'updated_at',
        )
        read_only_fields = fields

    def get_delay_display(self, obj):
        if obj.zone:
            return f"{obj.zone.delay_days_min}–{obj.zone.delay_days_max} jours"
        return "À confirmer"


class TransportEstimateSerializer(serializers.Serializer):
    """
    Simulateur de coût : le client envoie pays + poids,
    on retourne l'estimation sans créer de demande.
    """
    origin_country = serializers.CharField()
    vehicle_weight_kg = serializers.IntegerField(required=False, default=0)

    def get_estimate(self):
        country = self.validated_data['origin_country']
        weight = self.validated_data.get('vehicle_weight_kg', 0)

        for zone in TransportZone.objects.filter(is_active=True):
            if zone.country_belongs(country):
                cost = zone.base_price
                if weight and zone.price_per_kg:
                    cost += weight * zone.price_per_kg
                return {
                    'zone': zone.name,
                    'base_price': zone.base_price,
                    'weight_supplement': weight * zone.price_per_kg if weight else 0,
                    'total_estimate': cost,
                    'advance_required': cost * 30 / 100,
                    'delay': f"{zone.delay_days_min}–{zone.delay_days_max} jours",
                    'customs_note': "Le dédouanement n'est pas inclus dans ce devis.",
                    'notes': zone.notes,
                }

        return {
            'zone': None,
            'total_estimate': None,
            'message': f"Aucune zone tarifaire trouvée pour '{country}'. Contactez-nous pour un devis personnalisé.",
        }