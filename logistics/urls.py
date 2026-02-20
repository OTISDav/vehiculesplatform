from django.urls import path
from .views import TransportRequestCreateView

urlpatterns = [
    path('transport/', TransportRequestCreateView.as_view(), name='transport_request'),
]