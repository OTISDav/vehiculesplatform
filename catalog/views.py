from rest_framework import generics, permissions, filters
from .models import Brand, VehicleModel, Vehicle, SparePart
from .serializers import (
    BrandSerializer,
    VehicleListSerializer, VehicleDetailSerializer,
    SparePartListSerializer, SparePartDetailSerializer
)


class BrandListView(generics.ListAPIView):
    #----GET /api/v1/catalog/brands/ — Liste des marques
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]


class VehicleListView(generics.ListAPIView):
    #-----GET /api/v1/catalog/vehicles/
    serializer_class = VehicleListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'brand__name', 'model__name', 'description']
    ordering_fields = ['price', 'created_at', 'year', 'mileage']
    ordering = ['-is_featured', '-created_at']

    def get_queryset(self):
        qs = Vehicle.objects.filter(status='available').select_related('brand', 'model')
        params = self.request.query_params

        #-----Filtres
        if vtype := params.get('type'):
            qs = qs.filter(vehicle_type=vtype)
        if listing := params.get('listing_type'):
            qs = qs.filter(listing_type=listing)
        if brand := params.get('brand'):
            qs = qs.filter(brand_id=brand)
        if model := params.get('model'):
            qs = qs.filter(model_id=model)
        if year_min := params.get('year_min'):
            qs = qs.filter(year__gte=year_min)
        if year_max := params.get('year_max'):
            qs = qs.filter(year__lte=year_max)
        if price_min := params.get('min_price'):
            qs = qs.filter(price__gte=price_min)
        if price_max := params.get('max_price'):
            qs = qs.filter(price__lte=price_max)
        if fuel := params.get('fuel'):
            qs = qs.filter(fuel=fuel)
        if transmission := params.get('transmission'):
            qs = qs.filter(transmission=transmission)
        if condition := params.get('condition'):
            qs = qs.filter(condition=condition)
        if origin := params.get('origin'):
            qs = qs.filter(origin=origin)
        if country := params.get('country'):
            qs = qs.filter(country__icontains=country)
        if city := params.get('city'):
            qs = qs.filter(city__icontains=city)
        if featured := params.get('featured'):
            qs = qs.filter(is_featured=True)

        return qs


class VehicleDetailView(generics.RetrieveAPIView):
    #------GET /api/v1/catalog/vehicles/<id>/ — Fiche detail véhicule
    queryset = Vehicle.objects.select_related('brand', 'model').prefetch_related('media')
    serializer_class = VehicleDetailSerializer
    permission_classes = [permissions.AllowAny]


class SparePartListView(generics.ListAPIView):

    #----GET /api/v1/catalog/parts/
    serializer_class = SparePartListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'reference', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-is_featured', '-created_at']

    def get_queryset(self):
        qs = SparePart.objects.prefetch_related('compatible_brands', 'media')
        params = self.request.query_params

        if condition := params.get('condition'):
            qs = qs.filter(condition=condition)
        if is_local := params.get('is_local'):
            qs = qs.filter(is_local=is_local.lower() == 'true')
        if status := params.get('status'):
            qs = qs.filter(status=status)
        if brand := params.get('brand'):
            qs = qs.filter(compatible_brands__id=brand)
        if price_min := params.get('min_price'):
            qs = qs.filter(price__gte=price_min)
        if price_max := params.get('max_price'):
            qs = qs.filter(price__lte=price_max)

        return qs


class SparePartDetailView(generics.RetrieveAPIView):
    #---GET /api/v1/catalog/parts/<id>/ — Fiche détail piece
    queryset = SparePart.objects.prefetch_related('compatible_brands', 'compatible_models', 'media')
    serializer_class = SparePartDetailSerializer
    permission_classes = [permissions.AllowAny]