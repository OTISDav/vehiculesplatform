from django.db import models
from catalog.models import Vehicle


class TransportRequest(models.Model):

    STATUS_CHOICES = [
        ('quote_requested', 'Devis demandé'),
        ('quote_sent', 'Devis envoyé au client'),
        ('advance_paid', 'Avance payée'),
        ('in_transit', 'En transit'),
        ('arrived', 'Arrivé au Togo'),
        ('cancelled', 'Annulé'),
    ]

    #----Véhicule concerné
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name='transport_requests',
        verbose_name="Véhicule"
    )

    #-----Client demandeur
    client_name = models.CharField(max_length=150, verbose_name="Nom du client")
    client_email = models.EmailField(verbose_name="Email")
    client_phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    destination_city = models.CharField(max_length=100, default="Lomé", verbose_name="Ville de destination")

    #----Devis transport
    origin_country = models.CharField(max_length=100, verbose_name="Pays d'origine du véhicule")
    origin_city = models.CharField(max_length=100, blank=True, verbose_name="Ville d'origine")
    estimated_cost = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        verbose_name="Coût estimé (FCFA)"
    )
    transport_note = models.TextField(
        blank=True,
        verbose_name="Détails (délai, conditions, transporteur...)"
    )

    #------Rappel légal
    customs_note = models.CharField(
        max_length=255,
        default="Le dédouanement n'est pas inclus dans ce devis.",
        verbose_name="Mention dédouanement"
    )

    # ── Statut ────────────────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='quote_requested',
        verbose_name="Statut"
    )
    advance_paid = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0,
        verbose_name="Avance payée (FCFA)"
    )
    admin_note = models.TextField(blank=True, verbose_name="Note interne admin")

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Demande de transport"
        verbose_name_plural = "Demandes de transport"
        ordering = ['-created_at']

    def __str__(self):
        return f"Transport #{self.pk} — {self.vehicle.title} ({self.origin_country} → {self.destination_city})"