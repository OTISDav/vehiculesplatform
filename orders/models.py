# orders/models.py

from django.db import models
from django.conf import settings
from catalog.models import Vehicle, SparePart


class Rental(models.Model):

    #------necessite un compte client avec KYC valide

    DELIVERY_CHOICES = [
        ('pickup', 'Retrait sur place'),
        ('delivery', 'Livraison à domicile'),
    ]
    STATUS_CHOICES = [
        ('pending_kyc', 'En attente de vérification KYC'),
        ('pending_payment', 'En attente de paiement'),
        ('confirmed', 'Confirmée'),
        ('active', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='rentals',
        verbose_name="Client"
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name='rentals',
        verbose_name="Véhicule"
    )
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    delivery_mode = models.CharField(
        max_length=10,
        choices=DELIVERY_CHOICES,
        default='pickup',
        verbose_name="Mode de récupération"
    )
    delivery_address = models.TextField(blank=True, verbose_name="Adresse de livraison")
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix/jour (FCFA)")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix total (FCFA)")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant payé")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_kyc', verbose_name="Statut")
    admin_note = models.TextField(blank=True, verbose_name="Note admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ['-created_at']

    def __str__(self):
        return f"Réservation #{self.pk} — {self.client.get_full_name()} / {self.vehicle.title}"

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days

    @property
    def remaining_balance(self):
        return self.total_price - self.amount_paid


class SparePartOrder(models.Model):

    #-----Peut etre passee sans compte (en tant qu'invite)

    DELIVERY_CHOICES = [
        ('home', 'Livraison à domicile'),
        ('pickup', 'Retrait sur place'),
    ]
    STATUS_CHOICES = [
        ('pending', 'En attente de confirmation'),
        ('confirmed', 'Confirmée'),
        ('preparing', 'En préparation'),
        ('out_for_delivery', 'En cours de livraison'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]

    #----Client (peut être invite)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='part_orders',
        verbose_name="Compte client (optionnel)"
    )
    #----Infos client invite
    guest_name = models.CharField(max_length=150, blank=True, verbose_name="Nom (invité)")
    guest_phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone (invité)")
    guest_email = models.EmailField(blank=True, verbose_name="Email (invité)")
    part = models.ForeignKey(
        SparePart,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name="Pièce"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire (FCFA)")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix total (FCFA)")
    delivery_mode = models.CharField(max_length=10, choices=DELIVERY_CHOICES, default='home', verbose_name="Mode de livraison")
    delivery_address = models.TextField(blank=True, verbose_name="Adresse de livraison")
    estimated_delivery = models.CharField(max_length=100, blank=True, verbose_name="Délai estimé (ex: 1h, 24h)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    admin_note = models.TextField(blank=True, verbose_name="Note admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande de pièce"
        verbose_name_plural = "Commandes de pièces"
        ordering = ['-created_at']

    def __str__(self):
        client_name = self.client.get_full_name() if self.client else self.guest_name
        return f"Commande #{self.pk} — {client_name} / {self.part.title}"

    def save(self, *args, **kwargs):
        #-----Calcul automatique du prix total
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class ContactMessage(models.Model):

    #------Expediteur
    sender_name = models.CharField(max_length=150, verbose_name="Nom")
    sender_email = models.EmailField(verbose_name="Email")
    sender_phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")

    #---Sujet du message
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='messages',
        verbose_name="Véhicule concerné"
    )
    part = models.ForeignKey(
        SparePart,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='messages',
        verbose_name="Pièce concernée"
    )
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Lu par l'admin")
    admin_reply = models.TextField(blank=True, verbose_name="Réponse de l'admin")
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name="Répondu le")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']

    def __str__(self):
        return f"Message de {self.sender_name} — {self.subject}"