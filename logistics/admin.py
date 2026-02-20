from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import TransportZone, Transporter, TransportRequest, TransportStep


@admin.register(TransportZone)
class TransportZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price_display', 'price_per_kg', 'delay_display', 'country_count', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'countries')
    list_editable = ('is_active',)

    fieldsets = (
        ('Zone', {
            'fields': ('name', 'countries', 'is_active')
        }),
        ('Tarification', {
            'fields': ('base_price', 'price_per_kg')
        }),
        ('Délais', {
            'fields': ('delay_days_min', 'delay_days_max')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

    def base_price_display(self, obj):
        return f"{obj.base_price:,.0f} FCFA"
    base_price_display.short_description = "Prix de base"

    def delay_display(self, obj):
        return f"{obj.delay_days_min}–{obj.delay_days_max} jours"
    delay_display.short_description = "Délai"

    def country_count(self, obj):
        return len(obj.get_countries_list())
    country_count.short_description = "Nb pays"


@admin.register(Transporter)
class TransporterAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_name', 'phone', 'email', 'zone_list', 'is_active')
    list_filter = ('is_active', 'zones')
    search_fields = ('name', 'contact_name', 'email')
    filter_horizontal = ('zones',)
    list_editable = ('is_active',)

    fieldsets = (
        ('Informations', {
            'fields': ('name', 'contact_name', 'phone', 'email', 'is_active')
        }),
        ('Zones couvertes', {
            'fields': ('zones',)
        }),
        ('Notes internes', {
            'fields': ('notes',)
        }),
    )

    def zone_list(self, obj):
        zones = obj.zones.filter(is_active=True)
        return ", ".join(z.name for z in zones) or "—"
    zone_list.short_description = "Zones"


class TransportStepInline(admin.TabularInline):
    model = TransportStep
    extra = 1
    fields = ('status', 'title', 'description', 'location', 'reached_at')
    readonly_fields = ('reached_at',)


@admin.register(TransportRequest)
class TransportRequestAdmin(admin.ModelAdmin):
    inlines = [TransportStepInline]

    # list_display = (
    #     'id', 'vehicle', 'client_name',
    #     'origin_display', 'zone',
    #     'estimated_cost_display', 'final_cost_display',
    #     'advance_paid_display',
    #     'transporter', 'status_badge', 'created_at'
    # )

    list_display = (
        'id', 'vehicle', 'client_name',
        'origin_display', 'zone',
        'estimated_cost_display', 'final_cost_display',
        'advance_paid_display',
        'transporter',
        'status',
        'status_badge',
        'created_at'
    )

    list_filter = ('status', 'zone', 'transporter', 'origin_country')
    search_fields = ('client_name', 'client_email', 'vehicle__title', 'origin_country')
    readonly_fields = ('created_at', 'updated_at', 'estimated_cost')
    list_editable = ('status',)
    actions = [
        'action_send_quote',
        'action_mark_advance_paid',
        'action_mark_loading',
        'action_mark_in_transit',
        'action_mark_arrived_port',
        'action_mark_customs',
        'action_mark_delivered',
        'action_cancel',
    ]

    fieldsets = (
        ('Véhicule', {
            'fields': ('vehicle',)
        }),
        ('Client', {
            'fields': ('client_name', 'client_email', 'client_phone', 'destination_city')
        }),
        ('Origine & Zone', {
            'fields': ('origin_country', 'origin_city', 'zone', 'vehicle_weight_kg')
        }),
        ('Tarification', {
            'fields': ('estimated_cost', 'final_cost', 'advance_required', 'advance_paid')
        }),
        ('Logistique', {
            'fields': ('transporter', 'status')
        }),
        ('Communication', {
            'fields': ('customs_note', 'client_note', 'admin_note')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Calcule automatiquement l'estimation si une zone est sélectionnée.
        Crée une étape de suivi à chaque changement de statut.
        """
        if obj.zone and not obj.estimated_cost:
            obj.estimated_cost = obj.calculate_estimate()

        old_status = None
        if obj.pk:
            old_status = TransportRequest.objects.get(pk=obj.pk).status

        super().save_model(request, obj, form, change)

        # Créer une étape si le statut a changé
        if old_status and old_status != obj.status:
            labels = dict(TransportRequest.STATUS_CHOICES)
            TransportStep.objects.create(
                request=obj,
                status=obj.status,
                title=labels.get(obj.status, obj.status),
                description=obj.client_note or '',
            )

    # ── Affichage ─────────────────────────────────────────────────────────────
    def origin_display(self, obj):
        return f"{obj.origin_city or ''} {obj.origin_country}".strip()
    origin_display.short_description = "Origine"

    def estimated_cost_display(self, obj):
        return f"{obj.estimated_cost:,.0f} FCFA" if obj.estimated_cost else "—"
    estimated_cost_display.short_description = "Estimé"

    def final_cost_display(self, obj):
        return f"{obj.final_cost:,.0f} FCFA" if obj.final_cost else "—"
    final_cost_display.short_description = "Final"

    def advance_paid_display(self, obj):
        if obj.advance_paid > 0:
            return format_html('<span style="color:green;font-weight:bold">{} FCFA</span>', f"{obj.advance_paid:,.0f}")
        return format_html('<span style="color:gray">0 FCFA</span>')
    advance_paid_display.short_description = "Avance payée"

    def status_badge(self, obj):
        colors = {
            'quote_requested': '#f59e0b',
            'quote_sent':      '#3b82f6',
            'advance_paid':    '#8b5cf6',
            'loading':         '#6366f1',
            'in_transit':      '#0ea5e9',
            'arrived_port':    '#10b981',
            'customs':         '#f97316',
            'delivered':       '#22c55e',
            'cancelled':       '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        label = dict(TransportRequest.STATUS_CHOICES).get(obj.status, obj.status)
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            color, label
        )
    status_badge.short_description = "Statut"

    # ── Actions ───────────────────────────────────────────────────────────────
    def _change_status(self, request, queryset, new_status, message):
        labels = dict(TransportRequest.STATUS_CHOICES)
        for obj in queryset:
            old = obj.status
            if old != new_status:
                obj.status = new_status
                obj.save()
                TransportStep.objects.create(
                    request=obj,
                    status=new_status,
                    title=labels.get(new_status, new_status),
                )
        self.message_user(request, f"{queryset.count()} demande(s) : {message}")

    @admin.action(description="📧 Devis envoyé au client")
    def action_send_quote(self, request, queryset):
        self._change_status(request, queryset, 'quote_sent', "Devis marqué comme envoyé.")

    @admin.action(description="💰 Avance payée")
    def action_mark_advance_paid(self, request, queryset):
        self._change_status(request, queryset, 'advance_paid', "Avance enregistrée.")

    @admin.action(description="📦 Chargement en cours")
    def action_mark_loading(self, request, queryset):
        self._change_status(request, queryset, 'loading', "Chargement démarré.")

    @admin.action(description="🚢 En transit")
    def action_mark_in_transit(self, request, queryset):
        self._change_status(request, queryset, 'in_transit', "Marqué en transit.")

    @admin.action(description="⚓ Arrivé au port de Lomé")
    def action_mark_arrived_port(self, request, queryset):
        self._change_status(request, queryset, 'arrived_port', "Arrivée au port enregistrée.")

    @admin.action(description="🏛️ En dédouanement")
    def action_mark_customs(self, request, queryset):
        self._change_status(request, queryset, 'customs', "En cours de dédouanement.")

    @admin.action(description="🏁 Livré au client")
    def action_mark_delivered(self, request, queryset):
        self._change_status(request, queryset, 'delivered', "Livraison confirmée.")

    @admin.action(description="❌ Annuler")
    def action_cancel(self, request, queryset):
        self._change_status(request, queryset, 'cancelled', "Annulé.")


@admin.register(TransportStep)
class TransportStepAdmin(admin.ModelAdmin):
    list_display = ('request', 'status', 'title', 'location', 'reached_at')
    list_filter = ('status',)
    readonly_fields = ('reached_at',)