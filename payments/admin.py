from django.contrib import admin
from django.utils.html import format_html
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number', 'client_display',
        'payment_type', 'amount_display',
        'method', 'status_display', 'created_at'
    )
    list_filter = ('status', 'method', 'payment_type')
    search_fields = ('invoice_number', 'client__email', 'client_name', 'transaction_id')
    readonly_fields = ('invoice_number', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Client', {
            'fields': ('client', 'client_name', 'client_email')
        }),
        ('Transaction', {
            'fields': (
                'invoice_number', 'payment_type',
                'rental_id', 'order_id',
                'amount', 'currency',
                'method', 'transaction_id', 'status'
            )
        }),
        ('Notes', {
            'fields': ('admin_note',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def client_display(self, obj):
        if obj.client:
            return obj.client.get_full_name() or obj.client.email
        return obj.client_name or "Invité"
    client_display.short_description = "Client"

    def amount_display(self, obj):
        return f"{obj.amount:,.0f} {obj.currency}"
    amount_display.short_description = "Montant"

    def status_display(self, obj):
        colors = {
            'pending': 'orange',
            'completed': 'green',
            'failed': 'red',
            'refunded': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = "Statut"



from django.contrib import admin
from logistics.models import TransportRequest


@admin.register(TransportRequest)
class TransportRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'vehicle', 'client_name',
        'origin_country', 'destination_city',
        'estimated_cost_display', 'advance_paid_display',
        'status', 'created_at'
    )
    list_filter = ('status', 'origin_country')
    search_fields = ('client_name', 'client_email', 'vehicle__title', 'origin_country')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    actions = ['send_quote', 'mark_in_transit', 'mark_arrived']

    fieldsets = (
        ('Véhicule', {
            'fields': ('vehicle',)
        }),
        ('Client', {
            'fields': ('client_name', 'client_email', 'client_phone', 'destination_city')
        }),
        ('Transport', {
            'fields': (
                'origin_country', 'origin_city',
                'estimated_cost', 'transport_note',
                'customs_note'
            )
        }),
        ('Suivi financier', {
            'fields': ('advance_paid',)
        }),
        ('Statut & Notes', {
            'fields': ('status', 'admin_note')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def estimated_cost_display(self, obj):
        if obj.estimated_cost:
            return f"{obj.estimated_cost:,.0f} FCFA"
        return "—"
    estimated_cost_display.short_description = "Coût estimé"

    def advance_paid_display(self, obj):
        color = "green" if obj.advance_paid > 0 else "gray"
        return format_html(
            '<span style="color:{}">{} FCFA</span>',
            color, f"{obj.advance_paid:,.0f}"
        )
    advance_paid_display.short_description = "Avance payée"

    @admin.action(description="📧 Marquer devis envoyé")
    def send_quote(self, request, queryset):
        count = queryset.update(status='quote_sent')
        self.message_user(request, f"Devis marqué comme envoyé pour {count} demande(s).")

    @admin.action(description="🚢 Marquer en transit")
    def mark_in_transit(self, request, queryset):
        count = queryset.update(status='in_transit')
        self.message_user(request, f"{count} véhicule(s) marqué(s) en transit.")

    @admin.action(description="🏁 Marquer arrivé au Togo")
    def mark_arrived(self, request, queryset):
        count = queryset.update(status='arrived')
        self.message_user(request, f"{count} véhicule(s) arrivé(s) au Togo.")