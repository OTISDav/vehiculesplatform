from django.db import models
from catalog.models import Vehicle


class TransportZone(models.Model):
    """
    Zone géographique avec tarif fixe.
    Ex : Europe Ouest, Europe Est, Asie, Amérique...
    """
    name = models.CharField(max_length=100, verbose_name="Nom de la zone")
    countries = models.TextField(
        verbose_name="Pays inclus (un par ligne)",
        help_text="Ex: France\nAllemagne\nBelgique"
    )
    base_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name="Prix de base (FCFA)"
    )
    price_per_kg = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0,
        verbose_name="Supplément par kg (FCFA)"
    )
    delay_days_min = models.PositiveIntegerField(verbose_name="Délai minimum (jours)")
    delay_days_max = models.PositiveIntegerField(verbose_name="Délai maximum (jours)")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    notes = models.TextField(blank=True, verbose_name="Notes (conditions, restrictions...)")

    class Meta:
        verbose_name = "Zone tarifaire"
        verbose_name_plural = "Zones tarifaires"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} — {self.base_price:,.0f} FCFA"

    def get_countries_list(self):
        return [c.strip() for c in self.countries.splitlines() if c.strip()]

    def country_belongs(self, country_name):
        country_lower = country_name.lower()
        return any(c.lower() == country_lower for c in self.get_countries_list())


class Transporter(models.Model):
    """
    Transporteur partenaire géré par l'admin.
    """
    name = models.CharField(max_length=150, verbose_name="Nom du transporteur")
    contact_name = models.CharField(max_length=150, blank=True, verbose_name="Contact")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    zones = models.ManyToManyField(
        TransportZone,
        blank=True,
        related_name='transporters',
        verbose_name="Zones couvertes"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    notes = models.TextField(blank=True, verbose_name="Notes internes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transporteur"
        verbose_name_plural = "Transporteurs"
        ordering = ['name']

    def __str__(self):
        return self.name


class TransportRequest(models.Model):
    """
    Demande de transport d'un véhicule depuis l'étranger vers le Togo.
    Cycle de vie complet avec suivi étapé.
    """
    STATUS_CHOICES = [
        ('quote_requested', 'Devis demandé'),
        ('quote_sent',      'Devis envoyé au client'),
        ('advance_paid',    'Avance payée — en attente chargement'),
        ('loading',         'Chargement en cours'),
        ('in_transit',      'En transit'),
        ('arrived_port',    'Arrivé au port de Lomé'),
        ('customs',         'En cours de dédouanement'),
        ('delivered',       'Livré au client'),
        ('cancelled',       'Annulé'),
    ]

    # ── Véhicule ──────────────────────────────────────────────────────────────
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name='transport_requests',
        verbose_name="Véhicule"
    )

    # ── Client ────────────────────────────────────────────────────────────────
    client_name = models.CharField(max_length=150, verbose_name="Nom du client")
    client_email = models.EmailField(verbose_name="Email")
    client_phone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    destination_city = models.CharField(max_length=100, default="Lomé", verbose_name="Ville de destination")

    # ── Origine ───────────────────────────────────────────────────────────────
    origin_country = models.CharField(max_length=100, verbose_name="Pays d'origine")
    origin_city = models.CharField(max_length=100, blank=True, verbose_name="Ville d'origine")

    # ── Zone tarifaire & Calcul ───────────────────────────────────────────────
    zone = models.ForeignKey(
        TransportZone,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='requests',
        verbose_name="Zone tarifaire détectée"
    )
    vehicle_weight_kg = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Poids du véhicule (kg)"
    )
    estimated_cost = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        verbose_name="Coût estimé (FCFA)"
    )
    final_cost = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        verbose_name="Coût final validé par l'admin (FCFA)"
    )

    # ── Transporteur assigné ──────────────────────────────────────────────────
    transporter = models.ForeignKey(
        Transporter,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='requests',
        verbose_name="Transporteur assigné"
    )

    # ── Paiement avance ───────────────────────────────────────────────────────
    advance_required = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        verbose_name="Avance requise (FCFA)"
    )
    advance_paid = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0,
        verbose_name="Avance payée (FCFA)"
    )

    # ── Statut & Notes ────────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='quote_requested',
        verbose_name="Statut"
    )
    customs_note = models.CharField(
        max_length=255,
        default="Le dédouanement n'est pas inclus dans ce devis.",
        verbose_name="Mention dédouanement"
    )
    admin_note = models.TextField(blank=True, verbose_name="Note interne admin")
    client_note = models.TextField(blank=True, verbose_name="Message visible par le client")

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Demande de transport"
        verbose_name_plural = "Demandes de transport"
        ordering = ['-created_at']

    def __str__(self):
        return f"Transport #{self.pk} — {self.vehicle.title} ({self.origin_country} → {self.destination_city})"

    def calculate_estimate(self):
        """
        Calcule automatiquement le coût estimé selon la zone tarifaire.
        Appelé lors de la création de la demande.
        """
        if not self.zone:
            return None
        cost = self.zone.base_price
        if self.vehicle_weight_kg and self.zone.price_per_kg:
            cost += self.vehicle_weight_kg * self.zone.price_per_kg
        return cost


class TransportStep(models.Model):
    """
    Étape de suivi du transport.
    Chaque changement de statut crée une étape visible par le client.
    """
    request = models.ForeignKey(
        TransportRequest,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name="Demande de transport"
    )
    status = models.CharField(
        max_length=20,
        choices=TransportRequest.STATUS_CHOICES,
        verbose_name="Statut atteint"
    )
    title = models.CharField(max_length=200, verbose_name="Titre de l'étape")
    description = models.TextField(blank=True, verbose_name="Détails")
    location = models.CharField(
        max_length=150, blank=True,
        verbose_name="Lieu (port, ville...)"
    )
    reached_at = models.DateTimeField(auto_now_add=True, verbose_name="Atteint le")

    class Meta:
        verbose_name = "Étape de transport"
        verbose_name_plural = "Étapes de transport"
        ordering = ['reached_at']

    def __str__(self):
        return f"Étape [{self.get_status_display()}] — Transport #{self.request_id}"