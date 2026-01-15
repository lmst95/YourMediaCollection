"""
URL configuration for yourmedia project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API endpoints
    path('api/auth/', include('apps.accounts.urls')),
    path('api/media/', include('apps.media_catalog.urls')),
    path('api/collections/', include('apps.collections.urls')),
    path('api/sync/', include('apps.data_sync.urls')),
    # Phase 2:
    # path('api/social/', include('apps.social.urls')),
    # path('api/recommendations/', include('apps.recommendations.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
