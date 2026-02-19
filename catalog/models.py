from django.db import models


class Brand(models.Model):
    #------Marque de vehicule (Toyota, Peugeot, Honda...)
    name = models.CharField(max_length=100, unique=True, verbose_name="Marque")
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Marque"
        verbose_name_plural = "Marques"
        ordering = ['name']

    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    #----Modele de vehicule lie a une marque (Corolla, 206, CB500...)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100, verbose_name="Modèle")

    class Meta:
        verbose_name = "Modèle"
        verbose_name_plural = "Modèles"
        unique_together = ('brand', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class Vehicle(models.Model):

    TYPE_CHOICES = [
        ('car', 'Voiture'),
        ('moto', 'Moto'),
    ]
    LISTING_TYPE_CHOICES = [
        ('sale', 'En vente'),
        ('rental', 'En location'),
    ]
    FUEL_CHOICES = [
        ('petrol', 'Essence'),
        ('diesel', 'Diesel'),
        ('electric', 'Électrique'),
        ('hybrid', 'Hybride'),
    ]
    TRANSMISSION_CHOICES = [
        ('manual', 'Manuelle'),
        ('automatic', 'Automatique'),
    ]
    CONDITION_CHOICES = [
        ('new', 'Neuf'),
        ('used', 'Occasion'),
    ]
    ORIGIN_CHOICES = [
        ('local', 'Au Togo'),
        ('international', 'À l\'étranger'),
    ]
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('reserved', 'Réservé'),
        ('sold', 'Vendu'),
        ('unavailable', 'Indisponible'),
    ]

    #----Informations de base

    title = models.CharField(max_length=200, verbose_name="Titre de l'annonce")
    vehicle_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Type")
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES, verbose_name="Type d'annonce")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name="Marque")
    model = models.ForeignKey(VehicleModel, on_delete=models.PROTECT, verbose_name="Modèle")
    year = models.PositiveIntegerField(verbose_name="Année")
    mileage = models.PositiveIntegerField(null=True, blank=True, verbose_name="Kilométrage (km)")
    fuel = models.CharField(max_length=20, choices=FUEL_CHOICES, verbose_name="Carburant")
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, verbose_name="Transmission")
    color = models.CharField(max_length=50, blank=True, verbose_name="Couleur")
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, verbose_name="État")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix (vente en FCFA)")
    rental_price_per_day = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        verbose_name="Prix de location par jour (FCFA)"
    )

    #----Localisation
    origin = models.CharField(max_length=15, choices=ORIGIN_CHOICES, default='local', verbose_name="Origine")
    city = models.CharField(max_length=100, verbose_name="Ville")
    country = models.CharField(max_length=100, default="Togo", verbose_name="Pays")

    #---Transport international
    transport_included = models.BooleanField(default=False, verbose_name="Frais de transport inclus")
    transport_estimate = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        verbose_name="Estimation frais de transport (FCFA)"
    )

    #--- Description & statut
    description = models.TextField(verbose_name="Description détaillée")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available', verbose_name="Statut")
    is_featured = models.BooleanField(default=False, verbose_name="Mise en avant")

    #----Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.title} — {self.get_listing_type_display()}"


 #----Photos et videos associes a un vehicule
class VehicleMedia(models.Model):

    MEDIA_TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('video', 'Vidéo'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='photo')
    file = models.FileField(upload_to='vehicles/media/')
    is_cover = models.BooleanField(default=False, verbose_name="Photo principale")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Média véhicule"
        verbose_name_plural = "Médias véhicules"
        ordering = ['order']

    def __str__(self):
        return f"{self.get_media_type_display()} — {self.vehicle.title}"


class SparePart(models.Model):

    CONDITION_CHOICES = [
        ('new', 'Neuf'),
        ('used', 'Occasion'),
    ]
    STATUS_CHOICES = [
        ('in_stock', 'En stock'),
        ('out_of_stock', 'Rupture de stock'),
    ]

    title = models.CharField(max_length=200, verbose_name="Nom de la pièce")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence")
    compatible_brands = models.ManyToManyField(Brand, blank=True, verbose_name="Marques compatibles")
    compatible_models = models.ManyToManyField(VehicleModel, blank=True, verbose_name="Modèles compatibles")
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='new', verbose_name="État")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix (FCFA)")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Quantité en stock")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_stock', verbose_name="Statut")
    is_local = models.BooleanField(default=True, verbose_name="Disponible au Togo (livraison rapide)")
    description = models.TextField(blank=True, verbose_name="Description")
    is_featured = models.BooleanField(default=False, verbose_name="Mise en avant")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pièce détachée"
        verbose_name_plural = "Pièces détachées"
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.reference})"


class SparePartMedia(models.Model):
    #-----Photos de piece détache
    part = models.ForeignKey(SparePart, on_delete=models.CASCADE, related_name='media')
    file = models.ImageField(upload_to='parts/media/')
    is_cover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
