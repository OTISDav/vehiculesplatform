from django.urls import path
from .views import (
    RentalCreateView, RentalListView, RentalDetailView,
    SparePartOrderCreateView, SparePartOrderListView, SparePartOrderDetailView,
    ContactMessageCreateView
)

urlpatterns = [
    path('rentals/', RentalListView.as_view(), name='rental_list'),       # GET
    path('rentals/create/', RentalCreateView.as_view(), name='rental_create'),  # POST
    path('rentals/<int:pk>/', RentalDetailView.as_view(), name='rental_detail'),
    path('parts/', SparePartOrderListView.as_view(), name='part_order_list'),
    path('parts/create/', SparePartOrderCreateView.as_view(), name='part_order_create'),
    path('parts/<int:pk>/', SparePartOrderDetailView.as_view(), name='part_order_detail'),
    path('contact/', ContactMessageCreateView.as_view(), name='contact'),
]