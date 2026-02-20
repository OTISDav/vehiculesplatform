from rest_framework import serializers
from .models import Brand, VehicleModel, Vehicle, VehicleMedia, SparePart, SparePartMedia


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'logo')


class VehicleModelSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = VehicleModel
        fields = ('id', 'name', 'brand', 'brand_name')


class VehicleMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleMedia
        fields = ('id', 'media_type', 'file', 'is_cover', 'order')


class VehicleListSerializer(serializers.ModelSerializer):
    #---Version allege pour les listes (catalogue, recherche)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)
    cover_photo = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = (
            'id', 'title', 'vehicle_type', 'listing_type',
            'brand_name', 'model_name', 'year', 'mileage',
            'fuel', 'transmission', 'condition',
            'price', 'rental_price_per_day',
            'origin', 'city', 'country',
            'transport_included', 'transport_estimate',
            'status', 'is_featured',
            'cover_photo', 'created_at'
        )

    def get_cover_photo(self, obj):
        cover = obj.media.filter(is_cover=True, media_type='photo').first()
        if not cover:
            cover = obj.media.filter(media_type='photo').first()
        if cover:
            request = self.context.get('request')
            return request.build_absolute_uri(cover.file.url) if request else cover.file.url
        return None


class VehicleDetailSerializer(serializers.ModelSerializer):
    #-----Version complete pour la fiche détail d'un véhicule
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)
    media = VehicleMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = (
            'id', 'title', 'vehicle_type', 'listing_type',
            'brand', 'brand_name', 'model', 'model_name',
            'year', 'mileage', 'fuel', 'transmission',
            'color', 'condition',
            'price', 'rental_price_per_day',
            'origin', 'city', 'country',
            'transport_included', 'transport_estimate',
            'description', 'status', 'is_featured',
            'media', 'created_at', 'updated_at'
        )


class SparePartMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SparePartMedia
        fields = ('id', 'file', 'is_cover', 'order')


class SparePartListSerializer(serializers.ModelSerializer):
    #----Version allegee pour la liste des pieces
    compatible_brands = BrandSerializer(many=True, read_only=True)
    cover_photo = serializers.SerializerMethodField()

    class Meta:
        model = SparePart
        fields = (
            'id', 'title', 'reference', 'condition',
            'price', 'stock_quantity', 'status',
            'is_local', 'is_featured',
            'compatible_brands', 'cover_photo'
        )

    def get_cover_photo(self, obj):
        cover = obj.media.filter(is_cover=True).first()
        if not cover:
            cover = obj.media.first()
        if cover:
            request = self.context.get('request')
            return request.build_absolute_uri(cover.file.url) if request else cover.file.url
        return None


class SparePartDetailSerializer(serializers.ModelSerializer):
    #----Version complete pour la fiche detail d'une piece
    compatible_brands = BrandSerializer(many=True, read_only=True)
    compatible_models = VehicleModelSerializer(many=True, read_only=True)
    media = SparePartMediaSerializer(many=True, read_only=True)

    class Meta:
        model = SparePart
        fields = (
            'id', 'title', 'reference', 'condition',
            'price', 'stock_quantity', 'status',
            'is_local', 'is_featured', 'description',
            'compatible_brands', 'compatible_models',
            'media', 'created_at', 'updated_at'
        )