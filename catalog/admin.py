from django.contrib import admin
from django.utils.html import format_html
from .models import Brand, VehicleModel, Vehicle, VehicleMedia, SparePart, SparePartMedia


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'model_count')
    search_fields = ('name',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" height="30" />', obj.logo.url)
        return "—"
    logo_preview.short_description = "Logo"

    def model_count(self, obj):
        return obj.models.count()
    model_count.short_description = "Nb modèles"


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name')
    list_filter = ('brand',)
    search_fields = ('name', 'brand__name')


class VehicleMediaInline(admin.TabularInline):
    model = VehicleMedia
    extra = 3
    fields = ('file', 'media_type', 'is_cover', 'order')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    inlines = [VehicleMediaInline]

    list_display = (
        'title', 'vehicle_type', 'listing_type',
        'brand', 'model', 'year',
        'price_display', 'origin', 'status', 'is_featured'
    )
    list_filter = ('vehicle_type', 'listing_type', 'status', 'origin', 'condition', 'fuel', 'is_featured')
    search_fields = ('title', 'brand__name', 'model__name', 'description')
    list_editable = ('status', 'is_featured')
    ordering = ('-is_featured', '-created_at')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Informations générales', {
            'fields': (
                'title', 'vehicle_type', 'listing_type',
                'brand', 'model', 'year', 'condition',
            )
        }),
        ('Caractéristiques', {
            'fields': ('mileage', 'fuel', 'transmission', 'color')
        }),
        ('Prix', {
            'fields': ('price', 'rental_price_per_day')
        }),
        ('Localisation & Transport', {
            'fields': (
                'origin', 'city', 'country',
                'transport_included', 'transport_estimate'
            )
        }),
        ('Description & Statut', {
            'fields': ('description', 'status', 'is_featured')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def price_display(self, obj):
        return f"{obj.price:,.0f} FCFA"
    price_display.short_description = "Prix"


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'reference', 'condition',
        'price_display', 'stock_quantity', 'status', 'is_local', 'is_featured'
    )
    list_filter = ('condition', 'status', 'is_local', 'is_featured')
    search_fields = ('title', 'reference', 'description')
    list_editable = ('status', 'stock_quantity', 'is_featured')
    filter_horizontal = ('compatible_brands', 'compatible_models')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Informations', {
            'fields': ('title', 'reference', 'condition', 'description')
        }),
        ('Compatibilité', {
            'fields': ('compatible_brands', 'compatible_models')
        }),
        ('Stock & Prix', {
            'fields': ('price', 'stock_quantity', 'status', 'is_local')
        }),
        ('Mise en avant', {
            'fields': ('is_featured',)
        }),
    )

    def price_display(self, obj):
        return f"{obj.price:,.0f} FCFA"
    price_display.short_description = "Prix"