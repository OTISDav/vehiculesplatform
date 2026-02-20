from django.contrib import admin
from django.utils.html import format_html
from .models import Rental, SparePartOrder, ContactMessage


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client', 'vehicle',
        'start_date', 'end_date', 'duration_days',
        'total_price_display', 'amount_paid_display',
        'delivery_mode', 'status'
    )
    list_filter = ('status', 'delivery_mode')
    search_fields = ('client__email', 'client__first_name', 'vehicle__title')
    readonly_fields = ('created_at', 'updated_at', 'duration_days', 'remaining_balance')
    actions = ['confirm_rental', 'mark_active', 'mark_completed', 'cancel_rental']

    fieldsets = (
        ('Client & Véhicule', {
            'fields': ('client', 'vehicle')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'duration_days')
        }),
        ('Livraison', {
            'fields': ('delivery_mode', 'delivery_address')
        }),
        ('Prix & Paiement', {
            'fields': ('price_per_day', 'total_price', 'amount_paid', 'remaining_balance')
        }),
        ('Statut & Notes', {
            'fields': ('status', 'admin_note')
        }),
        ('Dates système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_price_display(self, obj):
        return f"{obj.total_price:,.0f} FCFA"
    total_price_display.short_description = "Total"

    def amount_paid_display(self, obj):
        color = "green" if obj.amount_paid >= obj.total_price else "orange"
        return format_html(
            '<span style="color:{}">{} FCFA</span>',
            color, f"{obj.amount_paid:,.0f}"
        )
    amount_paid_display.short_description = "Payé"

    def duration_days(self, obj):
        if obj.duration_days is not None:
            return f"{obj.duration_days} jour(s)"
        return "-"
    duration_days.short_description = "Durée"

    @admin.action(description="✅ Confirmer les réservations sélectionnées")
    def confirm_rental(self, request, queryset):
        count = queryset.update(status='confirmed')
        self.message_user(request, f"{count} réservation(s) confirmée(s).")

    @admin.action(description="🚗 Marquer comme en cours")
    def mark_active(self, request, queryset):
        count = queryset.update(status='active')
        self.message_user(request, f"{count} réservation(s) marquée(s) en cours.")

    @admin.action(description="🏁 Marquer comme terminée")
    def mark_completed(self, request, queryset):
        count = queryset.update(status='completed')
        self.message_user(request, f"{count} réservation(s) terminée(s).")

    @admin.action(description="❌ Annuler les réservations sélectionnées")
    def cancel_rental(self, request, queryset):
        count = queryset.update(status='cancelled')
        self.message_user(request, f"{count} réservation(s) annulée(s).")


@admin.register(SparePartOrder)
class SparePartOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client_display', 'part',
        'quantity', 'total_price_display',
        'delivery_mode', 'estimated_delivery', 'status'
    )
    list_filter = ('status', 'delivery_mode')
    search_fields = ('guest_name', 'guest_email', 'client__email', 'part__title')
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    list_editable = ('status',)
    actions = ['confirm_order', 'mark_preparing', 'mark_out_for_delivery', 'mark_delivered']

    fieldsets = (
        ('Client', {
            'fields': ('client', 'guest_name', 'guest_phone', 'guest_email')
        }),
        ('Commande', {
            'fields': ('part', 'quantity', 'unit_price', 'total_price')
        }),
        ('Livraison', {
            'fields': ('delivery_mode', 'delivery_address', 'estimated_delivery')
        }),
        ('Statut & Notes', {
            'fields': ('status', 'admin_note')
        }),
        ('Dates système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def client_display(self, obj):
        if obj.client:
            return obj.client.get_full_name() or obj.client.email
        return obj.guest_name or "Invité"
    client_display.short_description = "Client"

    def total_price_display(self, obj):
        return f"{obj.total_price:,.0f} FCFA"
    total_price_display.short_description = "Total"

    @admin.action(description="✅ Confirmer les commandes")
    def confirm_order(self, request, queryset):
        count = queryset.update(status='confirmed')
        self.message_user(request, f"{count} commande(s) confirmée(s).")

    @admin.action(description="📦 Marquer en préparation")
    def mark_preparing(self, request, queryset):
        count = queryset.update(status='preparing')
        self.message_user(request, f"{count} commande(s) en préparation.")

    @admin.action(description="🚚 Marquer en livraison")
    def mark_out_for_delivery(self, request, queryset):
        count = queryset.update(status='out_for_delivery')
        self.message_user(request, f"{count} commande(s) en cours de livraison.")

    @admin.action(description="🏠 Marquer comme livrée")
    def mark_delivered(self, request, queryset):
        count = queryset.update(status='delivered')
        self.message_user(request, f"{count} commande(s) livrée(s).")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        'sender_name', 'sender_email', 'subject',
        'vehicle', 'part', 'is_read', 'created_at'
    )
    list_filter = ('is_read',)
    search_fields = ('sender_name', 'sender_email', 'subject', 'message')
    readonly_fields = ('created_at', 'sender_name', 'sender_email', 'sender_phone', 'message', 'vehicle', 'part')
    list_editable = ('is_read',)

    fieldsets = (
        ('Expéditeur', {
            'fields': ('sender_name', 'sender_email', 'sender_phone')
        }),
        ('Message', {
            'fields': ('subject', 'message', 'vehicle', 'part')
        }),
        ('Réponse admin', {
            'fields': ('is_read', 'admin_reply', 'replied_at')
        }),
        ('Date', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_read']

    @admin.action(description="📬 Marquer comme lu")
    def mark_as_read(self, request, queryset):
        count = queryset.update(is_read=True)
        self.message_user(request, f"{count} message(s) marqué(s) comme lu(s).")