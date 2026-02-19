from django.db import models
from django.conf import settings


class Payment(models.Model):

    METHOD_CHOICES = [
        ('stripe', 'Carte bancaire (Stripe)'),
        ('tmoney', 'TMoney'),
        ('flooz', 'Flooz'),
        ('cash_office', 'Paiement au bureau'),
    ]
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Validé'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]
    TYPE_CHOICES = [
        ('rental', 'Réservation location'),
        ('part_order', 'Commande pièce'),
        ('transport_advance', 'Avance transport international'),
    ]

    #-----Qui paie
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payments',
        verbose_name="Client"
    )
    client_name = models.CharField(max_length=150, blank=True, verbose_name="Nom client (invité)")
    client_email = models.EmailField(blank=True, verbose_name="Email client (invité)")
    payment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type")
    rental_id = models.IntegerField(null=True, blank=True, verbose_name="ID Réservation")
    order_id = models.IntegerField(null=True, blank=True, verbose_name="ID Commande pièce")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant (FCFA)")
    currency = models.CharField(max_length=5, default='XOF', verbose_name="Devise")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name="Moyen de paiement")
    transaction_id = models.CharField(max_length=255, blank=True, verbose_name="ID transaction (externe)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Numéro de facture")
    admin_note = models.TextField(blank=True, verbose_name="Note admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-created_at']

    def __str__(self):
        return f"Paiement #{self.invoice_number} — {self.amount} {self.currency} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        #-----Generer un numero de facture automatiquement
        if not self.invoice_number:
            import uuid
            self.invoice_number = f"FAC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)