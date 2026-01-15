"""
URL routing for accounts app (authentication endpoints).
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

app_name = 'accounts'

urlpatterns = [
    # JWT Authentication
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),

    # User Profile
    path('users/me/', views.CurrentUserView.as_view(), name='current_user'),
    path('users/password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user_detail'),
]
