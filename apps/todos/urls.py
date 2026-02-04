from django.urls import path
from . import views

app_name = 'todos'

urlpatterns = [
    path('', views.TodoListView.as_view(), name='list'),
    path('create/', views.TodoCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TodoDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TodoUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.TodoDeleteView.as_view(), name='delete'),
    path('<int:pk>/toggle/', views.TodoToggleView.as_view(), name='toggle'),
]
