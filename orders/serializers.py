from rest_framework import serializers
from django.utils import timezone
from .models import Rental, SparePartOrder, ContactMessage
from catalog.models import Vehicle, SparePart


class RentalCreateSerializer(serializers.ModelSerializer):
    #--Creation d'une reservation de location par le client

    class Meta:
        model = Rental
        fields = (
            'vehicle', 'start_date', 'end_date',
            'delivery_mode', 'delivery_address'
        )

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_kyc_verified:
            raise serializers.ValidationError(
                "Votre dossier KYC doit être validé avant de pouvoir réserver un véhicule."
            )

        start = attrs['start_date']
        end = attrs['end_date']
        if start >= end:
            raise serializers.ValidationError(
                {"end_date": "La date de fin doit être après la date de début."}
            )
        if start < timezone.now().date():
            raise serializers.ValidationError(
                {"start_date": "La date de début ne peut pas être dans le passé."}
            )

        vehicle = attrs['vehicle']
        if vehicle.status != 'available':
            raise serializers.ValidationError(
                {"vehicle": "Ce véhicule n'est pas disponible à la location."}
            )
        if vehicle.listing_type != 'rental':
            raise serializers.ValidationError(
                {"vehicle": "Ce véhicule n'est pas proposé à la location."}
            )

        if attrs['delivery_mode'] == 'delivery' and not attrs.get('delivery_address'):
            raise serializers.ValidationError(
                {"delivery_address": "Une adresse de livraison est requise."}
            )

        return attrs

    def create(self, validated_data):
        vehicle = validated_data['vehicle']
        start = validated_data['start_date']
        end = validated_data['end_date']
        days = (end - start).days
        price_per_day = vehicle.rental_price_per_day

        rental = Rental.objects.create(
            client=self.context['request'].user,
            price_per_day=price_per_day,
            total_price=price_per_day * days,
            status='pending_payment',
            **validated_data
        )
        return rental


class RentalDetailSerializer(serializers.ModelSerializer):
    #------Detail d'une reservation pour le client
    vehicle_title = serializers.CharField(source='vehicle.title', read_only=True)
    duration_days = serializers.IntegerField(read_only=True)
    remaining_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Rental
        fields = (
            'id', 'vehicle', 'vehicle_title',
            'start_date', 'end_date', 'duration_days',
            'delivery_mode', 'delivery_address',
            'price_per_day', 'total_price',
            'amount_paid', 'remaining_balance',
            'status', 'admin_note', 'created_at'
        )
        read_only_fields = fields


class SparePartOrderCreateSerializer(serializers.ModelSerializer):
    #----Creation d'une commande de piece (avec ou sans compte)

    class Meta:
        model = SparePartOrder
        fields = (
            'part',
            'quantity',
            'delivery_mode',
            'delivery_address',
            # Champs invité
            'guest_name',
            'guest_phone',
            'guest_email',
        )

    def validate(self, attrs):
        part = attrs['part']

        if part.status == 'out_of_stock':
            raise serializers.ValidationError(
                {"part": "Cette pièce est actuellement en rupture de stock."}
            )
        if part.stock_quantity < attrs.get('quantity', 1):
            raise serializers.ValidationError(
                {"quantity": f"Stock insuffisant. Disponible : {part.stock_quantity}"}
            )

        if attrs.get('delivery_mode') == 'home' and not attrs.get('delivery_address'):
            raise serializers.ValidationError(
                {"delivery_address": "Une adresse est requise pour la livraison à domicile."}
            )

        request = self.context['request']
        if not request.user.is_authenticated:
            if not attrs.get('guest_name'):
                raise serializers.ValidationError({"guest_name": "Votre nom est requis."})
            if not attrs.get('guest_phone'):
                raise serializers.ValidationError({"guest_phone": "Votre téléphone est requis."})

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        part = validated_data['part']
        quantity = validated_data.get('quantity', 1)

        estimated_delivery = "1h" if part.is_local else "24-48h"

        order = SparePartOrder.objects.create(
            client=request.user if request.user.is_authenticated else None,
            unit_price=part.price,
            estimated_delivery=estimated_delivery,
            **validated_data
        )

        part.stock_quantity -= quantity
        if part.stock_quantity == 0:
            part.status = 'out_of_stock'
        part.save()

        return order


class SparePartOrderDetailSerializer(serializers.ModelSerializer):
    #----Detail d'une commande de piece
    part_title = serializers.CharField(source='part.title', read_only=True)

    class Meta:
        model = SparePartOrder
        fields = (
            'id', 'part', 'part_title',
            'quantity', 'unit_price', 'total_price',
            'delivery_mode', 'delivery_address', 'estimated_delivery',
            'guest_name', 'guest_phone', 'guest_email',
            'status', 'created_at'
        )
        read_only_fields = fields


class ContactMessageSerializer(serializers.ModelSerializer):
    #-----Formulaire de contact depuis une fiche annonce

    class Meta:
        model = ContactMessage
        fields = (
            'sender_name', 'sender_email', 'sender_phone',
            'vehicle', 'part',
            'subject', 'message'
        )

    def validate(self, attrs):
        if not attrs.get('vehicle') and not attrs.get('part'):
            raise serializers.ValidationError(
                "Le message doit être lié à un véhicule ou une pièce."
            )
        return attrs