# logistics/urls.py

from django.urls import path
from .views import (
    TransportZoneListView,
    TransportEstimateView,
    TransportRequestCreateView,
    TransportRequestDetailView,
    TransportRequestTrackView,
    TransportRequestPDFView,
)

urlpatterns = [
    # Zones tarifaires
    path('zones/', TransportZoneListView.as_view(), name='transport_zones'),

    # Simulateur de coût (sans créer de demande)
    path('estimate/', TransportEstimateView.as_view(), name='transport_estimate'),

    # Demandes de transport
    path('requests/', TransportRequestCreateView.as_view(), name='transport_create'),
    path('requests/<int:pk>/', TransportRequestDetailView.as_view(), name='transport_detail'),

    # Suivi public par ID
    path('track/<int:pk>/', TransportRequestTrackView.as_view(), name='transport_track'),

    # Fiche PDF récapitulative
    path('requests/<int:pk>/pdf/', TransportRequestPDFView.as_view(), name='transport_pdf'),
]