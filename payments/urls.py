from django.urls import path
from .views import (
    PaymentHistoryView,
    PaymentDetailView,
    StripePaymentIntentView,
    StripeWebhookView,
    MobileMoneyPaymentView,
    MobileMoneyCallbackView,
    PaymentStatusView,
)

urlpatterns = [
    path('', PaymentHistoryView.as_view(), name='payment_history'),
    path('<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),

    path('stripe/init/', StripePaymentIntentView.as_view(), name='stripe_init'),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),

    path('mobile-money/', MobileMoneyPaymentView.as_view(), name='mobile_money'),
    path('mobile-money/callback/', MobileMoneyCallbackView.as_view(), name='mobile_money_callback'),

    path('<str:invoice_number>/status/', PaymentStatusView.as_view(), name='payment_status'),
]