"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home

urlpatterns = [
    path('', home, name='home'),  # Temporary homepage
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Built-in auth URLs (login, logout, password reset, etc.)
    # path('accounts/', include('apps.accounts.urls')),
    path('books/', include('apps.books.urls')),
    path('documents/', include('apps.documents.urls')),
    path('collections/', include('apps.user_collections.urls')),
    # path('notes/', include('apps.notes.urls')),
    path('todos/', include('apps.todos.urls')),
    # path('timeline/', include('apps.timeline.urls')),
    # path('api/', include('api.urls')),
]

# Debug Toolbar (only in development)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
