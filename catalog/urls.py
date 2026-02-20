from django.urls import path
from .views import (
    BrandListView,
    VehicleListView, VehicleDetailView,
    SparePartListView, SparePartDetailView
)

urlpatterns = [
    path('brands/', BrandListView.as_view(), name='brands'),
    path('vehicles/', VehicleListView.as_view(), name='vehicles'),
    path('vehicles/<int:pk>/', VehicleDetailView.as_view(), name='vehicle_detail'),
    path('parts/', SparePartListView.as_view(), name='parts'),
    path('parts/<int:pk>/', SparePartDetailView.as_view(), name='part_detail'),
]