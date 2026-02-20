from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import User, KYCDocument


class KYCInline(admin.StackedInline):
    model = KYCDocument
    can_delete = False
    extra = 0
    readonly_fields = ('submitted_at', 'reviewed_at')
    fields = (
        'id_card_front', 'id_card_back',
        'driving_license', 'selfie',
        'status', 'admin_note',
        'submitted_at', 'reviewed_at',
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [KYCInline]
    list_display = ('email', 'get_full_name', 'phone', 'city', 'country', 'is_kyc_verified', 'date_joined')
    list_filter = ('is_kyc_verified', 'country', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations complémentaires', {
            'fields': ('phone', 'city', 'country', 'is_kyc_verified')
        }),
    )


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'submitted_at', 'reviewed_at')
    list_filter = ('status',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('submitted_at',)
    actions = ['approve_kyc', 'reject_kyc']

    fieldsets = (
        ('Client', {'fields': ('user',)}),
        ('Documents', {
            'fields': ('id_card_front', 'id_card_back', 'driving_license', 'selfie')
        }),
        ('Décision', {
            'fields': ('status', 'admin_note', 'submitted_at', 'reviewed_at')
        }),
    )

    @admin.action(description="Approuver les dossiers KYC sélectionnés")
    def approve_kyc(self, request, queryset):
        count = 0
        for kyc in queryset:
            kyc.status = 'approved'
            kyc.reviewed_at = timezone.now()
            kyc.save()
            #----Marquer l'utilisateur comme vérifié
            kyc.user.is_kyc_verified = True
            kyc.user.save()
            count += 1
        self.message_user(request, f"{count} dossier(s) KYC approuvé(s).")

    @admin.action(description="Refuser les dossiers KYC sélectionnés")
    def reject_kyc(self, request, queryset):
        count = queryset.update(status='rejected', reviewed_at=timezone.now())
        self.message_user(request, f"{count} dossier(s) KYC refusé(s).")