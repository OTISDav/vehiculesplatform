from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    #------seules les clients qui veulent louer on besoin de compte & commende (pieces) peuvens se faire comme invite

    phone = models.CharField(max_length=20, blank=True, verbose_name="Telephone")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    country = models.CharField(max_length=100, default="Togo", verbose_name="Pays")
    is_kyc_verified = models.BooleanField(default=False, verbose_name="KYC verifie")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"



class KYCDocument(models.Model):

    #----Documents de vrification d'identite pour la location de véhicules

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Refusé'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='kyc',
        verbose_name="Utilisateur"
    )
    id_card_front = models.ImageField(
        upload_to='kyc/id_cards/',
        verbose_name="Pièce d'identité (recto)"
    )
    id_card_back = models.ImageField(
        upload_to='kyc/id_cards/',
        blank=True,
        verbose_name="Pièce d'identité (verso)"
    )
    driving_license = models.ImageField(
        upload_to='kyc/licenses/',
        verbose_name="Permis de conduire"
    )
    selfie = models.ImageField(
        upload_to='kyc/selfies/',
        verbose_name="Photo (selfie de vérification)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut"
    )
    admin_note = models.TextField(
        blank=True,
        verbose_name="Note de l'admin (motif de refus etc.)"
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Soumis le")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Examiné le")

    class Meta:
        verbose_name = "Dossier KYC"
        verbose_name_plural = "Dossiers KYC"

    def __str__(self):
        return f"KYC — {self.user.get_full_name()} ({self.get_status_display()})"
