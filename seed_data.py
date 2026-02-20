from django.utils import timezone
from accounts.models import User, KYCDocument
from catalog.models import Brand, VehicleModel, Vehicle, SparePart

print("🌱 Création des données de test...\n")

# ─── Marques ─────────────────────────────────────────────────────────────────
print("📦 Marques...")
toyota, _ = Brand.objects.get_or_create(name="Toyota")
peugeot, _ = Brand.objects.get_or_create(name="Peugeot")
honda, _ = Brand.objects.get_or_create(name="Honda")
mercedes, _ = Brand.objects.get_or_create(name="Mercedes-Benz")
yamaha, _ = Brand.objects.get_or_create(name="Yamaha")

# ─── Modèles ─────────────────────────────────────────────────────────────────
print("🚗 Modèles de véhicules...")
corolla, _ = VehicleModel.objects.get_or_create(brand=toyota, name="Corolla")
land_cruiser, _ = VehicleModel.objects.get_or_create(brand=toyota, name="Land Cruiser")
peugeot_308, _ = VehicleModel.objects.get_or_create(brand=peugeot, name="308")
civic, _ = VehicleModel.objects.get_or_create(brand=honda, name="Civic")
classe_c, _ = VehicleModel.objects.get_or_create(brand=mercedes, name="Classe C")
ybr, _ = VehicleModel.objects.get_or_create(brand=yamaha, name="YBR 125")

# ─── Véhicules ────────────────────────────────────────────────────────────────
print("🚘 Véhicules...")

# 1. Voiture en location — locale — disponible
v1, created = Vehicle.objects.get_or_create(
    title="Toyota Corolla 2020 — Location",
    defaults={
        "vehicle_type": "car",
        "listing_type": "rental",
        "brand": toyota,
        "model": corolla,
        "year": 2020,
        "mileage": 45000,
        "fuel": "petrol",
        "transmission": "automatic",
        "color": "Blanc",
        "condition": "used",
        "price": 8500000,
        "rental_price_per_day": 25000,
        "origin": "local",
        "city": "Lomé",
        "country": "Togo",
        "description": "Toyota Corolla en excellent état, boîte automatique, climatisation, idéale pour vos déplacements à Lomé et environs. Kilométrage maîtrisé, entretien régulier.",
        "status": "available",
        "is_featured": True,
    }
)
if created:
    print(f"  ✅ {v1.title}")

# 2. Toyota Land Cruiser en vente — international
v2, created = Vehicle.objects.get_or_create(
    title="Toyota Land Cruiser V8 2019 — Import France",
    defaults={
        "vehicle_type": "car",
        "listing_type": "sale",
        "brand": toyota,
        "model": land_cruiser,
        "year": 2019,
        "mileage": 78000,
        "fuel": "diesel",
        "transmission": "automatic",
        "color": "Gris métallisé",
        "condition": "used",
        "price": 35000000,
        "origin": "international",
        "city": "Paris",
        "country": "France",
        "transport_included": False,
        "transport_estimate": 2500000,
        "description": "Land Cruiser V8 diesel en parfait état, full options : cuir, GPS, caméra de recul, toit ouvrant. Véhicule expertisé avant expédition. Frais de transport estimés : 2 500 000 FCFA (dédouanement non inclus).",
        "status": "available",
        "is_featured": True,
    }
)
if created:
    print(f"  ✅ {v2.title}")

# 3. Peugeot 308 en vente — locale
v3, created = Vehicle.objects.get_or_create(
    title="Peugeot 308 2018 — Occasion",
    defaults={
        "vehicle_type": "car",
        "listing_type": "sale",
        "brand": peugeot,
        "model": peugeot_308,
        "year": 2018,
        "mileage": 92000,
        "fuel": "petrol",
        "transmission": "manual",
        "color": "Rouge",
        "condition": "used",
        "price": 7500000,
        "origin": "local",
        "city": "Lomé",
        "country": "Togo",
        "description": "Peugeot 308 essence, boîte manuelle, très bonne condition générale. Carrosserie sans accroc, moteur révisé. Idéale pour usage quotidien en ville.",
        "status": "available",
        "is_featured": False,
    }
)
if created:
    print(f"  ✅ {v3.title}")

# 4. Mercedes Classe C en location — locale
v4, created = Vehicle.objects.get_or_create(
    title="Mercedes Classe C 2021 — Location Premium",
    defaults={
        "vehicle_type": "car",
        "listing_type": "rental",
        "brand": mercedes,
        "model": classe_c,
        "year": 2021,
        "mileage": 30000,
        "fuel": "diesel",
        "transmission": "automatic",
        "color": "Noir",
        "condition": "used",
        "price": 22000000,
        "rental_price_per_day": 75000,
        "origin": "local",
        "city": "Lomé",
        "country": "Togo",
        "description": "Mercedes Classe C diesel, finition Avantgarde. Parfaite pour vos événements professionnels ou personnels. Chauffeur disponible sur demande (supplément).",
        "status": "available",
        "is_featured": True,
    }
)
if created:
    print(f"  ✅ {v4.title}")

# 5. Honda Civic import Allemagne
v5, created = Vehicle.objects.get_or_create(
    title="Honda Civic 2022 — Import Allemagne",
    defaults={
        "vehicle_type": "car",
        "listing_type": "sale",
        "brand": honda,
        "model": civic,
        "year": 2022,
        "mileage": 25000,
        "fuel": "petrol",
        "transmission": "automatic",
        "color": "Bleu nuit",
        "condition": "used",
        "price": 18000000,
        "origin": "international",
        "city": "Frankfurt",
        "country": "Allemagne",
        "transport_included": False,
        "transport_estimate": 2200000,
        "description": "Honda Civic récente, très faible kilométrage. Full options : écran tactile, caméra 360°, régulateur de vitesse adaptatif. Véhicule en transit possible.",
        "status": "available",
        "is_featured": False,
    }
)
if created:
    print(f"  ✅ {v5.title}")

# 6. Moto Yamaha en location
v6, created = Vehicle.objects.get_or_create(
    title="Yamaha YBR 125 — Location Moto",
    defaults={
        "vehicle_type": "moto",
        "listing_type": "rental",
        "brand": yamaha,
        "model": ybr,
        "year": 2021,
        "mileage": 12000,
        "fuel": "petrol",
        "transmission": "manual",
        "color": "Rouge/Noir",
        "condition": "used",
        "price": 1200000,
        "rental_price_per_day": 8000,
        "origin": "local",
        "city": "Lomé",
        "country": "Togo",
        "description": "Yamaha YBR 125, économique et fiable. Idéale pour se déplacer rapidement en ville. Casque fourni à la location.",
        "status": "available",
        "is_featured": False,
    }
)
if created:
    print(f"  ✅ {v6.title}")

# ─── Pièces détachées ─────────────────────────────────────────────────────────
print("\n🔧 Pièces détachées...")

parts_data = [
    {
        "title": "Filtre à huile Toyota",
        "reference": "TOY-FH-001",
        "condition": "new",
        "price": 8500,
        "stock_quantity": 25,
        "is_local": True,
        "description": "Filtre à huile d'origine Toyota, compatible Corolla, Yaris, Avensis. Changement recommandé tous les 10 000 km.",
        "is_featured": True,
        "brands": [toyota],
        "models": [corolla],
    },
    {
        "title": "Huile moteur 5W30 — 5 litres",
        "reference": "HM-5W30-5L",
        "condition": "new",
        "price": 22000,
        "stock_quantity": 40,
        "is_local": True,
        "description": "Huile moteur synthétique 5W30, 5 litres. Compatible avec la majorité des véhicules essence et diesel. Norme ACEA C3.",
        "is_featured": True,
        "brands": [toyota, peugeot, honda],
        "models": [],
    },
    {
        "title": "Plaquettes de frein avant Peugeot 308",
        "reference": "PEU-PF-308",
        "condition": "new",
        "price": 35000,
        "stock_quantity": 8,
        "is_local": True,
        "description": "Plaquettes de frein avant pour Peugeot 308 (2013-2021). Montage simple, haute performance de freinage.",
        "is_featured": False,
        "brands": [peugeot],
        "models": [peugeot_308],
    },
    {
        "title": "Batterie 12V 60Ah",
        "reference": "BAT-12V-60",
        "condition": "new",
        "price": 75000,
        "stock_quantity": 10,
        "is_local": True,
        "description": "Batterie 12V 60Ah, compatible avec la majorité des berlines et SUV. Garantie 1 an. Livraison et pose possible.",
        "is_featured": False,
        "brands": [toyota, peugeot, honda, mercedes],
        "models": [],
    },
    {
        "title": "Kit distribution Honda Civic",
        "reference": "HON-KD-CIV",
        "condition": "new",
        "price": 120000,
        "stock_quantity": 3,
        "is_local": True,
        "description": "Kit distribution complet pour Honda Civic 1.6i (2012-2022). Comprend courroie, galets, et pompe à eau. Remplacement conseillé tous les 120 000 km.",
        "is_featured": False,
        "brands": [honda],
        "models": [civic],
    },
]

for data in parts_data:
    brands = data.pop("brands")
    models = data.pop("models")
    part, created = SparePart.objects.get_or_create(
        reference=data["reference"],
        defaults=data
    )
    if created:
        part.compatible_brands.set(brands)
        part.compatible_models.set(models)
        print(f"  ✅ {part.title}")

# ─── Utilisateurs de test ─────────────────────────────────────────────────────
print("\n👤 Utilisateurs de test...")

# Utilisateur 1 : KYC validé — peut louer
user1, created = User.objects.get_or_create(
    email="koffi.mensah@test.com",
    defaults={
        "username": "koffi.mensah@test.com",
        "first_name": "Koffi",
        "last_name": "Mensah",
        "phone": "+22890123456",
        "city": "Lomé",
        "country": "Togo",
        "is_kyc_verified": True,
    }
)
if created:
    user1.set_password("TestPassword123!")
    user1.save()
    print(f"  ✅ {user1.get_full_name()} — KYC validé — mot de passe: TestPassword123!")
else:
    print(f"  ℹ️  {user1.get_full_name()} existe déjà")

# Utilisateur 2 : Sans KYC — ne peut pas louer
user2, created = User.objects.get_or_create(
    email="ama.kluivert@test.com",
    defaults={
        "username": "ama.kluivert@test.com",
        "first_name": "Ama",
        "last_name": "Kluivert",
        "phone": "+22891234567",
        "city": "Kara",
        "country": "Togo",
        "is_kyc_verified": False,
    }
)
if created:
    user2.set_password("TestPassword123!")
    user2.save()
    print(f"  ✅ {user2.get_full_name()} — Sans KYC — mot de passe: TestPassword123!")
else:
    print(f"  ℹ️  {user2.get_full_name()} existe déjà")

# ─── Résumé ───────────────────────────────────────────────────────────────────
print("\n" + "═" * 55)
print("✅ DONNÉES DE TEST CRÉÉES AVEC SUCCÈS !")
print("═" * 55)
print(f"  Marques         : {Brand.objects.count()}")
print(f"  Modèles         : {VehicleModel.objects.count()}")
print(f"  Véhicules       : {Vehicle.objects.count()}")
print(f"  Pièces          : {SparePart.objects.count()}")
print(f"  Utilisateurs    : {User.objects.filter(is_superuser=False).count()}")
print("═" * 55)
print("\n📌 Comptes de test :")
print("  Email    : koffi.mensah@test.com")
print("  Password : TestPassword123!")
print("  KYC      : ✅ Validé (peut louer)\n")
print("  Email    : ama.kluivert@test.com")
print("  Password : TestPassword123!")
print("  KYC      : ❌ Non soumis\n")
print("📌 Accès admin Django :")
print("  URL      : http://127.0.0.1:8000/admin/")
print("  Compte   : celui créé avec createsuperuser")
print("═" * 55)
