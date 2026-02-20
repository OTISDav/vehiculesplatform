from accounts.models import User
from catalog.models import Brand, VehicleModel, Vehicle, SparePart
from logistics.models import TransportZone, Transporter, TransportRequest, TransportStep

print("=" * 60)
print("🌱  SEED DATA — Plateforme Véhicules & Pièces")
print("=" * 60)

# ─── 1. MARQUES & MODÈLES ────────────────────────────────────────────────────
print("\n📦 Marques & Modèles...")
toyota,   _ = Brand.objects.get_or_create(name="Toyota")
peugeot,  _ = Brand.objects.get_or_create(name="Peugeot")
honda,    _ = Brand.objects.get_or_create(name="Honda")
mercedes, _ = Brand.objects.get_or_create(name="Mercedes-Benz")
yamaha,   _ = Brand.objects.get_or_create(name="Yamaha")

corolla,      _ = VehicleModel.objects.get_or_create(brand=toyota,   name="Corolla")
land_cruiser, _ = VehicleModel.objects.get_or_create(brand=toyota,   name="Land Cruiser")
peugeot_308,  _ = VehicleModel.objects.get_or_create(brand=peugeot,  name="308")
civic,        _ = VehicleModel.objects.get_or_create(brand=honda,    name="Civic")
classe_c,     _ = VehicleModel.objects.get_or_create(brand=mercedes, name="Classe C")
ybr,          _ = VehicleModel.objects.get_or_create(brand=yamaha,   name="YBR 125")
print(f"  ✅ {Brand.objects.count()} marques, {VehicleModel.objects.count()} modèles")

# ─── 2. VÉHICULES ────────────────────────────────────────────────────────────
print("\n🚘 Véhicules...")
vehicles_data = [
    dict(title="Toyota Corolla 2020 — Location",
         vehicle_type="car", listing_type="rental", brand=toyota, model=corolla,
         year=2020, mileage=45000, fuel="petrol", transmission="automatic",
         color="Blanc", condition="used", price=8500000, rental_price_per_day=25000,
         origin="local", city="Lomé", country="Togo", status="available", is_featured=True,
         description="Toyota Corolla en excellent état, climatisation, entretien régulier."),
    dict(title="Toyota Land Cruiser V8 2019 — Import France",
         vehicle_type="car", listing_type="sale", brand=toyota, model=land_cruiser,
         year=2019, mileage=78000, fuel="diesel", transmission="automatic",
         color="Gris métallisé", condition="used", price=35000000,
         origin="international", city="Paris", country="France",
         transport_included=False, transport_estimate=2500000,
         status="available", is_featured=True,
         description="Land Cruiser V8 full options. Expertisé avant expédition. Dédouanement non inclus."),
    dict(title="Peugeot 308 2018 — Occasion",
         vehicle_type="car", listing_type="sale", brand=peugeot, model=peugeot_308,
         year=2018, mileage=92000, fuel="petrol", transmission="manual",
         color="Rouge", condition="used", price=7500000,
         origin="local", city="Lomé", country="Togo", status="available", is_featured=False,
         description="Peugeot 308 essence. Moteur révisé. Idéale usage quotidien."),
    dict(title="Mercedes Classe C 2021 — Location Premium",
         vehicle_type="car", listing_type="rental", brand=mercedes, model=classe_c,
         year=2021, mileage=30000, fuel="diesel", transmission="automatic",
         color="Noir", condition="used", price=22000000, rental_price_per_day=75000,
         origin="local", city="Lomé", country="Togo", status="available", is_featured=True,
         description="Mercedes Classe C Avantgarde diesel. Chauffeur disponible sur demande."),
    dict(title="Honda Civic 2022 — Import Allemagne",
         vehicle_type="car", listing_type="sale", brand=honda, model=civic,
         year=2022, mileage=25000, fuel="petrol", transmission="automatic",
         color="Bleu nuit", condition="used", price=18000000,
         origin="international", city="Frankfurt", country="Allemagne",
         transport_included=False, transport_estimate=2200000,
         status="available", is_featured=False,
         description="Honda Civic récente, full options : écran tactile, caméra 360°."),
    dict(title="Yamaha YBR 125 — Location Moto",
         vehicle_type="moto", listing_type="rental", brand=yamaha, model=ybr,
         year=2021, mileage=12000, fuel="petrol", transmission="manual",
         color="Rouge/Noir", condition="used", price=1200000, rental_price_per_day=8000,
         origin="local", city="Lomé", country="Togo", status="available", is_featured=False,
         description="Yamaha YBR 125 économique. Casque fourni."),
]
created_vehicles = []
for d in vehicles_data:
    v, c = Vehicle.objects.get_or_create(title=d['title'], defaults=d)
    created_vehicles.append(v)
    print(f"  {'✅' if c else 'ℹ️ '} [ID:{v.pk}] {v.title}")

# ─── 3. PIÈCES DÉTACHÉES ─────────────────────────────────────────────────────
print("\n🔧 Pièces détachées...")
parts_data = [
    dict(title="Filtre à huile Toyota", reference="TOY-FH-001", condition="new",
         price=8500, stock_quantity=25, is_local=True, is_featured=True,
         description="Filtre à huile Toyota. Compatible Corolla, Yaris. Remplacement tous les 10 000 km.",
         brands=[toyota], models=[corolla]),
    dict(title="Huile moteur 5W30 — 5 litres", reference="HM-5W30-5L", condition="new",
         price=22000, stock_quantity=40, is_local=True, is_featured=True,
         description="Huile moteur synthétique 5W30, 5L. Compatible essence et diesel. Norme ACEA C3.",
         brands=[toyota, peugeot, honda], models=[]),
    dict(title="Plaquettes de frein avant Peugeot 308", reference="PEU-PF-308", condition="new",
         price=35000, stock_quantity=8, is_local=True, is_featured=False,
         description="Plaquettes de frein avant pour Peugeot 308 (2013-2021).",
         brands=[peugeot], models=[peugeot_308]),
    dict(title="Batterie 12V 60Ah", reference="BAT-12V-60", condition="new",
         price=75000, stock_quantity=10, is_local=True, is_featured=False,
         description="Batterie universelle 12V 60Ah. Garantie 1 an.",
         brands=[toyota, peugeot, honda, mercedes], models=[]),
    dict(title="Kit distribution Honda Civic", reference="HON-KD-CIV", condition="new",
         price=120000, stock_quantity=3, is_local=True, is_featured=False,
         description="Kit distribution complet Honda Civic 1.6i (2012-2022).",
         brands=[honda], models=[civic]),
]
created_parts = []
for d in parts_data:
    brands = d.pop("brands"); models = d.pop("models")
    part, c = SparePart.objects.get_or_create(reference=d["reference"], defaults=d)
    if c:
        part.compatible_brands.set(brands)
        part.compatible_models.set(models)
    created_parts.append(part)
    print(f"  {'✅' if c else 'ℹ️ '} [ID:{part.pk}] {part.title}")

# ─── 4. UTILISATEURS ─────────────────────────────────────────────────────────
print("\n👤 Utilisateurs de test...")
user1, c = User.objects.get_or_create(
    email="koffi.mensah@test.com",
    defaults=dict(username="koffi.mensah@test.com", first_name="Koffi", last_name="Mensah",
                  phone="+22890123456", city="Lomé", country="Togo", is_kyc_verified=True))
if c: user1.set_password("TestPassword123!"); user1.save()
print(f"  {'✅' if c else 'ℹ️ '} {user1.get_full_name()} — KYC ✅ — TestPassword123!")

user2, c = User.objects.get_or_create(
    email="ama.kluivert@test.com",
    defaults=dict(username="ama.kluivert@test.com", first_name="Ama", last_name="Kluivert",
                  phone="+22891234567", city="Kara", country="Togo", is_kyc_verified=False))
if c: user2.set_password("TestPassword123!"); user2.save()
print(f"  {'✅' if c else 'ℹ️ '} {user2.get_full_name()} — KYC ❌ — TestPassword123!")

# ─── 5. ZONES TARIFAIRES ─────────────────────────────────────────────────────
print("\n🌍 Zones tarifaires...")
zones_data = [
    dict(name="Europe Occidentale",
         countries="France\nAllemagne\nBelgique\nPays-Bas\nLuxembourg\nSuisse\nAutriche\nItalie\nEspagne\nPortugal",
         base_price=2500000, price_per_kg=500, delay_days_min=25, delay_days_max=35,
         notes="Port d'embarquement : Marseille ou Le Havre."),
    dict(name="Europe du Nord",
         countries="Suède\nNorvège\nDanemark\nFinlande",
         base_price=2800000, price_per_kg=550, delay_days_min=30, delay_days_max=40,
         notes="Port : Rotterdam ou Hambourg."),
    dict(name="Europe de l'Est",
         countries="Pologne\nRépublique Tchèque\nHongrie\nRoumanie\nBulgarie\nUkraine",
         base_price=3000000, price_per_kg=600, delay_days_min=35, delay_days_max=45,
         notes="Transit via Hambourg ou Gdansk."),
    dict(name="Royaume-Uni",
         countries="Royaume-Uni\nAngleterre\nÉcosse\nGalles\nIrlande du Nord",
         base_price=2700000, price_per_kg=520, delay_days_min=28, delay_days_max=38,
         notes="Embarquement : Southampton ou Tilbury."),
    dict(name="Amérique du Nord",
         countries="États-Unis\nCanada",
         base_price=4500000, price_per_kg=800, delay_days_min=40, delay_days_max=55,
         notes="Ports : New York, Baltimore ou Houston."),
    dict(name="Asie de l'Est",
         countries="Chine\nJapon\nCorée du Sud\nTaïwan",
         base_price=4000000, price_per_kg=750, delay_days_min=35, delay_days_max=50,
         notes="Ports : Shanghai, Tokyo, Busan."),
    dict(name="Moyen-Orient",
         countries="Émirats Arabes Unis\nArabie Saoudite\nQatar\nKoweït\nBahreïn\nOman",
         base_price=3500000, price_per_kg=650, delay_days_min=20, delay_days_max=30,
         notes="Port de Dubaï (Jebel Ali)."),
]
created_zones = {}
for d in zones_data:
    z, c = TransportZone.objects.get_or_create(name=d['name'], defaults=d)
    created_zones[d['name']] = z
    print(f"  {'✅' if c else 'ℹ️ '} {z.name} — {z.base_price:,.0f} FCFA ({z.delay_days_min}–{z.delay_days_max}j)")

# ─── 6. TRANSPORTEURS ────────────────────────────────────────────────────────
print("\n🚢 Transporteurs partenaires...")
transporters_data = [
    dict(name="AfriLOG Shipping", contact_name="Jean-Marc Dupont",
         phone="+33612345678", email="contact@afrilog.fr",
         notes="Partenaire principal Europe Occidentale.",
         zone_names=["Europe Occidentale", "Europe du Nord", "Royaume-Uni"]),
    dict(name="TransGlobal Lomé", contact_name="Kofi Agbeko",
         phone="+22890111222", email="kofi@transglobal.tg",
         notes="Basé à Lomé, gère l'arrivée au port.",
         zone_names=["Europe Occidentale", "Europe de l'Est", "Moyen-Orient"]),
    dict(name="OceanRoute USA", contact_name="Mike Johnson",
         phone="+13015551234", email="mike@oceanroute.us",
         notes="Spécialisé Amérique du Nord → Afrique.",
         zone_names=["Amérique du Nord"]),
    dict(name="AsiaCargo Express", contact_name="Li Wei",
         phone="+8613812345678", email="liwei@asiacargo.cn",
         notes="Spécialisé Asie → Afrique.",
         zone_names=["Asie de l'Est"]),
]
created_transporters = {}
for d in transporters_data:
    znames = d.pop('zone_names')
    t, c = Transporter.objects.get_or_create(name=d['name'], defaults=d)
    if c: t.zones.set([created_zones[z] for z in znames if z in created_zones])
    created_transporters[d['name']] = t
    print(f"  {'✅' if c else 'ℹ️ '} {t.name}")

# ─── 7. DEMANDES DE TRANSPORT (démo) ─────────────────────────────────────────
print("\n📋 Demandes de transport (démo)...")
v_france  = created_vehicles[1]  # Land Cruiser — France
v_germany = created_vehicles[4]  # Civic — Allemagne
z_europe  = created_zones["Europe Occidentale"]
t_afrilog = created_transporters["AfriLOG Shipping"]

# Demande 1 : en transit, 5 étapes
req1, c = TransportRequest.objects.get_or_create(
    vehicle=v_france, client_email="kofi@test.com",
    defaults=dict(
        client_name="Kofi Atta", client_phone="+22890777888",
        destination_city="Lomé", origin_country="France", origin_city="Paris",
        zone=z_europe, vehicle_weight_kg=1800,
        estimated_cost=3400000, final_cost=3400000,
        advance_required=1020000, advance_paid=1020000,
        transporter=t_afrilog, status="in_transit",
        client_note="Votre véhicule est en mer. Arrivée prévue dans 12 jours.",
    ))
if c:
    for sv, ti, de, lo in [
        ("quote_requested","Demande reçue",         "Demande pour Land Cruiser depuis Paris.",       ""),
        ("quote_sent",     "Devis envoyé",           "Devis de 3 400 000 FCFA transmis par email.",  "Lomé"),
        ("advance_paid",   "Avance payée",           "Avance de 1 020 000 FCFA reçue via Stripe.",   "Lomé"),
        ("loading",        "Chargement en cours",    "Véhicule pris en charge à Paris.",             "Paris, France"),
        ("in_transit",     "En transit vers Lomé",   "Départ du Havre. ETA : 12 jours.",             "Le Havre, France"),
    ]:
        TransportStep.objects.create(request=req1, status=sv, title=ti, description=de, location=lo)
print(f"  {'✅' if c else 'ℹ️ '} [ID:{req1.pk}] {v_france.title} — EN TRANSIT (5 étapes)")

# Demande 2 : devis envoyé, 2 étapes
req2, c = TransportRequest.objects.get_or_create(
    vehicle=v_germany, client_email="ama@test.com",
    defaults=dict(
        client_name="Ama Kluivert", client_phone="+22891234567",
        destination_city="Lomé", origin_country="Allemagne", origin_city="Frankfurt",
        zone=z_europe, vehicle_weight_kg=1400,
        estimated_cost=3200000, advance_required=960000, advance_paid=0,
        status="quote_sent",
        client_note="Devis de 3 200 000 FCFA. Avance de 960 000 FCFA requise pour démarrer.",
    ))
if c:
    for sv, ti, de in [
        ("quote_requested","Demande reçue","Demande pour Honda Civic depuis Frankfurt."),
        ("quote_sent",     "Devis envoyé", "Devis envoyé. En attente de paiement de l'avance."),
    ]:
        TransportStep.objects.create(request=req2, status=sv, title=ti, description=de)
print(f"  {'✅' if c else 'ℹ️ '} [ID:{req2.pk}] {v_germany.title} — DEVIS ENVOYÉ (2 étapes)")

# ─── RÉSUMÉ ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("✅  SEED DATA TERMINÉ !")
print("=" * 60)
print(f"  Marques            : {Brand.objects.count()}")
print(f"  Modèles            : {VehicleModel.objects.count()}")
print(f"  Véhicules          : {Vehicle.objects.count()}")
print(f"  Pièces détachées   : {SparePart.objects.count()}")
print(f"  Utilisateurs       : {User.objects.filter(is_superuser=False).count()}")
print(f"  Zones tarifaires   : {TransportZone.objects.count()}")
print(f"  Transporteurs      : {Transporter.objects.count()}")
print(f"  Demandes transport : {TransportRequest.objects.count()}")
print("=" * 60)
print("\n📌 Comptes de test :")
print("  koffi.mensah@test.com  / TestPassword123!  → KYC ✅")
print("  ama.kluivert@test.com  / TestPassword123!  → KYC ❌")
print("\n📌 IDs à noter pour Postman :")
print(f"  vehicle_id      = {created_vehicles[0].pk}  (Corolla — location locale)")
print(f"  vehicle_intl_id = {created_vehicles[1].pk}  (Land Cruiser — France)")
print(f"  part_id         = {created_parts[0].pk}  (Filtre à huile)")
print(f"  transport_id    = {req1.pk}  (en transit, 5 étapes)")
print(f"  transport_id    = {req2.pk}  (devis envoyé, 2 étapes)")
print("\n📌 Admin : http://127.0.0.1:8000/admin/")
print("=" * 60)
