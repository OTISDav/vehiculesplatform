# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Personnalisation du titre du back-office admin
admin.site.site_header = "🚗 Plateforme Véhicules — Administration"
admin.site.site_title = "Admin Véhicules"
admin.site.index_title = "Tableau de bord"

urlpatterns = [
    # Back-office admin Django
    path('admin/', admin.site.urls),

    path('api/accounts/', include('accounts.urls')),
    path('api/catalog/', include('catalog.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/logistics/', include('logistics.urls')),
]

# Servir les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)