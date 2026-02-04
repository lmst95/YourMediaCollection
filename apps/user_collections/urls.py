from django.urls import path
from . import views

app_name = 'collections'

urlpatterns = [
    path('', views.CollectionListView.as_view(), name='list'),
    path('create/', views.CollectionCreateView.as_view(), name='create'),
    path('<int:pk>/', views.CollectionDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.CollectionUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.CollectionDeleteView.as_view(), name='delete'),

    # Sharing management
    path('<int:pk>/share/', views.CollectionShareSettingsView.as_view(), name='share_settings'),
    path('shared-with-me/', views.UserSharedCollectionsView.as_view(), name='shared_with_me'),
    path('s/<str:token>/', views.SharedCollectionView.as_view(), name='shared_view'),

    # Collection item management
    path('<int:collection_pk>/add-item/<int:content_type_id>/<int:object_id>/',
         views.CollectionItemAddView.as_view(), name='add_item'),
    path('item/<int:pk>/edit/', views.CollectionItemUpdateView.as_view(), name='update_item'),
    path('item/<int:pk>/remove/', views.CollectionItemRemoveView.as_view(), name='remove_item'),
]
