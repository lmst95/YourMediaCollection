from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.BookListView.as_view(), name='list'),
    path('timeline/', views.BookTimelineView.as_view(), name='timeline'),
    path('search-import/', views.BookSearchImportView.as_view(), name='search_import'),
    path('import-from-dnb/', views.BookImportFromDNBView.as_view(), name='import_from_dnb'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='detail'),
    path('<int:pk>/rate/', views.BookRateView.as_view(), name='rate'),
    path('<int:pk>/toggle-read/', views.BookReadStatusToggleView.as_view(), name='toggle_read'),
]
