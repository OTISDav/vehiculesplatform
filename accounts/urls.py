from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileView, KYCSubmitView, KYCStatusView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('kyc/submit/', KYCSubmitView.as_view(), name='kyc_submit'),
    path('kyc/status/', KYCStatusView.as_view(), name='kyc_status'),
]