"""
URL routing for media_catalog app.
"""

from django.urls import path
from . import views

app_name = 'media_catalog'

urlpatterns = [
    # General Media
    path('', views.MediaListView.as_view(), name='media-list'),
    path('<uuid:pk>/', views.MediaDetailView.as_view(), name='media-detail'),
    path('create/', views.MediaCreateView.as_view(), name='media-create'),
    path('genres/', views.GenreListView.as_view(), name='genre-list'),

    # Type-specific lists
    path('movies/', views.MovieListView.as_view(), name='movie-list'),
    path('tv-series/', views.TVSeriesListView.as_view(), name='tv-series-list'),
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('music/', views.MusicListView.as_view(), name='music-list'),
]
