"""
URL routing for collections app.
"""

from django.urls import path
from . import views

app_name = 'collections'

urlpatterns = [
    # My Collection
    path('my/', views.MyCollectionView.as_view(), name='my-collection'),
    path('', views.CollectionCreateView.as_view(), name='collection-create'),
    path('<uuid:pk>/', views.CollectionDetailView.as_view(), name='collection-detail'),

    # Statistics & Timeline
    path('stats/', views.CollectionStatsView.as_view(), name='collection-stats'),
    path('timeline/', views.CollectionTimelineView.as_view(), name='collection-timeline'),
]
